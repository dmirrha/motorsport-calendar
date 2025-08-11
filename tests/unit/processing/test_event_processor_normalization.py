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

    # pytz
    if 'pytz' not in sys.modules:
        mod = types.ModuleType('pytz')
        class _TZ:
            def __init__(self, name):
                self.name = name
            def localize(self, dt):
                class _DummyTZ:
                    def __init__(self, name):
                        self.zone = name
                return dt.replace(tzinfo=_DummyTZ(self.name))
        def timezone(name):
            return _TZ(name)
        mod.timezone = timezone
        sys.modules['pytz'] = mod

    # dateutil.parser
    if 'dateutil' not in sys.modules:
        pkg = types.ModuleType('dateutil')
        parser_mod = types.ModuleType('dateutil.parser')
        def parse(s):
            # very naive: parse "YYYY-MM-DD HH:MM" or "YYYY-MM-DD"
            try:
                if ' ' in s:
                    return datetime.strptime(s, "%Y-%m-%d %H:%M")
                return datetime.strptime(s, "%Y-%m-%d")
            except Exception:
                # fallback to current date to avoid failing test infra; prod code handles exceptions
                return datetime(2025, 1, 1, 12, 0)
        parser_mod.parse = parse
        sys.modules['dateutil'] = pkg
        sys.modules['dateutil.parser'] = parser_mod


@pytest.mark.unit
class TestEventProcessorNormalization:
    def setup_method(self):
        _ensure_stubs()
        from src.event_processor import EventProcessor
        self.ep = EventProcessor()

    def test_normalize_streaming_links_mixed_inputs(self):
        links = [
            {"name": "Band", "url": "http://band.com/stream"},
            " https://f1tv.com/live ",
            None,
            123,
            "ftp://invalid",
            "",
            {"name": "NoURL"},
        ]
        res = self.ep._normalize_streaming_links(links)
        assert res == [
            "http://band.com/stream",
            "https://f1tv.com/live",
        ]

    def test_normalize_date_formats_and_invalid(self):
        assert self.ep._normalize_date("2025-08-09") == "2025-08-09"
        assert self.ep._normalize_date("09/08/2025") == "2025-08-09"
        assert self.ep._normalize_date("09-08-2025") == "2025-08-09"
        assert self.ep._normalize_date("2025/8/9") == "2025-08-09"
        assert self.ep._normalize_date(datetime(2025, 8, 9)) == "2025-08-09"
        assert self.ep._normalize_date(None) is None
        assert self.ep._normalize_date("invalid") is None

    def test_normalize_time_formats_and_invalid(self):
        assert self.ep._normalize_time("9:05") == "09:05"
        assert self.ep._normalize_time("09h05") == "09:05"
        assert self.ep._normalize_time("09.05") == "09:05"
        assert self.ep._normalize_time("25:00") is None
        assert self.ep._normalize_time(None) is None

    def test_normalize_category_location_country_session(self):
        # category
        assert self.ep._normalize_category("fórmula-e") == "Formula E"
        assert self.ep._normalize_category("wec") == "WEC"
        # location
        assert self.ep._normalize_location("interlagos") == "Autódromo José Carlos Pace (Interlagos)"
        # country
        assert self.ep._normalize_country("br") == "Brazil"
        # session type
        assert self.ep._normalize_session_type("FP1") == "practice"
        assert self.ep._normalize_session_type("Quali") == "qualifying"

    def test_compute_datetime_with_and_without_time(self):
        dt1 = self.ep._compute_datetime("2025-08-09", "09:05", "UTC")
        assert dt1 is not None and dt1.hour == 9 and dt1.minute == 5 and getattr(dt1.tzinfo, 'zone', None) == 'UTC'

        dt2 = self.ep._compute_datetime("2025-08-09", None, "UTC")
        assert dt2 is not None and dt2.hour == 12 and dt2.minute == 0 and getattr(dt2.tzinfo, 'zone', None) == 'UTC'

        assert self.ep._compute_datetime(None, "09:05", "UTC") is None
