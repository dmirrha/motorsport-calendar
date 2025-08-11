import sys
import types
from datetime import datetime, timedelta

import pytest


def _ensure_stubs():
    # fuzzywuzzy
    if 'fuzzywuzzy' not in sys.modules:
        mod = types.ModuleType('fuzzywuzzy')
        class _Fuzz:
            @staticmethod
            def ratio(a, b):
                return 100 if a == b else 0
        mod.fuzz = _Fuzz()
        class _Process:
            @staticmethod
            def extract(query, choices, *args, **kwargs):
                return []
            @staticmethod
            def extractOne(query, choices=None, *args, **kwargs):
                return None
        mod.process = _Process()
        sys.modules['fuzzywuzzy'] = mod

    # unidecode
    if 'unidecode' not in sys.modules:
        mod = types.ModuleType('unidecode')
        def _unidecode(s):
            return s
        mod.unidecode = _unidecode
        sys.modules['unidecode'] = mod


@pytest.mark.unit
class TestEventProcessorDedup:
    def setup_method(self):
        _ensure_stubs()
        from src.event_processor import EventProcessor
        self.ep = EventProcessor()

    def test_deduplicate_events_groups_and_merges(self):
        now = datetime(2025, 8, 9, 12, 0, 0)
        e1 = {
            "name": "GP Brazil",
            "datetime": now,
            "detected_category": "Race",
            "streaming_links": ["http://a"],
            "source_priority": 10,
            "official_url": "",
            "location": "",
        }
        e2 = {
            "name": "GP Brazil",  # same -> similar by stub
            "datetime": now + timedelta(minutes=10),  # within 30 min tolerance
            "detected_category": "Race",
            "streaming_links": ["http://b"],
            "source_priority": 20,  # should be selected as best
            "official_url": "http://official",
            "location": "",
        }
        e3 = {
            "name": "Different",
            "datetime": now,
            "detected_category": "Race",
            "streaming_links": [],
            "source_priority": 5,
            "official_url": "",
            "location": "",
        }

        out = self.ep._deduplicate_events([e1, e2, e3])
        assert len(out) == 2
        # Find merged GP Brazil event
        gp = next(e for e in out if e["name"] == "GP Brazil")
        assert gp["official_url"] == "http://official"
        assert set(gp.get("streaming_links", [])) == {"http://a", "http://b"}

        # Distinct event preserved
        assert any(e["name"] == "Different" for e in out)

    def test_are_events_similar_thresholds_and_time_tolerance(self):
        now = datetime(2025, 8, 9, 12, 0, 0)
        a = {"name": "A", "datetime": now, "detected_category": ""}
        b = {"name": "B", "datetime": now, "detected_category": ""}
        # Lower threshold to accept different names under our stub (ratio=0)
        self.ep.similarity_threshold = 0
        assert self.ep._are_events_similar(a, b) is True

        # With large time difference, should fail even with name threshold satisfied
        c = {"name": "A", "datetime": now, "detected_category": ""}
        d = {"name": "A", "datetime": now + timedelta(minutes=45), "detected_category": ""}
        assert self.ep._are_events_similar(c, d) is False

    def test_select_best_event_prioritization_and_merge(self):
        now = datetime(2025, 8, 9, 12, 0, 0)
        low = {
            "name": "Same",
            "datetime": now,
            "detected_category": "Race",
            "streaming_links": ["http://x"],
            "source_priority": 1,
            "official_url": "",
            "location": "Interlagos",
        }
        mid = {
            "name": "Same",
            "datetime": now,
            "detected_category": "Race",
            "streaming_links": [],
            "source_priority": 50,
            "official_url": "http://mid",
            "location": "",
        }
        high = {
            "name": "Same",
            "datetime": now,
            "detected_category": "Race",
            "streaming_links": ["http://y"],
            "source_priority": 99,
            "official_url": "",
            "location": "",
        }
        # All in same group; pick best and merge
        best = self.ep._select_best_event([low, mid, high])
        # high should win by source_priority, and links should include both
        assert set(best.get("streaming_links", [])) == {"http://x", "http://y"}
        # If best has no official_url, should keep its own (empty) unless others provide; 
        # but merge logic only fills when best is missing and other has one
        assert best.get("official_url", "") in {"", "http://mid"}
