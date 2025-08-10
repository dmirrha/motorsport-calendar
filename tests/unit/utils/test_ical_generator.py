import os
from datetime import datetime

import pytest
import pytz

from src.ical_generator import ICalGenerator
from icalendar import Calendar


class DummyLogger:
    def __init__(self):
        self.info_msgs = []
        self.debug_msgs = []
        self.errors = []
        self.steps = []
        self.success = []

    def info(self, msg):
        self.info_msgs.append(str(msg))

    def debug(self, msg):
        self.debug_msgs.append(str(msg))

    def log_step(self, msg):
        self.steps.append(str(msg))

    def log_success(self, msg):
        self.success.append(str(msg))

    def log_error(self, msg):
        self.errors.append(str(msg))


@pytest.mark.unit
def test_create_ical_event_without_datetime_returns_none():
    gen = ICalGenerator(logger=DummyLogger())
    assert gen._create_ical_event({}) is None


@pytest.mark.unit
def test_generate_calendar_writes_file_and_validates(tmp_path):
    logger = DummyLogger()
    gen = ICalGenerator(logger=logger)
    gen.output_directory = str(tmp_path)

    tz = pytz.timezone("America/Sao_Paulo")
    event_dt = tz.localize(datetime(2025, 8, 10, 15, 0, 0))

    events = [
        {
            "event_id": "evt-001",
            "datetime": event_dt,
            "date": "2025-08-10",
            "name": "Monaco GP",
            "detected_category": "Formula 1",
            "session_type": "race",
            "location": "Monaco",
            "country": "Monaco",
            "official_url": "https://example.com",
            "source": "tt",
            "source_display_name": "TomadaTempo",
        }
    ]

    out_path = gen.generate_calendar(events, output_filename="test.ics")

    assert out_path
    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 0

    validation = gen.validate_calendar(out_path)
    assert validation["valid"] is True
    assert validation["events_count"] == 1

    # Parse ICS and assert vevent fields
    with open(out_path, "rb") as f:
        cal = Calendar.from_ical(f.read())

    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    assert len(vevents) == 1
    ve = vevents[0]

    # SUMMARY should be "Formula 1 - Monaco GP" (no session suffix for 'race')
    assert ve.get("summary").to_ical().decode() == "Formula 1 - Monaco GP"

    # DTSTART/DTEND present and duration >= default mapping
    dtstart = ve.decoded("dtstart")
    dtend = ve.decoded("dtend")
    assert dtend > dtstart

    # UID present
    assert "uid" in ve

    # Categories should contain category; for race we do not include session type
    cats = ve.get("categories").to_ical().decode()
    assert "Formula 1" in [c.strip() for c in cats.split(",")]

    # Custom X- props
    assert "x-motorsport-category" in ve
    assert ve.get("x-motorsport-category").to_ical().decode().lower() == "formula 1"
    assert "x-motorsport-session" in ve

    # Reminders (VALARM) present according to default [30, 60]
    alarms = [c for c in ve.subcomponents if c.name == "VALARM"]
    assert len(alarms) == 2


@pytest.mark.unit
def test_create_ical_event_fields_for_non_race_session(tmp_path):
    logger = DummyLogger()
    gen = ICalGenerator(logger=logger)
    gen.output_directory = str(tmp_path)

    tz = pytz.timezone("America/Sao_Paulo")
    event_dt = tz.localize(datetime(2025, 8, 10, 11, 0, 0))

    event = {
        "event_id": "evt-qual-01",
        "datetime": event_dt,
        "date": "2025-08-10",
        "name": "Monaco GP",
        "detected_category": "Formula 1",
        "session_type": "qualifying",
        "location": "Monaco",
        "country": "Monaco",
    }

    # End-to-end via ICS for robust assertion of fields
    out_path = gen.generate_calendar([event], output_filename="qual.ics")
    with open(out_path, "rb") as f:
        cal = Calendar.from_ical(f.read())

    ve = [c for c in cal.walk() if c.name == "VEVENT"][0]

    # SUMMARY must append session type when not 'race'
    assert ve.get("summary").to_ical().decode() == "Formula 1 - Monaco GP (Qualifying)"

    # Categories must include both category and session type
    cats = [c.strip() for c in ve.get("categories").to_ical().decode().split(",")]
    assert "Formula 1" in cats
    assert "Qualifying" in cats

    # Priority mapped to Formula 1 => 1
    assert int(ve.get("priority").to_ical().decode()) == 1

    # Location should not duplicate country when identical
    assert ve.get("location").to_ical().decode() == "Monaco"
