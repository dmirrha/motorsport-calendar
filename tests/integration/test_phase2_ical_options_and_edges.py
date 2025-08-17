"""
Phase 2 Integration — iCal Options & Edge Cases
Objetivo: validar opções de geração ICS e casos de borda (streaming_links, flags desativadas).
Marcadores: integration
"""

import json
from pathlib import Path
from datetime import datetime

import pytest

from src.ical_generator import ICalGenerator
from tests.utils.ical_snapshots import compare_or_write_snapshot, normalize_ics_text
from icalendar import Calendar


pytestmark = pytest.mark.integration


@pytest.fixture()
def base_event() -> dict:
    """Carrega um evento base do cenário simples e garante datetime com timezone."""
    fixture_path = Path(__file__).parents[1] / "fixtures" / "integration" / "scenario_basic.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    event = data["events"][0]
    if isinstance(event.get("datetime"), str):
        event["datetime"] = datetime.fromisoformat(event["datetime"])  # preserva offset
    return event


def test_edges_streaming_sorted_and_limited_with_alarms(tmp_path: Path, base_event: dict):
    """Streaming fora de ordem deve ser ordenado alfabeticamente e limitado a 3; VALARM padrão presente."""
    event = dict(base_event)
    event.update(
        {
            "streaming_links": [
                "https://z.example/stream",
                "https://a.example/alpha",
                "https://m.example/mid",
                "https://b.example/beta",
            ]
        }
    )

    gen = ICalGenerator()
    gen.output_directory = str(tmp_path)

    output_filename = "phase2_edges_streaming_sorted_limit.ics"
    output_path = gen.generate_calendar([event], output_filename=output_filename)

    assert output_path and Path(output_path).exists()

    # Validação estrutural
    validation = gen.validate_calendar(output_path)
    assert validation.get("valid") is True
    assert validation.get("events_count", 0) >= 1

    # Asserts diretos mínimos via parsing (evita problemas de folding da linha)
    cal = Calendar.from_ical(Path(output_path).read_bytes())
    descriptions = [c.get('description') for c in cal.walk() if getattr(c, 'name', '') == 'VEVENT']
    assert descriptions, "Esperado ao menos um VEVENT com DESCRIPTION"
    desc_text = str(descriptions[0])
    assert "Streaming:" in desc_text
    assert "https://a.example/alpha" in desc_text
    assert "https://b.example/beta" in desc_text
    assert "https://m.example/mid" in desc_text
    assert "https://z.example/stream" not in desc_text  # limitado a 3
    # VALARM padrão presente (reminders default)
    normalized = normalize_ics_text(Path(output_path).read_bytes())
    assert "BEGIN:VALARM" in normalized

    # Snapshot canônico
    snapshot_path = Path(__file__).parents[1] / "snapshots" / "phase2" / output_filename
    compare_or_write_snapshot(output_path, snapshot_path)


def test_edges_flags_disabled_no_streaming_no_source_no_alarms(tmp_path: Path, base_event: dict):
    """Com flags desativadas, não deve haver seção Streaming, Source nem VALARM."""
    event = dict(base_event)
    event.update(
        {
            "streaming_links": [
                "https://a.example/alpha",
                "https://b.example/beta",
            ],
            "source_display_name": "UnitTestSource",
        }
    )

    gen = ICalGenerator()
    gen.output_directory = str(tmp_path)
    gen.include_streaming_links = False
    gen.include_source_info = False
    gen.reminder_minutes = []  # sem VALARM

    output_filename = "phase2_edges_flags_disabled.ics"
    output_path = gen.generate_calendar([event], output_filename=output_filename)

    assert output_path and Path(output_path).exists()

    # Validação estrutural
    validation = gen.validate_calendar(output_path)
    assert validation.get("valid") is True
    assert validation.get("events_count", 0) >= 1

    # Asserts diretos: sem blocos de streaming/source e sem VALARM
    cal = Calendar.from_ical(Path(output_path).read_bytes())
    descriptions = [c.get('description') for c in cal.walk() if getattr(c, 'name', '') == 'VEVENT']
    assert descriptions, "Esperado ao menos um VEVENT com DESCRIPTION"
    desc_text = str(descriptions[0])
    assert "Streaming:" not in desc_text
    assert "Source:" not in desc_text
    normalized = normalize_ics_text(Path(output_path).read_bytes())
    assert "BEGIN:VALARM" not in normalized

    # Snapshot canônico
    snapshot_path = Path(__file__).parents[1] / "snapshots" / "phase2" / output_filename
    compare_or_write_snapshot(output_path, snapshot_path)
