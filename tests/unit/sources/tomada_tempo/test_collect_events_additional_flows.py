import pytest
from datetime import datetime
from unittest.mock import patch, Mock

from sources.tomada_tempo import TomadaTempoSource


class DummyLogger:
    def __init__(self):
        self.logs = []
    def log_source_start(self, *a, **k):
        self.logs.append(("start", a, k))
    def log_source_success(self, *a, **k):
        self.logs.append(("success", a, k))
    def log_source_error(self, *a, **k):
        self.logs.append(("error", a, k))
    def debug(self, *a, **k):
        self.logs.append(("debug", a, k))


class DummyUI:
    def __init__(self):
        self.calls = []
    def show_source_result(self, *a, **k):
        self.calls.append((a, k))


@pytest.fixture()
def source_io():
    s = TomadaTempoSource()
    s.logger = DummyLogger()
    s.ui = DummyUI()
    return s


@pytest.mark.unit
def test_collect_events_without_target_date_success_logs_and_ui(source_io):
    s = source_io
    with patch.object(TomadaTempoSource, '_collect_from_weekend_programming', return_value=[{"name": "E1"}]) as wknd, \
         patch.object(TomadaTempoSource, 'filter_weekend_events', side_effect=lambda evs, rng: evs) as filt, \
         patch.object(TomadaTempoSource, 'normalize_event_data', side_effect=lambda e: e) as norm, \
         patch.object(TomadaTempoSource, 'validate_event_data', return_value=True) as valid:
        events = s.collect_events()  # target_date None cobre _get_next_weekend e tz.localize
    assert events == [{"name": "E1"}]
    assert any(tag == "start" for tag, *_ in s.logger.logs)
    assert any(tag == "success" for tag, *_ in s.logger.logs)
    assert len(s.ui.calls) >= 1
    wknd.assert_called_once()
    assert filt.called and norm.called and valid.called


@pytest.mark.unit
def test_collect_from_weekend_programming_exact_date_link(source_io):
    s = source_io
    # Link com data exata no texto
    html_main = '<a href="/prog/123">PROGRAMAÇÃO DA TV E INTERNET – 01/08/2025</a>'
    resp_main = Mock(); resp_main.text = html_main
    resp_page = Mock(); resp_page.text = "<html></html>"; resp_page.url = "https://www.tomadadetempo.com.br/prog/123"

    with patch.object(TomadaTempoSource, 'make_request', side_effect=[resp_main, resp_page]) as mk, \
         patch.object(TomadaTempoSource, '_parse_calendar_page', return_value=[{"name": "EV"}]) as parse_page:
        evs = s._collect_from_weekend_programming(datetime(2025, 8, 1))

    assert isinstance(evs, list) and evs == [{"name": "EV"}]
    assert mk.call_count == 2
    parse_page.assert_called_once()


@pytest.mark.unit
def test_parse_calendar_page_exception_logging(source_io, monkeypatch):
    s = source_io
    # Força exceção dentro do try de _parse_calendar_page
    def boom(*a, **k):
        raise RuntimeError("boom")
    monkeypatch.setattr(TomadaTempoSource, '_extract_programming_context', boom)

    evs = s._parse_calendar_page("<html></html>", datetime(2025, 8, 1))
    assert evs == []
    assert any(tag == 'debug' for tag, *_ in s.logger.logs)


@pytest.mark.unit
def test_extract_event_from_element_exception_with_logger(source_io):
    s = source_io
    ev = s._extract_event_from_element(None, datetime(2025, 8, 1))
    assert ev is None
    assert any(tag == 'debug' for tag, *_ in s.logger.logs)
