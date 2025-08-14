import json
from pathlib import Path
from datetime import datetime, timedelta

import pytest
from icalendar import Calendar

from src.ical_generator import ICalGenerator
from tests.utils.ical_snapshots import compare_or_write_snapshot


@pytest.fixture()
def optionals_event() -> dict:
    fixture_path = Path(__file__).parents[1] / "fixtures" / "integration" / "scenario_optionals_missing.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    event = data["events"][0]

    if isinstance(event.get("datetime"), str):
        event["datetime"] = datetime.fromisoformat(event["datetime"])  # keeps offset

    return event


def test_phase2_optionals_missing_integration(tmp_path: Path, optionals_event: dict):
    gen = ICalGenerator()
    gen.output_directory = str(tmp_path)

    output_filename = "phase2_optionals.ics"
    output_path = gen.generate_calendar([optionals_event], output_filename=output_filename)

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
    assert "F1" in summary or "Formula 1" in summary

    dtstart = ve.decoded("dtstart")
    dtend = ve.decoded("dtend")
    assert isinstance(dtstart, datetime) and isinstance(dtend, datetime)
    assert dtend > dtstart

    # Optionals: location must be absent
    assert ve.get("location") is None

    # Description should not include More info / Source / Streaming blocks when fields are missing
    desc = str(ve.get("description", ""))
    assert "More info" not in desc
    assert "Source" not in desc
    assert "Streaming" not in desc

    # Snapshot compare (normalized)
    snapshot_path = Path(__file__).parents[1] / "snapshots" / "phase2" / output_filename
    compare_or_write_snapshot(output_path, snapshot_path)
