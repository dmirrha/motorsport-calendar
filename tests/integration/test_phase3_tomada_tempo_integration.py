"""
Phase 3 — Iteração 1: Testes de integração determinísticos para TomadaTempoSource
- Foco: fluxo collect_events -> _collect_from_weekend_programming -> _parse_calendar_page
- Sem rede: monkeypatch em make_request para retornar HTML de fixtures
- Casos: estrutura mínima, headers alternativos, horários sem minutos/variações, overnight
Marcadores: integration
"""

from pathlib import Path
from datetime import datetime as dt
from typing import Optional
from urllib.parse import urljoin

import pytest

from sources.tomada_tempo import TomadaTempoSource


pytestmark = pytest.mark.integration

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "html"


def read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def make_target_friday(date_str: str = "01/08/2025", tz_name: str = "America/Sao_Paulo"):
    import pytz

    tz = pytz.timezone(tz_name)
    base = dt.strptime(date_str, "%d/%m/%Y")
    return tz.localize(base)


def build_main_page(link_text: str, href: str) -> str:
    return f"""
    <html>
      <body>
        <a href=\"{href}\">{link_text}</a>
      </body>
    </html>
    """


class DummyResponse:
    def __init__(self, text: str, url: str):
        self.text = text
        self.url = url


def _patch_make_request(monkeypatch, src: TomadaTempoSource, main_html: str, programming_html: str, programming_href: str):
    base_url = src.get_base_url()
    programming_url = urljoin(base_url, programming_href)

    def stub(self, url: str, method: str = "GET", **kwargs) -> Optional[DummyResponse]:
        if url == base_url:
            return DummyResponse(main_html, base_url)
        if url == programming_url:
            return DummyResponse(programming_html, programming_url)
        return None

    monkeypatch.setattr(TomadaTempoSource, "make_request", stub, raising=True)


def test_integration_weekend_minimal_structure(monkeypatch):
    # Arrange
    programming_html = read_fixture("tomada_tempo_weekend_minimal.html")
    src = TomadaTempoSource()

    link_text = "PROGRAMAÇÃO DA TV E INTERNET — 01/08/2025"
    href = "/programacao-01-08-2025"
    main_html = build_main_page(link_text, href)

    _patch_make_request(monkeypatch, src, main_html, programming_html, href)

    target_date = make_target_friday()

    # Act
    events = src.collect_events(target_date)

    # Assert
    assert isinstance(events, list)
    assert len(events) == 4  # 2 sexta, 1 sábado, 1 domingo

    # Normalização básica
    for e in events:
        assert e.get("source_display_name") == "Tomada de Tempo"
        assert e.get("date") is not None
        # campos normalizados
        assert "raw_data" in e and isinstance(e["raw_data"], dict)

    # Verificações pontuais
    e0 = events[0]
    assert e0.get("raw_category") in {"F1", "FÓRMULA 1", "Formula 1", "Fórmula 1"}
    assert isinstance(e0.get("streaming_links"), list)


def test_integration_weekend_alt_headers_and_dot_time(monkeypatch):
    # Arrange
    programming_html = read_fixture("tomada_tempo_weekend_alt_header.html")
    src = TomadaTempoSource()

    link_text = "PROGRAMAÇÃO DA TV E INTERNET — 01/08/2025"
    href = "/programacao-01-08-2025"
    main_html = build_main_page(link_text, href)

    _patch_make_request(monkeypatch, src, main_html, programming_html, href)

    target_date = make_target_friday()

    # Act
    events = src.collect_events(target_date)

    # Assert
    assert len(events) == 3
    # Campos essenciais
    for e in events:
        assert e.get("date") is not None
        assert e.get("time") is not None


def test_integration_weekend_no_minutes_and_variants(monkeypatch):
    # Arrange
    programming_html = read_fixture("tomada_tempo_weekend_no_minutes.html")
    src = TomadaTempoSource()

    link_text = "PROGRAMAÇÃO DA TV E INTERNET — 01/08/2025"
    href = "/programacao-01-08-2025"
    main_html = build_main_page(link_text, href)

    _patch_make_request(monkeypatch, src, main_html, programming_html, href)

    target_date = make_target_friday()

    # Act
    events = src.collect_events(target_date)

    # Assert
    assert len(events) >= 4  # parser pode filtrar entradas incompletas

    # Checagens de categorias/horários plausíveis em data correta
    dates = {e.get("date") for e in events}
    assert dates.issubset({"2025-08-02", "2025-08-03", "2025-08-01"})


def test_integration_weekend_overnight_cross_midnight(monkeypatch):
    # Arrange
    programming_html = read_fixture("tomada_tempo_weekend_overnight.html")
    src = TomadaTempoSource()

    link_text = "PROGRAMAÇÃO DA TV E INTERNET — 01/08/2025"
    href = "/programacao-01-08-2025"
    main_html = build_main_page(link_text, href)

    _patch_make_request(monkeypatch, src, main_html, programming_html, href)

    target_date = make_target_friday()

    # Act
    events = src.collect_events(target_date)

    # Assert: domingo contém eventos após meia-noite
    sunday = [e for e in events if e.get("date") == "2025-08-03"]
    assert len(sunday) >= 2
    times = {e.get("time") for e in sunday}
    assert {"00:10", "01:05"}.issubset(times)
