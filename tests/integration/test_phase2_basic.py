import json
from pathlib import Path
from datetime import datetime

import pytest

from src.ical_generator import ICalGenerator
from tests.utils.ical_snapshots import compare_or_write_snapshot

pytestmark = pytest.mark.integration

@pytest.fixture()
def basic_event() -> dict:
    fixture_path = Path(__file__).parents[1] / "fixtures" / "integration" / "scenario_basic.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    event = data["events"][0]

    # Ensure datetime is a timezone-aware datetime object
    # Input is ISO string like "2025-11-09T14:00:00-03:00"
    if isinstance(event.get("datetime"), str):
        event["datetime"] = datetime.fromisoformat(event["datetime"])  # retains offset

    return event


def test_phase2_basic_integration_generates_stable_ics(tmp_path: Path, basic_event: dict):
    gen = ICalGenerator()

    # Write in temp directory to avoid polluting repo output/
    gen.output_directory = str(tmp_path)

    output_filename = "phase2_basic.ics"
    output_path = gen.generate_calendar([basic_event], output_filename=output_filename)

    assert output_path, "Expected a non-empty path for generated ICS"
    assert Path(output_path).exists(), "ICS file should have been created"

    # Optional validation (best-effort)
    validation = gen.validate_calendar(output_path)
    assert validation.get("valid") is True
    assert validation.get("events_count", 0) >= 1

    # Snapshot compare (normalized)
    snapshot_path = Path(__file__).parents[1] / "snapshots" / "phase2" / output_filename
    compare_or_write_snapshot(output_path, snapshot_path)
