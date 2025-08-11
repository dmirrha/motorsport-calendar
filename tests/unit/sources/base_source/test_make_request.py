import requests
import pytest
from datetime import datetime

from sources.base_source import BaseSource


class _LoggerStub:
    def __init__(self):
        self.saved_payloads = []
        self.errors = []
        self.debugs = []

    def debug(self, msg):
        self.debugs.append(msg)

    def save_payload(self, **kwargs):
        self.saved_payloads.append(kwargs)

    def log_source_error(self, source, message):
        self.errors.append((source, message))


class _DummySource(BaseSource):
    def get_display_name(self) -> str:
        return "Dummy"

    def get_base_url(self) -> str:
        return "https://example.com"

    def collect_events(self, target_date: datetime | None = None):  # not used here
        return []


@pytest.mark.unit
def test_make_request_success(patch_requests_session, dummy_response):
    logger = _LoggerStub()

    resp = dummy_response(text="ok", status_code=200)
    setattr(resp, "headers", {})

    # Patch antes de instanciar a fonte (BaseSource cria Session no __init__)
    sess = patch_requests_session(response_or_callable=lambda url, **kw: resp)
    # BaseSource.make_request usa self.session.request(method, url, **kwargs)
    setattr(sess, "request", lambda method, url, **kwargs: sess.get(url, **kwargs))
    # BaseSource._setup_session exige headers e mount
    if not hasattr(sess, "headers"):
        setattr(sess, "headers", {})
    if not hasattr(sess, "mount"):
        setattr(sess, "mount", lambda prefix, adapter: None)

    src = _DummySource(config_manager=None, logger=logger)

    r = src.make_request("https://example.com")

    assert r is resp
    assert src.stats["requests_made"] >= 1
    assert src.stats["successful_requests"] >= 1
    # save_payload chamado
    assert logger.saved_payloads, "payload não foi salvo via logger.save_payload"


@pytest.mark.unit
def test_make_request_timeout(patch_requests_session):
    logger = _LoggerStub()

    sess = patch_requests_session(exception_to_raise=requests.Timeout())
    setattr(sess, "request", lambda method, url, **kwargs: sess.get(url, **kwargs))
    if not hasattr(sess, "headers"):
        setattr(sess, "headers", {})
    if not hasattr(sess, "mount"):
        setattr(sess, "mount", lambda prefix, adapter: None)

    src = _DummySource(config_manager=None, logger=logger)

    r = src.make_request("https://example.com")

    assert r is None
    assert src.stats["failed_requests"] == 1
    # deve registrar erros por tentativa
    assert len(src.stats["errors"]) == src.retry_attempts
    assert logger.errors, "log_source_error não foi chamado no erro final"


@pytest.mark.unit
def test_make_request_http_error(patch_requests_session, dummy_response):
    logger = _LoggerStub()

    bad = dummy_response(text="", status_code=500)
    setattr(bad, "headers", {})

    sess = patch_requests_session(response_or_callable=lambda url, **kw: bad)
    setattr(sess, "request", lambda method, url, **kwargs: sess.get(url, **kwargs))
    if not hasattr(sess, "headers"):
        setattr(sess, "headers", {})
    if not hasattr(sess, "mount"):
        setattr(sess, "mount", lambda prefix, adapter: None)

    src = _DummySource(config_manager=None, logger=logger)

    r = src.make_request("https://example.com")

    assert r is None
    assert src.stats["failed_requests"] == 1
    assert len(src.stats["errors"]) == src.retry_attempts
    assert logger.errors, "log_source_error não foi chamado"


@pytest.mark.unit
def test_make_request_4xx_http_error(patch_requests_session, dummy_response):
    """Deve tentar novamente em 4xx e falhar no final com rastros e log de erro."""
    logger = _LoggerStub()

    bad = dummy_response(text="", status_code=404)
    setattr(bad, "headers", {})

    sess = patch_requests_session(response_or_callable=lambda url, **kw: bad)
    setattr(sess, "request", lambda method, url, **kwargs: sess.get(url, **kwargs))
    if not hasattr(sess, "headers"):
        setattr(sess, "headers", {})
    if not hasattr(sess, "mount"):
        setattr(sess, "mount", lambda prefix, adapter: None)

    src = _DummySource(config_manager=None, logger=logger)

    r = src.make_request("https://example.com/not-found")

    assert r is None
    assert src.stats["failed_requests"] == 1
    assert len(src.stats["errors"]) == src.retry_attempts
    assert logger.errors, "log_source_error não foi chamado no 4xx"


