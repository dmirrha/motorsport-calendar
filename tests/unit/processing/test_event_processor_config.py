import sys
import types
from datetime import datetime

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
        sys.modules['fuzzywuzzy'] = mod

    # unidecode
    if 'unidecode' not in sys.modules:
        mod = types.ModuleType('unidecode')
        def _unidecode(s):
            return s
        mod.unidecode = _unidecode
        sys.modules['unidecode'] = mod


class _ConfigStub:
    def get_deduplication_config(self):
        return {
            'similarity_threshold': 0,            # extremo para facilitar o assert
            'time_tolerance_minutes': 120,
            'location_similarity_threshold': 0,
            'category_similarity_threshold': 0,
        }

    def get_general_config(self):
        return {
            'weekend_detection': {
                'start_day': 1,   # Monday
                'end_day': 3,     # Wednesday (apenas para validar carregamento)
                'extend_hours': 2,
            }
        }

    def get_timezone(self):
        return 'UTC'


@pytest.mark.unit
class TestEventProcessorConfig:
    def setup_method(self):
        _ensure_stubs()

    def test_load_config_applies_values(self):
        from src.event_processor import EventProcessor
        ep = EventProcessor(config_manager=_ConfigStub())
        # valores devem refletir o que o stub fornece
        assert ep.similarity_threshold == 0
        assert ep.time_tolerance_minutes == 120
        assert ep.location_similarity_threshold == 0
        assert ep.category_similarity_threshold == 0
        assert ep.weekend_start_day == 1
        assert ep.weekend_end_day == 3
        assert ep.extend_weekend_hours == 2

    def test_are_events_similar_respects_config_thresholds(self):
        from src.event_processor import EventProcessor
        ep = EventProcessor(config_manager=_ConfigStub())
        now = datetime(2025, 8, 9, 12, 0, 0)
        a = {"name": "A", "datetime": now, "detected_category": ""}
        b = {"name": "B", "datetime": now, "detected_category": ""}
        # Com similarity_threshold=0 (via config), mesmo nomes diferentes (ratio=0) devem ser considerados similares
        assert ep._are_events_similar(a, b) is True
