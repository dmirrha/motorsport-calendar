import pytest
from bs4 import BeautifulSoup
from datetime import datetime
from unittest.mock import patch, Mock

from sources.tomada_tempo import TomadaTempoSource


@pytest.fixture()
def source():
    return TomadaTempoSource()


@pytest.mark.unit
def test_extract_event_name_gp_pattern(source):
    text = "GP do Brasil Qualifying"
    # Deve capturar o nome após o padrão GP ...
    name = source._extract_event_name(text)
    assert isinstance(name, str)
    assert "Brasil" in name


@pytest.mark.unit
def test_extract_location_em_pattern(source):
    text = "Corrida principal em Hungaroring às 15:00"
    loc = source._extract_location(text)
    assert loc == "Hungaroring"


@pytest.mark.unit
def test_extract_official_url_absolute_only(source):
    html = '<div><a href="https://example.com/evento">Evento Oficial</a></div>'
    soup = BeautifulSoup(html, 'html.parser')
    url = source._extract_official_url(soup.div)
    assert url == "https://example.com/evento"


@pytest.mark.unit
def test_extract_event_from_element_exception_returns_none(source):
    # Passar elemento None dispara AttributeError e cobre o branch de exceção
    result = source._extract_event_from_element(None, datetime(2025, 8, 1))
    assert result is None


@pytest.mark.unit
def test_collect_from_categories_with_mocks(source):
    # Mocka make_request para retornar um objeto com .text e _parse_calendar_page para retornar lista
    fake_response = Mock()
    fake_response.text = "<html><body>ok</body></html>"

    with patch.object(TomadaTempoSource, 'make_request', return_value=fake_response) as mk_req, \
         patch.object(TomadaTempoSource, '_parse_calendar_page', return_value=[{"name": "X"}]) as parse_page:
        events = source._collect_from_categories(datetime(2025, 8, 1))

    # Deve chamar make_request para várias páginas e agregar eventos
    assert isinstance(events, list)
    assert len(events) >= 1
    mk_req.assert_called()
    parse_page.assert_called()
