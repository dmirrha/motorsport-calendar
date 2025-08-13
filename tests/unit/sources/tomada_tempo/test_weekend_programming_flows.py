import pytest
from bs4 import BeautifulSoup
from datetime import datetime
from unittest.mock import patch, Mock

from sources.tomada_tempo import TomadaTempoSource


class DummyLogger:
    def __init__(self):
        self.messages = []
    def log_source_start(self, *a, **k):
        self.messages.append(("start", a, k))
    def log_source_success(self, *a, **k):
        self.messages.append(("success", a, k))
    def log_source_error(self, *a, **k):
        self.messages.append(("error", a, k))
    def debug(self, *a, **k):
        self.messages.append(("debug", a, k))


class DummyUI:
    def __init__(self):
        self.calls = []
    def show_source_result(self, *a, **k):
        self.calls.append((a, k))


@pytest.fixture()
def source_with_io():
    s = TomadaTempoSource()
    s.logger = DummyLogger()
    s.ui = DummyUI()
    return s


@pytest.mark.unit
def test_collect_events_handles_exception_and_logs(source_with_io):
    s = source_with_io
    target_date = datetime(2025, 8, 1)
    with patch.object(TomadaTempoSource, '_collect_from_weekend_programming', side_effect=RuntimeError("boom")):
        events = s.collect_events(target_date)
    assert events == []
    # Garantir que UI e logger foram acionados no fluxo de erro
    assert any(m[0] == "error" for m in s.logger.messages)
    assert len(s.ui.calls) >= 1


@pytest.mark.unit
def test_collect_from_weekend_programming_no_response_logs(source_with_io):
    s = source_with_io
    with patch.object(TomadaTempoSource, 'make_request', return_value=None):
        evs = s._collect_from_weekend_programming(datetime(2025, 8, 1))
    assert evs == []
    assert any(m[0] == "debug" for m in s.logger.messages)


@pytest.mark.unit
def test_collect_from_weekend_programming_generic_link_then_no_page(source_with_io):
    s = source_with_io
    # HTML com link genérico (sem data específica)
    html_main = '<a href="/programacao">PROGRAMAÇÃO DA TV E INTERNET - geral</a>'
    resp_main = Mock(); resp_main.text = html_main
    # Segunda chamada retorna None para simular falha ao abrir página de programação
    with patch.object(TomadaTempoSource, 'make_request', side_effect=[resp_main, None]):
        evs = s._collect_from_weekend_programming(datetime(2025, 8, 1))
    assert evs == []
    # Deve ter logado mensagens de debug do caminho genérico e da falha ao carregar
    assert any("programming page" in (args[0] if args else "") for tag, args, _ in s.logger.messages if tag == "debug")


@pytest.mark.unit
def test_collect_from_weekend_programming_access_and_parse_zero(source_with_io):
    s = source_with_io
    html_main = '<a href="/programacao">PROGRAMAÇÃO DA TV E INTERNET - geral</a>'
    resp_main = Mock(); resp_main.text = html_main
    resp_page = Mock(); resp_page.text = "<html></html>"; resp_page.url = "https://example.com/programacao"
    with patch.object(TomadaTempoSource, 'make_request', side_effect=[resp_main, resp_page]), \
         patch.object(TomadaTempoSource, '_parse_calendar_page', return_value=[]):
        evs = s._collect_from_weekend_programming(datetime(2025, 8, 1))
    assert evs == []


@pytest.mark.unit
def test_extract_programming_context_invalid_title_then_url(source_with_io):
    s = source_with_io
    # Título sem padrão de datas para forçar fallback pela URL
    html = '<html><head><title>Final de semana | Programação</title></head></html>'
    soup = BeautifulSoup(html, 'html.parser')
    page_url = 'https://site/2025/08/01/qualquer'
    ctx = s._extract_programming_context(soup, page_url)
    # Deve cair no fallback de URL
    assert ctx['start_date'] == '01/08/2025'
    assert ctx['end_date'] == '03/08/2025'
    assert ctx['weekend_dates'] == ['01/08/2025', '02/08/2025', '03/08/2025']


@pytest.mark.unit
def test_collect_from_categories_exception_logged(source_with_io):
    s = source_with_io
    # make_request explode para cobrir ramo de exceção
    with patch.object(TomadaTempoSource, 'make_request', side_effect=Exception('net error')):
        evs = s._collect_from_categories(datetime(2025, 8, 1))
    assert evs == []
    assert any(m[0] == 'debug' for m in s.logger.messages)


@pytest.mark.unit
def test_parse_calendar_page_last_resort_text_parsing(source_with_io):
    s = source_with_io
    # Sem header e sem seletores; texto com data explícita
    html = '<html><body><p>SÁBADO – 02/08/2025 F1 atividade</p></body></html>'
    evs = s._parse_calendar_page(html, datetime(2025, 8, 2))
    assert isinstance(evs, list)
    assert len(evs) >= 1


@pytest.mark.unit
def test_extract_event_from_text_line_exception_logs(source_with_io):
    s = source_with_io
    # Força exceção passando None e garantindo que logger.debug seja executado
    assert s._extract_event_from_text_line(None) is None
    assert any(m[0] == 'debug' for m in s.logger.messages)
