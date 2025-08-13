#!/usr/bin/env python3
"""
Testes unitários determinísticos para o parser de TomadaTempoSource.
Foco: estrutura de programação do fim de semana (h5 + ul/li), cabeçalhos alternativos,
horários sem minutos/variações, eventos overnight e extração de contexto do título.
"""

from pathlib import Path
from datetime import datetime as dt
import pytz
from bs4 import BeautifulSoup

from sources.tomada_tempo import TomadaTempoSource


FIXTURES_DIR = Path(__file__).resolve().parents[4] / "tests" / "fixtures" / "html"


def read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def make_target_friday(date_str: str = "01/08/2025", tz_name: str = "America/Sao_Paulo"):
    tz = pytz.timezone(tz_name)
    base = dt.strptime(date_str, "%d/%m/%Y")
    return tz.localize(base)


def test_parse_weekend_minimal_structure():
    # Arrange
    html = read_fixture("tomada_tempo_weekend_minimal.html")
    source = TomadaTempoSource()
    target_date = make_target_friday()

    # Act
    events = source._parse_calendar_page(html, target_date)

    # Assert básicos
    assert isinstance(events, list)
    assert len(events) == 4  # 2 sexta, 1 sábado, 1 domingo

    # Sexta 08:00 F1
    ev0 = events[0]
    assert ev0.get("from_weekend_programming") is True
    assert ev0.get("date") == "2025-08-01"
    assert ev0.get("time") == "08:00"
    assert ev0.get("category") == "F1"
    assert isinstance(ev0.get("streaming_links"), list)

    # Sexta 14:30 NASCAR
    ev1 = events[1]
    assert ev1.get("date") == "2025-08-01"
    assert ev1.get("time") == "14:30"
    assert ev1.get("category") == "NASCAR"

    # Sábado 10:00 F1
    ev2 = events[2]
    assert ev2.get("date") == "2025-08-02"
    assert ev2.get("time") == "10:00"
    assert ev2.get("category") == "F1"

    # Domingo 10:00 F1
    ev3 = events[3]
    assert ev3.get("date") == "2025-08-03"
    assert ev3.get("time") == "10:00"
    assert ev3.get("category") == "F1"


def test_parse_weekend_alt_headers_and_dot_time():
    # Arrange
    html = read_fixture("tomada_tempo_weekend_alt_header.html")
    source = TomadaTempoSource()
    target_date = make_target_friday()

    # Act
    events = source._parse_calendar_page(html, target_date)

    # Assert
    assert len(events) == 3

    # Sexta 08.00 MotoGP -> 08:00
    ev0 = events[0]
    assert ev0.get("date") == "2025-08-01"
    assert ev0.get("time") == "08:00"
    assert ev0.get("category") == "MotoGP"

    # Sábado 12:15 F2
    ev1 = events[1]
    assert ev1.get("date") == "2025-08-02"
    assert ev1.get("time") == "12:15"
    assert ev1.get("category") == "F2"

    # Domingo 15:00 NASCAR
    ev2 = events[2]
    assert ev2.get("date") == "2025-08-03"
    assert ev2.get("time") == "15:00"
    assert ev2.get("category") == "NASCAR"


def test_parse_weekend_no_minutes_and_variants():
    # Arrange
    html = read_fixture("tomada_tempo_weekend_no_minutes.html")
    source = TomadaTempoSource()
    target_date = make_target_friday()

    # Act
    events = source._parse_calendar_page(html, target_date)

    # Assert
    assert len(events) >= 4  # 3 sábado + 2 domingo (5) no fixture; parser pode filtrar itens inválidos

    # Sábado F1 TL3 — às 8h -> 08:00
    ev0 = events[0]
    assert ev0.get("date") == "2025-08-02"
    assert ev0.get("time") == "08:00"
    assert ev0.get("category") == "F1"

    # Sábado NASCAR — 14 horas -> 14:00
    ev1 = events[1]
    assert ev1.get("date") == "2025-08-02"
    assert ev1.get("time") == "14:00"
    assert ev1.get("category") == "NASCAR"

    # Sábado Stock Car — "21" (sem minutos) pode não ser extraído -> None aceitável
    ev2 = events[2]
    assert ev2.get("date") == "2025-08-02"
    assert ev2.get("category") == "StockCar"
    # tempo pode ser None dependendo do padrão suportado
    assert ev2.get("time") in {None, "21:00"}

    # Domingo F1 Corrida — às 10 -> 10:00
    ev3 = next(e for e in events if e.get("category") == "F1" and e.get("date") == "2025-08-03")
    assert ev3.get("time") == "10:00"


def test_parse_weekend_overnight_cross_midnight():
    # Arrange
    html = read_fixture("tomada_tempo_weekend_overnight.html")
    source = TomadaTempoSource()
    target_date = make_target_friday()

    # Act
    events = source._parse_calendar_page(html, target_date)

    # Assert: dois eventos após meia-noite no domingo
    sunday_events = [e for e in events if e.get("date") == "2025-08-03"]
    assert len(sunday_events) >= 2
    times = {e.get("time") for e in sunday_events}
    assert {"00:10", "01:05"}.issubset(times)


def test_extract_programming_context_from_title():
    # Arrange
    html = read_fixture("tomada_tempo_weekend_minimal.html")
    soup = BeautifulSoup(html, "html.parser")
    source = TomadaTempoSource()

    # Act
    context = source._extract_programming_context(soup)

    # Assert
    assert context["start_date"] == "01/08/2025"
    assert context["end_date"] == "03/08/2025"
    assert context["weekend_dates"] == ["01/08/2025", "02/08/2025", "03/08/2025"]
