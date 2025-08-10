import pytest

from sources.tomada_tempo import TomadaTempoSource


class _LoggerStub:
    def __init__(self):
        self.debugs = []

    def debug(self, msg):
        self.debugs.append(msg)


@pytest.mark.unit
def test_parse_calendar_page_malformed_html():
    # HTML propositalmente malformado
    html = "<html><body><h5>PROGRAMAÇÃO</h5><ul><li>Evento 1"

    src = TomadaTempoSource(config_manager=None, logger=_LoggerStub())

    events = src._parse_calendar_page(html_content=html, target_date=__import__("datetime").datetime.now())

    # Não deve lançar exceção e pode retornar lista vazia
    assert isinstance(events, list)
    assert events == [] or all(isinstance(e, dict) for e in events)