@pytest.mark.unit
def test_make_request_backoff_and_rate_limit_no_sleep(monkeypatch, patch_requests_session):
    """Valida chamadas de sleep: rate-limit no início e backoff exponencial por tentativa, sem esperar de fato."""
    logger = _LoggerStub()
    sleep_calls = []

    # Patch do sleep no módulo da fonte para não pausar de verdade
    monkeypatch.setattr("sources.base_source.time.sleep", lambda s: sleep_calls.append(s))

    # Session que sempre lança Timeout para acionar retries
    sess = patch_requests_session(exception_to_raise=requests.Timeout())
    setattr(sess, "request", lambda method, url, **kwargs: sess.get(url, **kwargs))
    if not hasattr(sess, "headers"):
        setattr(sess, "headers", {})
    if not hasattr(sess, "mount"):
        setattr(sess, "mount", lambda prefix, adapter: None)

    src = _DummySource(config_manager=None, logger=logger)
    # Configurações para facilitar assert dos tempos
    src.rate_limit_delay = 0.5
    src.retry_attempts = 3

    # Força o rate-limit inicial (stats será incrementado e ficará > 1)
    src.stats["requests_made"] = 1

    r = src.make_request("https://example.com/timeout")

    assert r is None
    assert src.stats["failed_requests"] == 1

    # Esperado: 1 chamada de rate-limit (0.5) + 2 chamadas de backoff: 0.5 (2**0 * 0.5), 1.0 (2**1 * 0.5)
    assert sleep_calls[:3] == [0.5, 0.5, 1.0]
    # Total de sleeps deve ser exatamente 3 neste cenário (sem sleep após última tentativa)
    assert len(sleep_calls) == 3


@pytest.mark.unit
def test_make_request_logger_none_safe(monkeypatch, patch_requests_session):
    """Quando logger é None, a função deve falhar de forma silenciosa e segura (retornando None)."""
    # Evita sleeps reais
    monkeypatch.setattr("sources.base_source.time.sleep", lambda s: None)

    sess = patch_requests_session(exception_to_raise=requests.ConnectionError())
    setattr(sess, "request", lambda method, url, **kwargs: sess.get(url, **kwargs))
    if not hasattr(sess, "headers"):
        setattr(sess, "headers", {})
    if not hasattr(sess, "mount"):
        setattr(sess, "mount", lambda prefix, adapter: None)

    src = _DummySource(config_manager=None, logger=None)

    r = src.make_request("https://example.com/error")

    assert r is None
    # Sem logger, ainda assim deve registrar estatísticas e não lançar exceções
    assert src.stats["failed_requests"] == 1
    assert len(src.stats["errors"]) == src.retry_attempts


@pytest.mark.unit
def test_make_request_logs_attempts_and_payload_details(patch_requests_session, dummy_response):
    """Confere logs de tentativas (debug) e conteúdo do payload salvo no sucesso."""
    logger = _LoggerStub()

    resp = dummy_response(text="<html>OK</html>", status_code=200)
    setattr(resp, "headers", {"X-Test": "1"})

    sess = patch_requests_session(response_or_callable=lambda url, **kw: resp)
    setattr(sess, "request", lambda method, url, **kwargs: sess.get(url, **kwargs))
    if not hasattr(sess, "headers"):
        setattr(sess, "headers", {})
    if not hasattr(sess, "mount"):
        setattr(sess, "mount", lambda prefix, adapter: None)

    src = _DummySource(config_manager=None, logger=logger)

    r = src.make_request("https://example.com/success")

    assert r is not None
    # Deve ter salvo payload com texto e headers incluídos
    assert logger.saved_payloads, "payload não foi salvo"
    saved = logger.saved_payloads[-1]
    assert saved.get("data") == "<html>OK</html>"
    assert saved.get("include_headers") is True
    assert saved.get("headers") == {"X-Test": "1"}


@pytest.mark.unit
def test_make_request_user_agent_rotation_on_10th_call(monkeypatch, patch_requests_session, dummy_response):
    """Na 10ª chamada, o header User-Agent deve ser atualizado (rotação)."""
    # Evita sleeps reais
    monkeypatch.setattr("sources.base_source.time.sleep", lambda s: None)

    # Resposta OK para todas as chamadas
    resp = dummy_response(text="ok", status_code=200)
    setattr(resp, "headers", {})

    sess = patch_requests_session(response_or_callable=lambda url, **kw: resp)
    setattr(sess, "request", lambda method, url, **kwargs: sess.get(url, **kwargs))
    if not hasattr(sess, "headers"):
        setattr(sess, "headers", {})
    if not hasattr(sess, "mount"):
        setattr(sess, "mount", lambda prefix, adapter: None)

    logger = _LoggerStub()
    src = _DummySource(config_manager=None, logger=logger)

    # Configura user_agents controlado e monkeypatch em random.choice para determinismo
    src.user_agents = ["UA-A", "UA-B", "UA-ROTATED"]
    monkeypatch.setattr("sources.base_source.random.choice", lambda lst: "UA-ROTATED")

    # Captura UA inicial definido no _setup_session (valor qualquer sob seed fixo)
    initial_ua = src.session.headers.get("User-Agent")

    # Executa 10 chamadas; na 10ª deve rotacionar UA
    for i in range(10):
        r = src.make_request("https://example.com/ua-rotate")
        assert r is not None

    rotated_ua = src.session.headers.get("User-Agent")
    assert rotated_ua == "UA-ROTATED"
    # Opcionalmente, garantir que houve alteração (se o inicial não for já "UA-ROTATED")
    if initial_ua is not None and initial_ua != "UA-ROTATED":
        assert rotated_ua != initial_ua

