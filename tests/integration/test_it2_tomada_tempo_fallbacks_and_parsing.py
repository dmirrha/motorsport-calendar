import pathlib
from datetime import datetime as dt
from typing import Optional
from urllib.parse import urljoin

import pytest
from sources.tomada_tempo import TomadaTempoSource

pytestmark = [pytest.mark.integration]


def _make_target_friday(date_str: str = "01/08/2025", tz_name: str = "America/Sao_Paulo"):
    import pytz

    tz = pytz.timezone(tz_name)
    base = dt.strptime(date_str, "%d/%m/%Y")
    return tz.localize(base)


class _DummyResponse:
    def __init__(self, text: str, url: str):
        self.text = text
        self.url = url


# 1) Fallback: _collect_from_calendar com seletores comuns e contexto via <title>

def test_fallback_calendar_with_common_selectors_and_title_context(monkeypatch):
    src = TomadaTempoSource()
    base_url = src.get_base_url()

    # Página principal sem link de "PROGRAMAÇÃO DA TV E INTERNET" para forçar fallback
    main_html = """
    <html>
      <head><title>PROGRAMAÇÃO – 01 a 03/08/2025</title></head>
      <body>
        <div class="calendar-event">
          <a href="https://globoplay.globo.com">Assista ao vivo</a>
          FÓRMULA 1 – Qualifying – Interlagos às 14h30
        </div>
      </body>
    </html>
    """

    def stub(self, url: str, method: str = "GET", **kwargs) -> Optional[_DummyResponse]:
        if url == base_url:
            return _DummyResponse(main_html, base_url)
        return None

    monkeypatch.setattr(TomadaTempoSource, "make_request", stub, raising=True)

    target_date = _make_target_friday()
    events = src.collect_events(target_date)

    assert isinstance(events, list)
    assert len(events) >= 1
    # Deve usar contexto do title para preencher data quando ausente no elemento
    # Não checamos o formato exato da data (pode ser DD/MM/YYYY ou YYYY-MM-DD), apenas se existe
    assert any(e.get("date") for e in events)
    assert any(e.get("session_type") == "qualifying" for e in events)


# 2) Último recurso: _parse_text_content em HTML sem estrutura

def test_last_resort_text_parsing(monkeypatch):
    src = TomadaTempoSource()
    base_url = src.get_base_url()

    # HTML sem header/ul/seletores, apenas texto
    txt_html = """
    <html>
      <head><title>PROGRAMAÇÃO – 01 a 03/08/2025</title></head>
      <body>
        FÓRMULA 1 – Treino Livre 1 – 01/08/2025 às 09h
        NASCAR CUP – Sprint – às 20:15
      </body>
    </html>
    """

    def stub(self, url: str, method: str = "GET", **kwargs) -> Optional[_DummyResponse]:
        if url == base_url:
            return _DummyResponse(txt_html, base_url)
        return None

    monkeypatch.setattr(TomadaTempoSource, "make_request", stub, raising=True)

    target_date = _make_target_friday()
    events = src.collect_events(target_date)

    assert isinstance(events, list)
    assert len(events) >= 1
    # Deve conseguir extrair pelo menos uma linha por parsing de texto
    assert any(e.get("session_type") in {"practice", "sprint", "race", "qualifying"} for e in events)


# 3) Contexto via URL quando title não possui intervalo

def test_programming_context_from_url_when_title_missing_range(monkeypatch):
    src = TomadaTempoSource()
    base_url = src.get_base_url()
    # URL contendo data, para extrair start_date e weekend_dates
    calendar_url = urljoin(base_url, "/2025/08/01/post")

    html_without_range_in_title = """
    <html>
      <head><title>PROGRAMAÇÃO – Agosto</title></head>
      <body>
        <div class="post">F1 – Qualifying – Interlagos às 14:30</div>
      </body>
    </html>
    """

    call_count = {"n": 0}

    def stub(self, url: str, method: str = "GET", **kwargs) -> Optional[_DummyResponse]:
        # 1ª chamada (weekend programming): retorna main vazio
        # 2ª chamada (calendar fallback): retorna página com URL datada
        if url == base_url:
            call_count["n"] += 1
            if call_count["n"] == 1:
                return _DummyResponse("<html><body>Sem link</body></html>", base_url)
            return _DummyResponse(html_without_range_in_title, calendar_url)
        return None

    monkeypatch.setattr(TomadaTempoSource, "make_request", stub, raising=True)

    target_date = _make_target_friday()
    events = src.collect_events(target_date)

    assert isinstance(events, list)
    assert len(events) >= 1
    # Data deve ser inferida do contexto (URL -> start_date)
    assert any(e.get("date") for e in events)


