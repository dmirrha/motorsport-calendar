import pytest
from datetime import datetime, timedelta
import sys
import types


def _ensure_third_party_stubs():
    if 'fuzzywuzzy' not in sys.modules:
        mod = types.ModuleType('fuzzywuzzy')
        class _Fuzz:
            @staticmethod
            def ratio(a, b):
                return 100 if a == b else 0
        mod.fuzz = _Fuzz()
        sys.modules['fuzzywuzzy'] = mod
    if 'unidecode' not in sys.modules:
        mod = types.ModuleType('unidecode')
        def _unidecode(s):
            return s
        mod.unidecode = _unidecode
        sys.modules['unidecode'] = mod


@pytest.mark.unit
class TestEventProcessorWeekendFilter:
    def test_filter_weekend_inclusive_bounds(self):
        _ensure_third_party_stubs()
        from src.event_processor import EventProcessor

        ep = EventProcessor()
        # Define um intervalo de fim de semana fixo
        # Sexta 18:00 até Domingo 21:00 (naive)
        friday = datetime(2025, 8, 8, 18, 0, 0)
        sunday = datetime(2025, 8, 10, 21, 0, 0)
        target = (friday, sunday)

        inside_start = {"name": "StartEvent", "datetime": friday, "detected_category": "Race"}
        before_start = {"name": "BeforeEvent", "datetime": friday - timedelta(minutes=1), "detected_category": "Race"}
        inside_end = {"name": "EndEvent", "datetime": sunday, "detected_category": "Race"}
        after_end = {"name": "AfterEvent", "datetime": sunday + timedelta(minutes=1), "detected_category": "Race"}
        middle = {"name": "MidEvent", "datetime": friday + timedelta(days=1), "detected_category": "Race"}

        events = [inside_start, before_start, inside_end, after_end, middle]
        filtered = ep._filter_weekend_events(events, target)

        names = {e["name"] for e in filtered}
        assert names == {"StartEvent", "EndEvent", "MidEvent"}

    def test_filter_weekend_empty(self):
        _ensure_third_party_stubs()
        from src.event_processor import EventProcessor

        ep = EventProcessor()
        friday = datetime(2025, 8, 8, 18, 0, 0)
        sunday = datetime(2025, 8, 10, 21, 0, 0)
        filtered = ep._filter_weekend_events([], (friday, sunday))
        assert filtered == []
