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
    def __init__(self, threshold=0.7, learning=True):
        self._threshold = threshold
        self._learning = learning

    def get_category_confidence_threshold(self):
        return self._threshold

    def is_learning_mode_enabled(self):
        return self._learning

    def get(self, key, default=None):
        # Suporta chamadas do detector a chaves opcionais de mapeamento/tipagem
        if key in ("category_mapping.custom_mappings", "category_mapping.type_classification"):
            return {}
        return default


@pytest.mark.parametrize(
    "threshold,learning,should_learn",
    [
        (0.7, True, True),      # threshold padrão, learning on → aprende
        (0.99, True, False),    # limiar alto impede aprendizado
        (0.7, False, False),    # learning off impede aprendizado
    ],
)
def test_learning_behavior_under_threshold_and_flag(threshold, learning, should_learn):
    logger = LoggerStub()
    cfg = ConfigStub(threshold=threshold, learning=learning)
    det = CategoryDetector(config_manager=cfg, logger=logger)

    raw = "Formule 1"  # similar a F1, mas não perfeita
    cat, score, meta = det.detect_category(raw)

    assert cat == "F1"
    assert 0.0 <= score <= 1.0

    if should_learn:
        assert "F1" in det.learned_variations
        assert any(item.get("variation") == raw for item in det.learned_variations["F1"])
    else:
        assert "F1" not in det.learned_variations or not any(
            item.get("variation") == raw for item in det.learned_variations.get("F1", [])
        )


def test_get_category_type_known_and_unknown():
    det = CategoryDetector(logger=LoggerStub())
    assert det._get_category_type("F1") == "cars"
    assert det._get_category_type("MotoGP") == "motorcycles"
    assert det._get_category_type("SomeUnknown") == "other"
