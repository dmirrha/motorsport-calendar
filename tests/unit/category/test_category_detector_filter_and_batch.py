import pytest

from category_detector import CategoryDetector


class LoggerStub:
    def __init__(self):
        self.debug_calls = []
        self.info_calls = []
        self.error_calls = []
        self.warning_calls = []

    def debug(self, msg):
        self.debug_calls.append(msg)

    def info(self, msg):
        self.info_calls.append(msg)

    def error(self, msg, exc_info=False):
        self.error_calls.append((msg, exc_info))

    def warning(self, msg):
        self.warning_calls.append(msg)


class ConfigStub:
    def __init__(self, threshold=0.8, learning=True):
        self._threshold = threshold
        self._learning = learning

    def get_category_confidence_threshold(self):
        return self._threshold

    def is_learning_mode_enabled(self):
        return self._learning

    def get(self, key, default=None):
        return {}


def test_filter_by_confidence_uses_default_threshold_and_logs_warnings():
    logger = LoggerStub()
    det = CategoryDetector(config_manager=ConfigStub(threshold=0.8), logger=logger)

    events = [
        {"name": "High", "category_confidence": 0.90},
        {"name": "Low", "category_confidence": 0.50},
    ]

    out = det.filter_by_confidence(events)
    assert [e["name"] for e in out] == ["High"]
    # Deve ter logado um aviso para o evento Low
    assert len(logger.warning_calls) == 1
    assert "Low" in logger.warning_calls[0]


def test_filter_by_confidence_override_min_confidence_filters_all_and_logs():
    logger = LoggerStub()
    det = CategoryDetector(config_manager=ConfigStub(threshold=0.6), logger=logger)

    events = [
        {"name": "A", "category_confidence": 0.90},
        {"name": "B", "category_confidence": 0.50},
    ]

    out = det.filter_by_confidence(events, min_confidence=0.95)
    assert out == []
    # Ambos devem ser filtrados e logados
    assert len(logger.warning_calls) == 2
    assert any("A" in msg for msg in logger.warning_calls)
    assert any("B" in msg for msg in logger.warning_calls)


def test_batch_detect_categories_updates_event_fields():
    logger = LoggerStub()
    det = CategoryDetector(logger=logger)

    events = [
        {"raw_category": "Formula One", "source": "feedA", "name": "Round 1"}
    ]

    processed = det.batch_detect_categories(events)
    assert len(processed) == 1
    ev = processed[0]

    assert ev["category"] == "F1"
    assert ev["category_type"] == "cars"
    assert ev["category_confidence"] == 1.0
    assert ev["raw_category_text"] == "Formula One"
    assert isinstance(ev["category_metadata"], dict)
    # A origem passada no batch deve aparecer no metadata
    assert ev["category_metadata"].get("source") == "feedA"


def test_detect_categories_batch_combines_name_and_handles_empty():
    logger = LoggerStub()
    det = CategoryDetector(logger=logger)

    events = [
        {"raw_category": "", "name": ""},
        {"raw_category": "Moto GP", "name": "Qatar GP"},
    ]

    res = det.detect_categories_batch(events)
    assert len(res) == 2

    # Primeiro não tem texto → Unknown com 0.0
    assert res[0]["category"] == "Unknown"
    assert res[0]["confidence"] == 0.0

    # Segundo combina texto e deve atingir ao menos o threshold
    assert res[1]["category"] == "MotoGP"
    assert res[1]["confidence"] >= det.confidence_threshold
    assert res[1]["source"] == "pattern_matching"
