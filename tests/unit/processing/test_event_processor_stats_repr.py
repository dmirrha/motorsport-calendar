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
        sys.modules['fuzzywuzzy'] = mod

    # unidecode
    if 'unidecode' not in sys.modules:
        mod = types.ModuleType('unidecode')
        def _unidecode(s):
            return s
        mod.unidecode = _unidecode
        sys.modules['unidecode'] = mod


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


@pytest.mark.unit
class TestEventProcessorStatsRepr:
    def setup_method(self):
        _ensure_stubs()
        from src.event_processor import EventProcessor
        self.logger = _LoggerStub()
        self.ep = EventProcessor(logger=self.logger)

    def test_get_processing_statistics_returns_copy(self):
        self.ep.processing_stats['events_input'] = 5
        stats = self.ep.get_processing_statistics()
        assert stats['events_input'] == 5
        stats['events_input'] = 0
        # Original não deve mudar
        assert self.ep.processing_stats['events_input'] == 5

    def test_log_processing_summary_includes_counts_and_duration(self):
        now = datetime.now()
        self.ep.processing_stats.update({
            'events_input': 5,
            'events_validated': 4,
            'events_final': 3,
            'duplicates_removed': 1,
            'categories_detected': 5,
            'events_silent_filtered': 1,
            'processing_start_time': (now - timedelta(seconds=2)).isoformat(),
            'processing_end_time': now.isoformat(),
        })
        self.ep._log_processing_summary()
        # Verifica que houve um log de passo com resumo
        assert any('Processing Summary' in s for s in self.logger.steps)
        # Verifica que houve um debug de duração
        assert any('Processing completed in' in d for d in self.logger.debugs)

    def test_str_and_repr_format(self):
        s = str(self.ep)
        r = repr(self.ep)
        assert 'EventProcessor(' in s and 'threshold=' in s
        assert '<EventProcessor(' in r and 'time_tolerance=' in r and r.endswith('min)>')
