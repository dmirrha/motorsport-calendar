import os
from datetime import datetime

import pytest
import pytz
from icalendar import Calendar

from src.ical_generator import ICalGenerator


class DummyLogger:
    def __init__(self):
        self.steps = []
        self.debugs = []
        self.success = []
        self.errors = []
        self.warnings = []

    def log_step(self, msg):
        self.steps.append(str(msg))

    def debug(self, msg):
        self.debugs.append(str(msg))

    def log_success(self, msg):
        self.success.append(str(msg))

    def log_error(self, msg):
        self.errors.append(str(msg))

    def log_warning(self, msg):
        self.warnings.append(str(msg))


@pytest.mark.unit
def test_description_streaming_official_source_and_confidence(tmp_path):
    logger = DummyLogger()
    gen = ICalGenerator(logger=logger)
    gen.output_directory = str(tmp_path)

    tz = pytz.timezone("America/Sao_Paulo")
    event_dt = tz.localize(datetime(2025, 8, 10, 15, 0, 0))

    events = [
        {
            "event_id": "evt-desc-001",
            "datetime": event_dt,
            "date": "2025-08-10",
            "name": "Interlagos",
            "detected_category": "Stock Car",
            "session_type": "race",
            "location": "São Paulo",
            "country": "Brasil",
            "streaming_links": [
                "https://stream1.example.com",
                "https://stream2.example.com",
                "https://stream3.example.com",
                "https://stream4.example.com",
            ],
            "official_url": "https://example.com/interlagos",
            "source_display_name": "Oficial",
            "category_confidence": 0.5,
        }
    ]

    out_path = gen.generate_calendar(events, output_filename="desc.ics")
    with open(out_path, "rb") as f:
        cal = Calendar.from_ical(f.read())

    ve = [c for c in cal.walk() if c.name == "VEVENT"][0]

    desc = ve.get("description").to_ical().decode()
    # Deve conter seção Streaming e limitar a 3 links
    assert "Streaming:" in desc
    assert desc.count("https://stream") == 3
    # Deve conter link oficial e fonte
    assert "More info: https://example.com/interlagos" in desc
    assert "Source: Oficial" in desc
    # Confiança baixa deve aparecer
    assert "Category detection confidence: 50%" in desc


@pytest.mark.unit
def test_location_only_country_and_reminders_empty(tmp_path):
    logger = DummyLogger()
    gen = ICalGenerator(logger=logger)
    gen.output_directory = str(tmp_path)
    gen.reminder_minutes = []  # sem lembretes

    tz = pytz.timezone("America/Sao_Paulo")
    event_dt = tz.localize(datetime(2025, 8, 10, 12, 0, 0))

    events = [
        {
            "event_id": "evt-loc-001",
            "datetime": event_dt,
            "date": "2025-08-10",
            "name": "Prova Nacional",
            "detected_category": "MotoGP",
            "session_type": "race",
            "country": "Brasil",
        }
    ]

    out_path = gen.generate_calendar(events, output_filename="loc.ics")
    with open(out_path, "rb") as f:
        cal = Calendar.from_ical(f.read())

    ve = [c for c in cal.walk() if c.name == "VEVENT"][0]

    # Localização deve conter apenas o país
    assert ve.get("location").to_ical().decode() == "Brasil"

    # Sem lembretes quando reminder_minutes vazio
    alarms = [c for c in ve.subcomponents if c.name == "VALARM"]
    assert len(alarms) == 0


@pytest.mark.unit
def test_duration_priority_and_defaults():
    gen = ICalGenerator()

    # Duração para WEC race (endurance)
    assert gen._get_event_duration({"session_type": "race", "detected_category": "WEC"}) == 360
    # Qualifying para F1
    assert gen._get_event_duration({"session_type": "qualifying", "detected_category": "F1"}) == 60
    # Practice default
    assert gen._get_event_duration({"session_type": "practice", "detected_category": "Unknown"}) == 90
    # Sessão desconhecida -> cai no mapa de race default
    assert gen._get_event_duration({"session_type": "other", "detected_category": "Unknown"}) == 120

    # Prioridade mapeada e default
    assert gen._get_event_priority("MotoGP") == 2
    assert gen._get_event_priority("Unknown Series") == 5


@pytest.mark.unit
def test_validate_calendar_with_invalid_file(tmp_path):
    gen = ICalGenerator()
    bad = tmp_path / "bad.ics"
    bad.write_text("NOT AN ICS FILE")

    result = gen.validate_calendar(str(bad))
    assert result["valid"] is False
    assert any("Failed to parse calendar" in e for e in result["errors"])  # branch de erro


@pytest.mark.unit
def test_archive_old_ical_files(tmp_path):
    gen = ICalGenerator()
    gen.output_directory = str(tmp_path)
    os.makedirs(gen.output_directory, exist_ok=True)

    # cria arquivos antigos
    f1 = tmp_path / "old1.ics"
    f2 = tmp_path / "old2.ics"
    f1.write_text("BEGIN:VCALENDAR\nEND:VCALENDAR\n")
    f2.write_text("BEGIN:VCALENDAR\nEND:VCALENDAR\n")

    # Deve mover para history
    gen._archive_old_ical_files()

    history = tmp_path / "history"
    assert history.exists()
    # Ambos arquivos devem ter sido movidos
    moved = list(history.glob("*.ics"))
    assert len(moved) >= 2


@pytest.mark.unit
def test_sanitize_and_stats_and_repr():
    gen = ICalGenerator()

    sanitized = gen._sanitize_filename('Motorsport: Events/2025* F1?.ics')
    assert ":" not in sanitized and "/" not in sanitized and "*" not in sanitized and "?" not in sanitized
    assert sanitized == sanitized.lower()

    # Estatísticas retornam cópia
    stats = gen.get_generation_statistics()
    stats["events_added"] = 999
    assert gen.generation_stats.get("events_added") != 999

    # Representações
    assert "ICalGenerator(" in str(gen)
    assert "<ICalGenerator(" in repr(gen)


@pytest.mark.unit
def test_generate_calendar_with_no_events_logs_warning(tmp_path):
    logger = DummyLogger()
    gen = ICalGenerator(logger=logger)
    gen.output_directory = str(tmp_path)

    out = gen.generate_calendar([])
    assert out == ""
    # logger.log_warning chamado
    assert any("No events" in w for w in logger.warnings)
