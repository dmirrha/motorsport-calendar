import pytest
import types
from datetime import datetime, timedelta

import pytz

from sources.base_source import BaseSource


class TestSource(BaseSource):
    def get_display_name(self) -> str:
        return "Test Source"

    def get_base_url(self) -> str:
        return "https://example.com"

    def collect_events(self, target_date=None):
        return []


class DummyLogger:
    def __init__(self):
        self.debug_messages = []
        self.saved_payloads = []
        self.source_errors = []

    def debug(self, msg):
        self.debug_messages.append(str(msg))

    def save_payload(self, **kwargs):
        self.saved_payloads.append(kwargs)

    def log_source_error(self, source_display_name, error_msg):
        self.source_errors.append((source_display_name, error_msg))


class SessionSpy:
    """Session double com request() para inspecionar kwargs e retornar resposta fake."""
    def __init__(self, response, exception=None):
        self.response = response
        self.exception = exception
        self.calls = []
        self.headers = {}

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, **kwargs})
        if self.exception:
            raise self.exception
        return self.response

    def close(self):
        pass

    def mount(self, prefix, adapter):
        # Stub para compatibilidade com requests.Session.mount
        return None


class DummyResponse:
    def __init__(self, text="", status_code=200, raise_http_error=False, headers=None):
        self.text = text
        self.status_code = status_code
        self._raise_http_error = raise_http_error
        self.headers = headers or {"Content-Type": "text/html"}

    def raise_for_status(self):
        if self._raise_http_error or not (200 <= self.status_code < 400):
            import requests
            raise requests.HTTPError(f"HTTP {self.status_code}")


@pytest.fixture
def logger():
    return DummyLogger()


@pytest.fixture
def source(logger):
    return TestSource(config_manager=None, logger=logger, ui_manager=None)


def test_setup_session_headers_user_agent(monkeypatch):
    # Garante determinismo do User-Agent inicial
    ua = "UA-Test/1.0"
    monkeypatch.setattr("sources.base_source.random.choice", lambda seq: ua)

    s = TestSource()
    assert s.session.headers["User-Agent"] == ua
    # Checa cabeçalhos principais
    assert "Accept" in s.session.headers
    assert "Accept-Language" in s.session.headers
    assert "Connection" in s.session.headers


def test_parse_date_time_basic_br_and_iso(source):
    # BR
    dt_br = source.parse_date_time("10/08/2025", "21:30")
    assert dt_br is not None
    assert dt_br.tzinfo is not None
    assert dt_br.strftime("%Y-%m-%d %H:%M") == "2025-08-10 21:30"
    assert str(dt_br.tzinfo) in ("America/Sao_Paulo", "-03")  # compat

    # ISO
    dt_iso = source.parse_date_time("2025-08-10", "")
    assert dt_iso is not None
    assert dt_iso.tzinfo is not None


def test_parse_date_time_fallback_dateutil(source):
    dt = source.parse_date_time("10 Aug 2025 21:00")
    assert dt is not None
    assert dt.tzinfo is not None


def test_parse_date_time_invalid_returns_none_and_logs(logger):
    s = TestSource(logger=logger)
    dt = s.parse_date_time("data inválida", "hora inválida")
    assert dt is None
    # Deve logar debug
    assert any("Failed to parse datetime" in m for m in logger.debug_messages)


def test_normalize_event_data_cleanup_and_defaults(source):
    raw = {
        "name": "  Grande Prêmio  ",
        "category": "  F1  ",
        "date": "2025-08-10",
        "time": "21:00",
        "location": "   ",
        "country": "  BR  ",
    }
    normalized = source.normalize_event_data(raw)
    assert normalized["name"] == "Grande Prêmio"
    assert normalized["raw_category"] == "F1"
    # location só com espaços -> após strip fica string vazia (comportamento atual)
    assert normalized["location"] == ""
    # defaults e metadata
    assert normalized["session_type"] == "race"
    assert normalized["source"] == source.source_name
    assert normalized["source_display_name"] == source.source_display_name


def test_filter_weekend_events_string_datetime_and_target_window(source):
    tz = pytz.timezone("America/Sao_Paulo")
    fri = tz.localize(datetime(2025, 8, 8, 10, 0))   # sexta
    wed = tz.localize(datetime(2025, 8, 6, 10, 0))   # quarta

    events = [
        {"name": "E1", "date": fri},
        {"name": "E2", "date": "10/08/2025"},  # domingo
        {"name": "E3", "date": wed},
        {"name": "E4"},  # sem data
    ]

    # Sem janela alvo -> somente sex-sáb-dom
    out = source.filter_weekend_events(events)
    names = {e["name"] for e in out}
    assert names == {"E1", "E2"}

    # Com janela alvo inclusiva: considerar quarta a domingo
    start = tz.localize(datetime(2025, 8, 6, 0, 0))
    end = tz.localize(datetime(2025, 8, 10, 23, 59))
    out2 = source.filter_weekend_events(events, (start, end))
    names2 = {e["name"] for e in out2}
    assert names2 == {"E1", "E2", "E3"}


