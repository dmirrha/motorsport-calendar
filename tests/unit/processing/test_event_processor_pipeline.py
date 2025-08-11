import sys
import types
from datetime import datetime, timedelta

import pytest


class _LoggerStub:
    def __init__(self):
        self.steps = []
        self.debugs = []
        self.warnings = []
    def log_step(self, msg):
        self.steps.append(msg)
    def debug(self, msg):
        self.debugs.append(msg)
    def log_warning(self, msg):
        self.warnings.append(msg)


class _ConfigStub:
    def __init__(self, tz='UTC'):
        self._tz = tz
    def get_deduplication_config(self):
        return {
            'similarity_threshold': 80,
            'time_tolerance_minutes': 45,
            'location_similarity_threshold': 70,
            'category_similarity_threshold': 85,
        }
    def get_general_config(self):
        return {
            'weekend_detection': {
                'start_day': 4,
                'end_day': 6,
                'extend_hours': 6,
            }
        }
    def get_timezone(self):
        return self._tz


class _SilentStub:
    def __init__(self, keep=True):
        self.logged = False
        self.keep = keep
    def filter_events(self, events):
        if self.keep:
            return events, []
        # filter out all
        return [], events
    def log_filtering_summary(self, events):
        self.logged = True


class _CategoryDetectorStub:
    def __init__(self, category='Race'):
        self.category = category
    def detect_categories_batch(self, inputs):
        return [{
            'category': self.category,
            'confidence': 0.9,
            'source': 'stub'
        } for _ in inputs]


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


@pytest.mark.unit
class TestEventProcessorPipeline:
    def test_process_events_empty_warns_and_returns(self):
        _ensure_stubs()
        from src.event_processor import EventProcessor
        logger = _LoggerStub()
        ep = EventProcessor(config_manager=_ConfigStub(), logger=logger)
        # Monkeypatch silent manager to avoid importing real
        ep.silent_period_manager = _SilentStub()
        out = ep.process_events([])
        assert out == []
        assert any('No events to process' in w for w in logger.warnings)

    def test_process_events_pipeline_with_detector_and_silent(self):
        _ensure_stubs()
        from src.event_processor import EventProcessor
        logger = _LoggerStub()
        cfg = _ConfigStub(tz='UTC')
        cat = _CategoryDetectorStub('Endurance')
        ep = EventProcessor(config_manager=cfg, logger=logger, category_detector=cat)
        ep.silent_period_manager = _SilentStub(keep=True)

        raw = [
            {
                'name': 'GP Brazil',
                'raw_category': 'f1',
                'date': '2025-08-09',
                'time': '09:00',
                'timezone': 'UTC',
                'location': 'interlagos',
                'country': 'br',
                'session_type': 'qualifying',
                'streaming_links': [{'name': 'x', 'url': 'http://a'}],
                'source': 'unit',
                'source_priority': 10,
            },
            {
                'name': 'GP Brazil',
                'raw_category': 'f1',
                'date': '2025-08-09',
                'time': '09:10',  # within tolerance
                'timezone': 'UTC',
                'location': 'interlagos',
                'country': 'br',
                'session_type': 'qualifying',
                'streaming_links': [{'name': 'y', 'url': 'http://b'}],
                'source': 'unit',
                'source_priority': 20,
            },
        ]
        # Provide a datetime to trigger weekend computation branch
        target_dt = datetime(2025, 8, 9, 8, 0, 0)
        out = ep.process_events(raw, target_weekend=target_dt)
        assert len(out) == 1  # deduplicated
        ev = out[0]
        assert ev['detected_category'] == 'Endurance'
        # stats populated
        stats = ep.get_processing_statistics()
        assert stats['events_input'] == 2
        assert stats['events_normalized'] == 2
        assert stats['events_weekend_filtered'] >= 1
        assert stats['events_deduplicated'] == 1
        assert stats['events_validated'] == 1
        assert 'processing_start_time' in stats and 'processing_end_time' in stats
        # logger had summary
        assert any('Processing Summary' in s for s in logger.steps)

    def test_detect_categories_without_detector_uses_raw(self):
        _ensure_stubs()
        from src.event_processor import EventProcessor
        ep = EventProcessor(logger=_LoggerStub())
        events = [{'name': 'x', 'raw_category': 'wec'}]
        out = ep._detect_categories(events)
        assert out[0]['detected_category'] == 'wec'

    def test_normalize_events_exception_path(self, monkeypatch):
        _ensure_stubs()
        from src.event_processor import EventProcessor
        logger = _LoggerStub()
        ep = EventProcessor(logger=logger)
        def boom(_):
            raise RuntimeError('boom')
        monkeypatch.setattr(ep, '_normalize_single_event', boom)
        out = ep._normalize_events([{'name': 'x'}])
        assert out == []
        assert any('Failed to normalize event' in d for d in logger.debugs)

    def test_compute_datetime_invalid_timezone_logs_and_none(self):
        _ensure_stubs()
        from src.event_processor import EventProcessor
        logger = _LoggerStub()
        ep = EventProcessor(logger=logger)
        # patch pytz to raise
        import pytz
        def bad_tz(_):
            raise Exception('bad tz')
        pytz.timezone = bad_tz
        dt = ep._compute_datetime('2025-08-09', '09:00', 'Invalid/TZ')
        assert dt is None
        assert any('Failed to compute datetime' in d for d in logger.debugs)

    def test_deduplicate_events_logs_duplicates_removed(self):
        _ensure_stubs()
        from src.event_processor import EventProcessor
        logger = _LoggerStub()
        ep = EventProcessor(logger=logger)
        now = datetime(2025, 8, 9, 12, 0, 0)
        a = {"name": "N", "datetime": now, "detected_category": "Race"}
        b = {"name": "N", "datetime": now, "detected_category": "Race"}
        out = ep._deduplicate_events([a, b])
        assert len(out) == 1
        assert any('Removed' in d for d in logger.debugs)
