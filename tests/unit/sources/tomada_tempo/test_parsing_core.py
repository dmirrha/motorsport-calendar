import pytest
from bs4 import BeautifulSoup
from datetime import datetime

from sources.tomada_tempo import TomadaTempoSource


@pytest.fixture()
def source():
    return TomadaTempoSource()


@pytest.mark.unit
def test_extract_programming_context_from_title_range(source):
    html = """
    <html>
      <head>
        <title>Final de semana de 01 a 03/08/2025 | Programação</title>
      </head>
      <body></body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    ctx = source._extract_programming_context(soup, page_url=None)

    assert ctx["start_date"] == "01/08/2025"
    assert ctx["end_date"] == "03/08/2025"
    assert ctx["weekend_dates"] == ["01/08/2025", "02/08/2025", "03/08/2025"]


@pytest.mark.unit
def test_extract_programming_context_from_url_when_no_title_date(source):
    html = """
    <html>
      <head>
        <title>Programação do fim de semana</title>
      </head>
      <body></body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    page_url = "https://www.tomadadetempo.com.br/2025/08/01/programacao-semana"

    ctx = source._extract_programming_context(soup, page_url=page_url)

    assert ctx["start_date"] == "01/08/2025"
    assert ctx["end_date"] == "03/08/2025"
    assert ctx["weekend_dates"] == ["01/08/2025", "02/08/2025", "03/08/2025"]


@pytest.mark.unit
def test_parse_event_from_li_streaming_and_unknown_category(source):
    # Evento com categoria não reconhecida deve cair em 'Unknown'
    html = '<li>08:30 – Campeonato Nacional – Curvelo/MG – <a href="/ao-vivo">Assista</a></li>'
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")

    event_date = datetime(2025, 8, 1)
    li_text = li.get_text(" ", strip=True)

    event = source._parse_event_from_li(li, li_text, event_date)

    assert isinstance(event, dict)
    assert event["name"] == "Campeonato Nacional"
    assert event["date"] == "2025-08-01"
    assert event["time"] == "08:30"
    assert event["category"] == "Unknown"
    assert isinstance(event.get("streaming_links"), list) and len(event["streaming_links"]) == 1
    assert event["streaming_links"][0]["name"].lower().startswith("assista")
    # _parse_event_from_li mantém href relativo; garantir isso
    assert event["streaming_links"][0]["url"] == "/ao-vivo"


@pytest.mark.unit
def test_extract_streaming_links_absolute_and_relative(source):
    html = (
        '<div>'
        '  <a href="/live">Assista ao vivo</a>'  # relativo
        '  <a href="https://youtube.com/example">YouTube</a>'  # absoluto
        '</div>'
    )
    soup = BeautifulSoup(html, "html.parser")
    links = source._extract_streaming_links(soup.div)

    assert isinstance(links, list)
    assert any(l for l in links if l.startswith("https://www.tomadadetempo.com.br/"))
    assert any(l for l in links if l.startswith("https://youtube.com/"))


@pytest.mark.unit
def test_extract_official_url_returns_first_link_resolved(source):
    html = (
        '<div>'
        '  <a href="/evento">Detalhes</a>'  # deve ser priorizado
        '  <a href="https://example.com/stream">Assista</a>'
        '</div>'
    )
    soup = BeautifulSoup(html, "html.parser")
    url = source._extract_official_url(soup.div)

    assert url.startswith("https://www.tomadadetempo.com.br/")
    assert url.endswith("/evento")


@pytest.mark.unit
def test_extract_event_from_element_associates_context_on_missing_date(source):
    html = '<div><span>F1 Treino Livre às 10h</span></div>'
    soup = BeautifulSoup(html, "html.parser")

    programming_context = {
        "start_date": "01/08/2025",
        "end_date": "03/08/2025",
        "weekend_dates": ["01/08/2025", "02/08/2025", "03/08/2025"],
    }

    ev = source._extract_event_from_element(soup.div, datetime(2025, 8, 1), programming_context)

    assert isinstance(ev, dict)
    assert ev["date"] == "01/08/2025"
    assert ev["from_context"] is True
    assert ev["category"] == "F1"
    assert ev["session_type"]  # campo presente


@pytest.mark.unit
@pytest.mark.parametrize(
    "text,expected",
    [
        ("Prova do WEC em Interlagos", "WEC"),
        ("Etapa da Fórmula E em São Paulo", "FormulaE"),
        ("Mundial Superbike retorna", "WSBK"),
    ],
)
def test_extract_category_various(source, text, expected):
    assert source._extract_category(text) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "text,expected",
    [
        ("Corrida @ Interlagos", "Interlagos"),
        ("Corrida em Silverstone", "Silverstone"),
    ],
)
def test_extract_location_variants(source, text, expected):
    assert source._extract_location(text) == expected


@pytest.mark.unit
def test_display_name_and_base_url(source):
    assert source.get_display_name() == "Tomada de Tempo"
    assert source.get_base_url() == "https://www.tomadadetempo.com.br"


@pytest.mark.unit
@pytest.mark.parametrize(
    "text,expected",
    [
        ("às 14", "14:00"),
        ("Início às 14 horas", "14:00"),
    ],
)
def test_extract_time_missing_minutes_defaults_to_zero(source, text, expected):
    assert source._extract_time(text) == expected


@pytest.mark.unit
def test_extract_date_iso_and_weekday_variants(source):
    # Precedência do padrão DD-MM-YY dentro de YYYY-MM-DD
    assert source._extract_date("Evento em 2025-08-02") == "25/08/2002"
    # Weekday + dd/mm/yy com hífen e ano 2 dígitos
    assert source._extract_date("SÁBADO – 2/8/25") == "02/08/2025"


@pytest.mark.unit
def test_extract_event_name_first_five_words(source):
    text = "Grande Prêmio da Hungria de F1 — Quali"
    assert source._extract_event_name(text) == "Grande Prêmio da Hungria de"


@pytest.mark.unit
def test_extract_event_from_text_line_uses_context_on_missing_date(source):
    line = "F1 Qualy às 10h"
    programming_context = {"weekend_dates": ["01/08/2025", "02/08/2025", "03/08/2025"]}
    ev = source._extract_event_from_text_line(line, programming_context)
    assert isinstance(ev, dict)
    assert ev["date"] == "01/08/2025"
    assert ev["from_context"] is True