# 4) Fallback final: _collect_from_categories quando base/calendar não retornam eventos

def test_categories_fallback(monkeypatch):
    src = TomadaTempoSource()
    base_url = src.get_base_url()
    f1_url = urljoin(base_url, "/f1")

    empty_main = "<html><body>Sem nada</body></html>"
    category_page = """
    <html>
      <head><title>PROGRAMAÇÃO – 01 a 03/08/2025</title></head>
      <body>
        <article>
          FÓRMULA 1 – Corrida – Interlagos às 15:00
          <a href="https://www.youtube.com/watch?v=test">YouTube</a>
        </article>
      </body>
    </html>
    """

    def stub(self, url: str, method: str = "GET", **kwargs) -> Optional[_DummyResponse]:
        # Busca por link principal e calendário retornam vazio
        if url == base_url:
            return _DummyResponse(empty_main, base_url)
        # Páginas de categoria: retornamos algo apenas para "/f1"
        if url == f1_url:
            return _DummyResponse(category_page, f1_url)
        # Outras categorias retornam vazio
        return _DummyResponse(empty_main, url)

    monkeypatch.setattr(TomadaTempoSource, "make_request", stub, raising=True)

    target_date = _make_target_friday()
    events = src.collect_events(target_date)

    assert isinstance(events, list)
    assert len(events) >= 1
    # Deve haver pelo menos um evento vindo de categorias
    assert any("FÓRMULA 1" in (e.get("raw_text", "")) or e.get("category") == "F1" for e in events)


# 5) Cobrir padrões de sessão e horários variados em li (estrutura de programação de fim de semana)

def test_session_types_and_time_patterns(monkeypatch):
    src = TomadaTempoSource()
    base_url = src.get_base_url()

    main_html = """
    <html><body>Sem link direto</body></html>
    """

    programming_html = """
    <html>
      <head><title>PROGRAMAÇÃO – 01 a 03/08/2025</title></head>
      <body>
        <h5>HORÁRIOS, PROGRAMAÇÃO E ONDE ASSISTIR</h5>
        <p>SEXTA-FEIRA – 01/08/2025</p>
        <ul>
          <li>14.30 – MotoGP – Classificação – Suzuka</li>
          <li>14h 05 – FÓRMULA 1 – Treino Livre 2 – Interlagos</li>
          <li>às 09 – NASCAR CUP – Sprint – Daytona</li>
          <li>10 horas e 45 – WEC – Corrida – Spa</li>
        </ul>
      </body>
    </html>
    """

    prog_url = urljoin(base_url, "/programacao-01-08-2025")

    call_count = {"n": 0}

    def stub(self, url: str, method: str = "GET", **kwargs) -> Optional[_DummyResponse]:
        if url == base_url:
            call_count["n"] += 1
            # 1ª chamada: página principal sem link (força fallback)
            if call_count["n"] == 1:
                return _DummyResponse(main_html, base_url)
            # 2ª chamada: calendário recebe a página de programação com URL específica
            return _DummyResponse(programming_html, prog_url)
        if url == prog_url:
            return _DummyResponse(programming_html, prog_url)
        return None

    monkeypatch.setattr(TomadaTempoSource, "make_request", stub, raising=True)

    target_date = _make_target_friday()
    events = src.collect_events(target_date)

    assert isinstance(events, list)
    assert len(events) >= 3

    times = {e.get("time") for e in events}
    # Verifica parsing de horários variados
    assert any(t in times for t in {"14:30", "14:05", "09:00", "10:45"})

    sessions = {e.get("session_type") for e in events}
    # Verifica mapeamento de sessões
    assert {"qualifying", "practice", "sprint", "race"}.intersection(sessions)
