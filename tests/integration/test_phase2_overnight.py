import json
from pathlib import Path
from datetime import datetime, timedelta

import pytest
from icalendar import Calendar

from src.ical_generator import ICalGenerator
from tests.utils.ical_snapshots import compare_or_write_snapshot

pytestmark = pytest.mark.integration

@pytest.fixture()
def overnight_event() -> dict:
    fixture_path = Path(__file__).parents[1] / "fixtures" / "integration" / "scenario_overnight.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    event = data["events"][0]

    if isinstance(event.get("datetime"), str):
        event["datetime"] = datetime.fromisoformat(event["datetime"])  # keeps offset

    return event


def test_phase2_overnight_integration(tmp_path: Path, overnight_event: dict):
    gen = ICalGenerator()
    gen.output_directory = str(tmp_path)

    output_filename = "phase2_overnight.ics"
    output_path = gen.generate_calendar([overnight_event], output_filename=output_filename)

    assert output_path and Path(output_path).exists()

    # Optional validation
    validation = gen.validate_calendar(output_path)
    assert validation.get("valid") is True
    assert validation.get("events_count", 0) == 1

    # Parse ICS and assert fields
    cal = Calendar.from_ical(Path(output_path).read_bytes())
    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    assert len(vevents) == 1

    ve = vevents[0]
    uid = str(ve.get("uid")) if ve.get("uid") is not None else ""
    assert uid.strip() != ""

    summary = str(ve.get("summary"))
    assert "WEC" in summary
    assert "São Paulo" in summary or "Sao Paulo" in summary

    dtstart = ve.decoded("dtstart")
    dtend = ve.decoded("dtend")
    assert isinstance(dtstart, datetime) and isinstance(dtend, datetime)
    assert dtend > dtstart
    # Overnight: date must roll over to next day
    assert dtend.date() == (dtstart.date() + timedelta(days=1))

    # Snapshot compare (normalized)
    snapshot_path = Path(__file__).parents[1] / "snapshots" / "phase2" / output_filename
    compare_or_write_snapshot(output_path, snapshot_path)
