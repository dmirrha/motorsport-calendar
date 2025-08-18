import pathlib
from datetime import datetime as dt
from typing import Optional
from urllib.parse import urljoin

import pytest
from sources.tomada_tempo import TomadaTempoSource

pytestmark = [pytest.mark.integration]

FIXTURES_DIR = pathlib.Path(__file__).parents[1] / "fixtures" / "html" / "tomada_tempo"


def _read_fixture(name: str):
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


def test_tomada_tempo_happy_path(monkeypatch):
    # Arrange
    programming_html = _read_fixture("programming_happy.html")
    src = TomadaTempoSource()

    link_text = "PROGRAMAÇÃO DA TV E INTERNET — 01/08/2025"
    href = "/programacao-01-08-2025"
    main_html = _build_main_page(link_text, href)

    _patch_make_request(monkeypatch, src, main_html, programming_html, href)

    target_date = _make_target_friday()

    # Act
    events = src.collect_events(target_date)

    # Assert
    assert isinstance(events, list)
    assert len(events) == 2
    for e in events:
        assert e.get("date") is not None
        assert isinstance(e.get("streaming_links"), list)


def test_tomada_tempo_missing_fields(monkeypatch):
    # Arrange
    programming_html = _read_fixture("programming_missing_fields.html")
    src = TomadaTempoSource()

    link_text = "PROGRAMAÇÃO DA TV E INTERNET — 01/08/2025"
    href = "/programacao-01-08-2025"
    main_html = _build_main_page(link_text, href)

    _patch_make_request(monkeypatch, src, main_html, programming_html, href)

    target_date = _make_target_friday()

    # Act
    events = src.collect_events(target_date)

    # Assert
    assert isinstance(events, list)
    assert len(events) == 2
    # Campos essenciais
    for e in events:
        assert e.get("date") is not None
        assert isinstance(e.get("streaming_links"), list)
    # Pelo menos um evento sem links e um sem localidade
    assert any(e for e in events if e.get("streaming_links") == [])
    assert any(e for e in events if e.get("location") in (None, ""))