def test_filter_weekend_events_invalid_date_logs_and_skips(logger):
    s = TestSource(logger=logger)
    events = [{"name": "Bad", "date": "inválido"}]
    out = s.filter_weekend_events(events)
    assert out == []
    # parse_date_time faz o log de falha com debug
    assert any("Failed to parse datetime" in m for m in logger.debug_messages)


def test_get_streaming_links_no_config_returns_empty():
    s = TestSource(config_manager=None)
    assert s.get_streaming_links("F1", region="BR") == []


def test_get_streaming_links_with_config(monkeypatch):
    class Cfg:
        def get_data_sources_config(self):
            # Config mínimo para evitar efeitos colaterais
            return {
                "timeout_seconds": 5,
                "retry_attempts": 2,
                "rate_limit_delay": 0,
                "user_agents": ["UA-Cfg/1.0"],
            }

        def get_streaming_providers(self, region):
            return {"F1": ["F1TV", "Band"]} if region == "BR" else {}

    s = TestSource(config_manager=Cfg())
    assert s.get_streaming_links("F1", region="BR") == ["F1TV", "Band"]
    assert s.get_streaming_links("F2", region="BR") == []


def test_make_request_respects_timeout_and_rate_limit(monkeypatch):
    # Evita sleeps reais
    monkeypatch.setattr("sources.base_source.time.sleep", lambda *_a, **_k: None)

    # User-Agent determinístico
    monkeypatch.setattr("sources.base_source.random.choice", lambda seq: "UA-1")

    # Resposta OK
    resp = DummyResponse(text="<html>ok</html>")

    # Session spy para capturar kwargs (timeout)
    sess = SessionSpy(response=resp)

    # Patch da Session para retornar nosso spy
    monkeypatch.setattr("sources.base_source.requests.Session", lambda: sess)

    s = TestSource()

    # 1ª chamada: aplica timeout default
    r1 = s.make_request("https://example.com/foo")
    assert r1 is resp
    assert sess.calls[0]["timeout"] == s.timeout

    # 2ª chamada: aciona branch de rate-limit (sem sleep real)
    r2 = s.make_request("https://example.com/bar", timeout=3)
    assert r2 is resp
    # timeout customizado é respeitado
    assert sess.calls[1]["timeout"] == 3


def test_make_request_user_agent_rotation_on_10th(monkeypatch):
    # Evita sleeps
    monkeypatch.setattr("sources.base_source.time.sleep", lambda *_a, **_k: None)

    # Primeiro UA para _setup_session
    monkeypatch.setattr("sources.base_source.random.choice", lambda seq: "UA-setup")
    resp = DummyResponse(text="<html>ok</html>")

    sess = SessionSpy(response=resp)
    monkeypatch.setattr("sources.base_source.requests.Session", lambda: sess)

    s = TestSource()

    # Força 9 requisições feitas anteriormente
    s.stats["requests_made"] = 9

    # Agora, 10ª requisição deve rotacionar UA
    rotated = {"val": False}

    def choice_rot(seq):
        rotated["val"] = True
        return "UA-rot"

    monkeypatch.setattr("sources.base_source.random.choice", choice_rot)

    _ = s.make_request("https://example.com/rot")
    assert rotated["val"] is True
    assert s.session.headers["User-Agent"] == "UA-rot"


def test_validate_event_data_and_logging(logger):
    s = TestSource(logger=logger)
    ok = {"name": "Evento", "date": "2025-08-10"}
    bad = {"name": "", "date": "2025-08-10"}
    assert s.validate_event_data(ok) is True
    assert s.validate_event_data(bad) is False
    assert any("missing required field" in m for m in logger.debug_messages)


def test_get_statistics_and_cleanup(monkeypatch):
    # Session com close rastreável
    class CloseSpy(SessionSpy):
        def __init__(self):
            super().__init__(response=DummyResponse())
            self.closed = False
        def close(self):
            self.closed = True

    sess = CloseSpy()
    monkeypatch.setattr("sources.base_source.requests.Session", lambda: sess)

    s = TestSource()
    # simula algumas métricas
    s.stats["requests_made"] = 4
    s.stats["successful_requests"] = 3
    s.stats["failed_requests"] = 1
    s.stats["events_collected"] = 7
    s.stats["last_collection_time"] = datetime.now().isoformat()

    stats = s.get_statistics()
    assert stats["success_rate"] == pytest.approx(3/4)

    s.cleanup()
    assert sess.closed is True


def test_normalize_event_data_missing_fields_defaults_htmlish(source):
    raw = {
        # name ausente -> vira string vazia por get('name') or ''
        # category None -> vira string vazia e strip
        "category": None,
        # location ausente -> string vazia
        # country ausente -> string vazia
        # session_type ausente -> default 'race'
        # streaming_links ausente -> default []
        # official_url ausente -> default ''
        # incluir valores com aparência de HTML malformado nos campos livres
        "name": "<h1>Evento</h1>",
        "location": "<div>Autódromo</div>",
    }
    normalized = source.normalize_event_data(raw)
    # Mantém texto como está (não sanitiza HTML), mas aplica strip e defaults
    assert normalized["name"] == "<h1>Evento</h1>"
    assert normalized["raw_category"] == ""
    assert normalized["location"] == "<div>Autódromo</div>"
    assert normalized["session_type"] == "race"
    assert normalized["streaming_links"] == []
    assert normalized["official_url"] == ""


