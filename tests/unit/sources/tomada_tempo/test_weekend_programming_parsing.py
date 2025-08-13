import pytest
from bs4 import BeautifulSoup
from datetime import datetime, date

from sources.tomada_tempo import TomadaTempoSource


@pytest.fixture()
def source():
    return TomadaTempoSource()


@pytest.mark.unit
def test_parse_weekend_programming_structure_basic(source):
    html = (
        "<html><body>"
        "<h5>HORÁRIOS, PROGRAMAÇÃO E ONDE ASSISTIR</h5>"
        "<p>SÁBADO – 02/08/2025</p>"
        "<ul>"
        "  <li>08:30 – F1 – em Hungaroring – <a href=\"/live\">Assista</a></li>"
        "</ul>"
        "</body></html>"
    )
    soup = BeautifulSoup(html, "html.parser")
    events = source._parse_weekend_programming_structure(soup, datetime(2025, 8, 2), programming_context=None)

    assert isinstance(events, list)
    assert len(events) == 1
    ev = events[0]
    assert ev["from_weekend_programming"] is True
    assert ev["session_type"] in {"practice", "qualifying", "sprint", "race"}


@pytest.mark.unit
def test_parse_event_list_error_handling_returns_empty(source):
    # Passa ul_element None para cair no except e retornar lista vazia
    result = source._parse_event_list(None, date(2025, 8, 2))
    assert result == []


@pytest.mark.unit
def test_parse_event_from_li_returns_none_without_time_or_strong(source):
    soup = BeautifulSoup("<ul><li>Evento sem horário e sem <em>strong</em></li></ul>", "html.parser")
    li = soup.find("li")
    assert source._parse_event_from_li(li, li.get_text(strip=True), date(2025, 8, 2)) is None


@pytest.mark.unit
def test_parse_event_from_li_exception_branch(source):
    # li_element None -> AttributeError dentro do método -> retorna None
    assert source._parse_event_from_li(None, "qualquer", date(2025, 8, 2)) is None


@pytest.mark.unit
def test_parse_calendar_page_fallback_selector(source):
    # Sem header específico de programação; usa seletor .event
    html = (
        "<html><body>"
        "<div class=\"event\">SÁBADO – 02/08/2025 08:30 – F1 – em Interlagos</div>"
        "</body></html>"
    )
    events = source._parse_calendar_page(html, datetime(2025, 8, 2))
    assert isinstance(events, list)
    assert len(events) >= 1


@pytest.mark.unit
def test_extract_location_none(source):
    text = "Evento corporativo interno"
    assert source._extract_location(text) is None


@pytest.mark.unit
def test_extract_event_from_text_line_none_paths(source):
    # Sem data explícita e sem contexto + categoria => retorna None (sem exceção)
    assert source._extract_event_from_text_line("Cerimônia de abertura 10:00") is None
    # Chamada com None -> cobre ramo de exceção
    assert source._extract_event_from_text_line(None) is None
