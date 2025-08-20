import pathlib
from datetime import datetime as dt
from typing import Optional
from urllib.parse import urljoin

import pytest
from sources.tomada_tempo import TomadaTempoSource
from src.event_processor import EventProcessor

pytestmark = [pytest.mark.integration]

FIXTURES_DIR = pathlib.Path(__file__).parents[1] / "fixtures" / "html" / "tomada_tempo"


def _read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def _make_target_friday(date_str: str = "01/08/2025", tz_name: str = "America/Sao_Paulo"):
    import pytz

    tz = pytz.timezone(tz_name)
    base = dt.strptime(date_str, "%d/%m/%Y")
    return tz.localize(base)


def _build_main_page(link_text: str, href: str) -> str:
    return f"""
    <html>
      <body>
        <a href=\"{href}\">{link_text}</a>
      </body>
    </html>
    """


class _DummyResponse:
    def __init__(self, text: str, url: str):
        self.text = text
        self.url = url


def _patch_make_request(monkeypatch, src: TomadaTempoSource, main_html: str, programming_html: str, programming_href: str):
    base_url = src.get_base_url()
    programming_url = urljoin(base_url, programming_href)

    def stub(self, url: str, method: str = "GET", **kwargs) -> Optional[_DummyResponse]:
        if url == base_url:
            return _DummyResponse(main_html, base_url)
        if url == programming_url:
            return _DummyResponse(programming_html, programming_url)
        return None

    monkeypatch.setattr(TomadaTempoSource, "make_request", stub, raising=True)


def test_entities_normalization(monkeypatch):
    programming_html = _read_fixture("programming_entities.html")
    src = TomadaTempoSource()

    link_text = "PROGRAMAÇÃO DA TV E INTERNET — 01/08/2025"
    href = "/programacao-01-08-2025"
    main_html = _build_main_page(link_text, href)

    _patch_make_request(monkeypatch, src, main_html, programming_html, href)
    target_date = _make_target_friday()

    events = src.collect_events(target_date)

    assert isinstance(events, list)
    assert len(events) >= 3
    # strings com acentos e entities não devem quebrar o parsing
    for e in events:
        assert e.get("date") in {"2025-08-01", "2025-08-02", "2025-08-03"}
        assert isinstance(e.get("streaming_links"), list)


def test_duplicates_deduplication(monkeypatch):
    programming_html = _read_fixture("programming_duplicates.html")
    src = TomadaTempoSource()

    link_text = "PROGRAMAÇÃO DA TV E INTERNET — 01/08/2025"
    href = "/programacao-01-08-2025"
    main_html = _build_main_page(link_text, href)

    _patch_make_request(monkeypatch, src, main_html, programming_html, href)
    target_date = _make_target_friday()

    # Coleta da fonte (pode conter duplicatas)
    raw_events = src.collect_events(target_date)

    # Deduplicação ocorre no pipeline de processamento
    processor = EventProcessor()
    processed = processor.process_events(raw_events, target_weekend=target_date)

    # Esperado: apenas um evento após dedupe no pipeline
    assert isinstance(processed, list)
    assert len(processed) == 1, f"Esperado 1 evento após dedupe, obtido {len(processed)}: {[e.get('display_name') for e in processed]}"