def test_validate_event_data_missing_date_logs(logger):
    s = TestSource(logger=logger)
    event = {"name": "Evento Sem Data"}  # falta 'date'
    ok = s.validate_event_data(event)
    assert ok is False
    assert any("missing required field 'date'" in m for m in logger.debug_messages)


def test_filter_weekend_events_none_input(source):
    # Entrada None deve retornar lista vazia (branch inicial)
    out = source.filter_weekend_events(None)
    assert out == []


def test_parse_date_time_additional_formats_and_timezone(source):
    # formato YYYY/MM/DD e time com segundos
    dt1 = source.parse_date_time("2025/08/10", "21:30:15")
    assert dt1 is not None and dt1.strftime("%Y-%m-%d %H:%M:%S") == "2025-08-10 21:30:15"
    # timezone custom
    dt2 = source.parse_date_time("10-08-2025", "21:00", timezone_str="UTC")
    assert dt2 is not None and str(dt2.tzinfo) in ("UTC", "UTC+00:00", "+00")


def test_get_statistics_recent_errors_slice(logger):
    s = TestSource(logger=logger)
    # preencher mais de 5 erros para exercitar slice dos últimos 5
    for i in range(7):
        s.stats["errors"].append({"timestamp": str(i), "url": f"u{i}", "attempt": i+1, "error": "x"})
    stats = s.get_statistics()
    assert stats["error_count"] == 7
    assert len(stats["recent_errors"]) == 5
    # últimos 5 devem terminar com timestamp '6'
    assert stats["recent_errors"][-1]["timestamp"] == "6"


def test_generate_event_id_stability_and_variation(source):
    base = {"name": "GP", "date": "2025-08-10", "time": "21:00", "location": "Interlagos"}
    id1 = source._generate_event_id(base)
    id2 = source._generate_event_id(base.copy())
    assert isinstance(id1, str) and len(id1) == 16
    assert id1 == id2  # determinístico para mesmos dados
    # alteração de campo deve alterar o ID
    base2 = {**base, "time": "22:00"}
    id3 = source._generate_event_id(base2)
    assert id3 != id1


def test_parse_date_time_iso_with_tz_no_localize(source):
    # ISO com timezone embutido: tzinfo já presente deve ser preservado
    dt = source.parse_date_time("2025-08-10T21:00:00-03:00")
    assert dt is not None
    # Garante que um offset de -3 horas foi mantido
    assert dt.utcoffset() is not None and dt.utcoffset().total_seconds() == -3 * 3600


def test_parse_date_time_invalid_time_is_ignored(source):
    # time_str inválido deve ser ignorado (mantém apenas a data)
    dt = source.parse_date_time("2025-08-10", "25:99")
    assert dt is not None
    assert dt.hour == 0 and dt.minute == 0


def test_filter_weekend_events_unsupported_date_type_is_skipped(source):
    # date com tipo não suportado (ex.: int) deve ser ignorado
    events = [{"name": "BadType", "date": 1691625600}]
    out = source.filter_weekend_events(events)
    assert out == []


def test_get_statistics_no_requests_success_rate_zero_and_empty_errors(source):
    # Sem requests feitos, success_rate deve ser 0.0 e recent_errors vazio
    stats = source.get_statistics()
    assert stats["requests_made"] == 0
    assert stats["success_rate"] == 0.0
    assert stats["recent_errors"] == []


def test_filter_weekend_events_exception_branch_logs(logger, monkeypatch):
    # Força parse_date_time a lançar erro para cobrir o except do filtro
    s = TestSource(logger=logger)
    monkeypatch.setattr(s, "parse_date_time", lambda *_a, **_k: (_ for _ in ()).throw(ValueError("boom")))
    out = s.filter_weekend_events([{"name": "X", "date": "2025-08-10"}])
    assert out == []
    assert any("Error filtering event date" in m for m in logger.debug_messages)


def test_normalize_event_data_cleanup_whitespace_fields(source):
    raw = {
        "name": "Event",
        "date": "2025-08-10",
        # official_url e timezone com espaços devem virar None no cleanup loop
        "official_url": "   ",
        "timezone": "   ",
    }
    norm = source.normalize_event_data(raw)
    assert norm["official_url"] is None
    assert norm["timezone"] is None


def test_context_manager_and_str_repr(monkeypatch):
    # Patch cleanup para confirmar chamada via __exit__
    called = {"v": False}
    def cleanup_stub(self):
        called["v"] = True
    monkeypatch.setattr(TestSource, "cleanup", cleanup_stub)

    with TestSource() as s:
        # __enter__ deve retornar self
        assert isinstance(s, TestSource)
        # __str__
        assert str(s) == "Test Source (test)"
        # __repr__ com URL
        assert repr(s) == "<TestSource(name='test', url='https://example.com')>"

    assert called["v"] is True
