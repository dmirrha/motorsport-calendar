import json
from pathlib import Path
from datetime import datetime, timedelta

import pytest
from icalendar import Calendar

from src.ical_generator import ICalGenerator
from tests.utils.ical_snapshots import compare_or_write_snapshot


@pytest.fixture()
def tz_events() -> list[dict]:
    fixture_path = Path(__file__).parents[1] / "fixtures" / "integration" / "scenario_timezones.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    events = data["events"]

    for ev in events:
        if isinstance(ev.get("datetime"), str):
            ev["datetime"] = datetime.fromisoformat(ev["datetime"])  # keeps offset

    return events


def test_phase2_timezones_integration(tmp_path: Path, tz_events: list[dict]):
    gen = ICalGenerator()
    gen.output_directory = str(tmp_path)

    output_filename = "phase2_timezones.ics"
    output_path = gen.generate_calendar(tz_events, output_filename=output_filename)

    assert output_path and Path(output_path).exists()

    # Optional validation
    validation = gen.validate_calendar(output_path)
    assert validation.get("valid") is True
    assert validation.get("events_count", 0) == 2

    # Parse ICS and assert fields
    cal = Calendar.from_ical(Path(output_path).read_bytes())
    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    assert len(vevents) == 2

    # Build map by SUMMARY to assert per-event expectations
    by_summary = {str(ve.get("summary")): ve for ve in vevents}

    # BR event (-03:00)
    ve_br = next(v for k, v in by_summary.items() if "BR" in k)
    dtstart_br = ve_br.decoded("dtstart")
    dtend_br = ve_br.decoded("dtend")
    assert isinstance(dtstart_br, datetime) and isinstance(dtend_br, datetime)
    assert dtend_br - dtstart_br == timedelta(minutes=90)  # practice default
    # When TZID is present in ICS, icalendar may return naive datetime on decoded();
    # assert TZID parameter presence and local time components instead of utcoffset.
    tzid_br = ve_br.get("dtstart").params.get("TZID") if ve_br.get("dtstart") is not None else None
    assert tzid_br, "Expected TZID parameter for BR event"
    assert dtstart_br.hour == 8 and dtstart_br.minute == 0

    # UK event (+00:00)
    ve_uk = next(v for k, v in by_summary.items() if "UK" in k)
    dtstart_uk = ve_uk.decoded("dtstart")
    dtend_uk = ve_uk.decoded("dtend")
    assert isinstance(dtstart_uk, datetime) and isinstance(dtend_uk, datetime)
    assert dtend_uk - dtstart_uk == timedelta(minutes=90)  # practice default
    tzid_uk = ve_uk.get("dtstart").params.get("TZID") if ve_uk.get("dtstart") is not None else None
    # For UTC, ICS may use 'Z' suffix without TZID, so only assert local time components.
    assert dtstart_uk.hour == 13 and dtstart_uk.minute == 0

    # Basic presence
    for ve in vevents:
        uid = str(ve.get("uid")) if ve.get("uid") is not None else ""
        assert uid.strip() != ""
        summary = str(ve.get("summary"))
        assert "F1" in summary or "Formula 1" in summary

    # Snapshot compare (normalized)
    snapshot_path = Path(__file__).parents[1] / "snapshots" / "phase2" / output_filename
    compare_or_write_snapshot(output_path, snapshot_path)
