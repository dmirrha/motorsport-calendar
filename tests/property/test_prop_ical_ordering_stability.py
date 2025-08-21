from datetime import datetime
from typing import List

import pytest
import pytz
from hypothesis import given, strategies as st

from src.ical_generator import ICalGenerator


class CapturingCalendar:
    def __init__(self):
        self.events_uids: List[str] = []

    def add_component(self, component):
        # icalendar.Event exposes get('uid') as vText/vCal types; str() is fine
        uid = component.get("uid")
        if uid is not None:
            self.events_uids.append(str(uid))

    # generate_calendar() writes the calendar to file, so provide a minimal API
    def to_ical(self):
        return b"BEGIN:VCALENDAR\nEND:VCALENDAR\n"


class StubICalGenerator(ICalGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_calendar = None

    def _create_calendar(self):
        cal = CapturingCalendar()
        self._last_calendar = cal
        return cal

    def _archive_old_ical_files(self):
        # Avoid touching filesystem history during tests
        return None


TZ = pytz.timezone("America/Sao_Paulo")


def _event_dict(event_id: str, dt: datetime, category: str, display_name: str, name: str, prio: int):
    return {
        "event_id": event_id,
        "datetime": TZ.localize(dt) if dt.tzinfo is None else dt,
        "detected_category": category,
        "display_name": display_name,
        "name": name,
        "source_priority": prio,
        "session_type": "race",
    }


# Small alphabets keep example generation fast and focused on ordering behavior
_cat = st.sampled_from(["Formula 1", "MotoGP", "IndyCar"])  # maps to display strings in generator
_name = st.text(alphabet=st.sampled_from(list("abcdefghijklmnopqrstuvwxyz ")), min_size=3, max_size=20)


@pytest.mark.property
@given(
    count=st.integers(min_value=2, max_value=10),
    year=st.integers(min_value=2023, max_value=2025),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28),
    base_hour=st.integers(min_value=8, max_value=18),
)
def test_ical_sorting_is_deterministic(count, year, month, day, base_hour, tmp_path):
    gen = StubICalGenerator(config_manager=None, logger=None, ui_manager=None)
    gen.output_directory = str(tmp_path)
    gen.enforce_sort = True

    # Build events with controlled variety to exercise all tie-breakers
    events: List[dict] = []
    for i in range(count):
        dt = datetime(year, month, day, (base_hour + i) % 24, i % 60)
        category = ["Formula 1", "MotoGP", "IndyCar"][i % 3]
        display_name = f"Grand Prix {i}"
        name = f"gp {i}"
        prio = (i * 7) % 100
        events.append(_event_dict(f"e{i}", dt, category, display_name, name, prio))

    # Shuffle order (reverse) and ensure output order equals the sorted key in generator
    reversed_events = list(reversed(events))

    def sort_key(e):
        return (
            e.get("datetime"),
            str(e.get("detected_category") or ""),
            str(e.get("display_name") or e.get("name") or ""),
            -int(e.get("source_priority", 0)),
            str(e.get("event_id") or ""),
        )

    expected = [f"{e['event_id']}@motorsport-calendar" for e in sorted(events, key=sort_key)]

    # First run
    gen.generate_calendar(reversed_events, output_filename="t.ics")
    captured1 = gen._last_calendar.events_uids
    assert captured1 == expected

    # Second run with original order must match as well
    gen.generate_calendar(events, output_filename="t2.ics")
    captured2 = gen._last_calendar.events_uids
    assert captured2 == expected
