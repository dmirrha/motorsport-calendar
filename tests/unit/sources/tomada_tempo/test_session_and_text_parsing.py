import pytest
from bs4 import BeautifulSoup
from datetime import datetime

from sources.tomada_tempo import TomadaTempoSource


@pytest.fixture()
def source():
    return TomadaTempoSource()


@pytest.mark.unit
@pytest.mark.parametrize(
    "text,expected",
    [
        ("Quali de F1", "qualifying"),
        ("Classificação MotoGP", "qualifying"),
        ("Treino Livre 2 (FP2)", "practice"),
        ("FP3 começa às 11:30", "practice"),
        ("Sprint Race hoje", "sprint"),
        ("Grande Prêmio de São Paulo", "race"),
        ("Cerimônia de abertura", "race"),  # default
    ],
)
def test_extract_session_type_mappings(source, text, expected):
    assert source._extract_session_type(text) == expected


@pytest.mark.unit
def test_extract_official_url_none_when_no_links(source):
    html = "<div><span>Sem link de evento</span></div>"
    soup = BeautifulSoup(html, "html.parser")
    assert source._extract_official_url(soup.div) is None


@pytest.mark.unit
def test_extract_streaming_links_ignores_non_streaming(source):
    html = (
        "<div>"
        "  <a href=\"/detalhes\">Detalhes</a>"
        "  <a href=\"https://example.com/info\">Saiba mais</a>"
        "  <a href=\"/inscricoes\">Inscrições</a>"
        "</div>"
    )
    soup = BeautifulSoup(html, "html.parser")
    links = source._extract_streaming_links(soup.div)
    assert isinstance(links, list)
    assert links == []


@pytest.mark.unit
def test_parse_text_content_builds_event_and_uses_context(source):
    # Linha com categoria (F1) e horário sem formato HH:MM (não deve extrair time),
    # mas deve associar a data do contexto do fim de semana.
    html = (
        "<div>"
        "  <p>F1 Treino Livre às 10h</p>"
        "  <p>Outro texto qualquer</p>"
        "</div>"
    )
    ctx = {
        "start_date": "01/08/2025",
        "end_date": "03/08/2025",
        "weekend_dates": ["01/08/2025", "02/08/2025", "03/08/2025"],
    }

    events = source._parse_text_content(html, datetime(2025, 8, 1), programming_context=ctx)

    assert isinstance(events, list)
    assert len(events) == 1
    ev = events[0]
    assert ev["category"] == "F1"
    assert ev["date"] == "01/08/2025"
    assert ev["from_context"] is True
    # Campos não determinados pelo parsing textual permanecem padrão
    assert ev.get("streaming_links") == []
    assert ev.get("official_url") == ""


@pytest.mark.unit
def test_parse_text_content_ignores_non_motorsport_lines(source):
    html = (
        "<div>"
        "  <p>Festival de música ao ar livre</p>"
        "  <p>Feira gastronômica</p>"
        "</div>"
    )
    events = source._parse_text_content(html, datetime(2025, 8, 1))
    assert events == []
