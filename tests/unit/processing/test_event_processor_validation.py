import pytest
from datetime import datetime, timedelta
import sys
import types


def _ensure_third_party_stubs():
    """Cria stubs mínimos para deps opcionais usadas em src.event_processor.

    Evita ImportError quando `fuzzywuzzy`/`unidecode` não estiverem instalados.
    """
    if 'fuzzywuzzy' not in sys.modules:
        mod = types.ModuleType('fuzzywuzzy')
        class _Fuzz:
            @staticmethod
            def ratio(a, b):
                # Implementação mínima suficiente para não quebrar chamadas.
                return 100 if a == b else 0
        mod.fuzz = _Fuzz()
        sys.modules['fuzzywuzzy'] = mod
    if 'unidecode' not in sys.modules:
        mod = types.ModuleType('unidecode')
        import unicodedata as _ud
        def _unidecode(s):
            try:
                return _ud.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode('ascii')
            except Exception:
                return str(s)
        mod.unidecode = _unidecode
        sys.modules['unidecode'] = mod


@pytest.mark.unit
class TestEventProcessorValidation:
    def test_is_event_valid_ok(self):
        _ensure_third_party_stubs()
        from src.event_processor import EventProcessor
        ep = EventProcessor()
        now = datetime.now()
        event = {
            "name": "GP Brasil",
            "datetime": now + timedelta(days=1),
            "detected_category": "Race",
        }
        assert ep._is_event_valid(event) is True

    def test_is_event_valid_missing_fields(self):
        _ensure_third_party_stubs()
        from src.event_processor import EventProcessor
        ep = EventProcessor()
        now = datetime.now()
        # missing detected_category
        event1 = {
            "name": "Endurance 6h",
            "datetime": now,
        }
        # missing datetime
        event2 = {
            "name": "Endurance 6h",
            "detected_category": "Endurance",
        }
        assert ep._is_event_valid(event1) is False
        assert ep._is_event_valid(event2) is False

    def test_is_event_valid_short_name(self):
        _ensure_third_party_stubs()
        from src.event_processor import EventProcessor
        ep = EventProcessor()
        now = datetime.now()
        event = {
            "name": "GP",  # length < 3
            "datetime": now,
            "detected_category": "Race",
        }
        assert ep._is_event_valid(event) is False

    def test_is_event_valid_out_of_range_past(self):
        _ensure_third_party_stubs()
        from src.event_processor import EventProcessor
        ep = EventProcessor()
        now = datetime.now()
        event = {
            "name": "Historic GP",
            "datetime": now - timedelta(days=366),
            "detected_category": "Race",
        }
        assert ep._is_event_valid(event) is False

    def test_is_event_valid_out_of_range_future(self):
        _ensure_third_party_stubs()
        from src.event_processor import EventProcessor
        ep = EventProcessor()
        now = datetime.now()
        event = {
            "name": "Future GP",
            "datetime": now + timedelta(days=366),
            "detected_category": "Race",
        }
        assert ep._is_event_valid(event) is False
