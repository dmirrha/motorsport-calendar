import pytest

from category_detector import CategoryDetector


class LoggerStub:
    def __init__(self):
        self.debug_calls = []
        self.info_calls = []
        self.error_calls = []

    def debug(self, msg):
        self.debug_calls.append(msg)

    def info(self, msg):
        self.info_calls.append(msg)

    def error(self, msg, exc_info=False):
        self.error_calls.append((msg, exc_info))


class ConfigStub:
    def __init__(self, custom_maps=None, custom_types=None, threshold=0.7, learning=True):
        self._maps = custom_maps or {}
        self._types = custom_types or {}
        self._threshold = threshold
        self._learning = learning

    def get_category_confidence_threshold(self):
        return self._threshold

    def is_learning_mode_enabled(self):
        return self._learning

    def get(self, key, default=None):
        if key == "category_mapping.custom_mappings":
            return self._maps
        if key == "category_mapping.type_classification":
            return self._types
        return default


def test_conflicting_exact_variation_prefers_first_in_order():
    # Cria conflito: adiciona variation "formula one" a outra categoria (MotoGP)
    custom_maps = {
        "MotoGP": ["Formula One"],
    }
    det = CategoryDetector(config_manager=ConfigStub(custom_maps=custom_maps), logger=LoggerStub())

    cat, score, meta = det.detect_category("Formula One", source="feedX")
    # Deve preferir F1 (ordem de definição original) e não MotoGP
    assert cat == "F1"
    assert score == 1.0
    assert meta["best_match"] in ("Formula One", "formula one")


def test_summary_aggregates_counts_sources_and_confidence_average():
    det = CategoryDetector(logger=LoggerStub())

    # Executa detecções em múltiplas fontes
    det.detect_category("Formula One", source="feedA")
    det.detect_category("Formula One", source="feedB")
    det.detect_category("Moto GP", source="feedA")

    summary = det.get_detected_categories_summary()

    assert "F1" in summary
    assert summary["F1"]["event_count"] >= 2
    assert set(summary["F1"]["sources"]) >= {"feedA", "feedB"}
    # Como os dois matches são perfeitos, média deve ser 1.0
    assert summary["F1"]["confidence"] == pytest.approx(1.0, rel=1e-6)

    # MotoGP aparece ao menos uma vez
    assert "MotoGP" in summary
    assert summary["MotoGP"]["event_count"] >= 1


def test_custom_mappings_and_types_are_merged_and_used():
    custom_maps = {
        "Karting": ["Super Kart"],
    }
    custom_types = {
        "Karting": "other",
    }
    det = CategoryDetector(config_manager=ConfigStub(custom_maps=custom_maps, custom_types=custom_types), logger=LoggerStub())

    cat, score, meta = det.detect_category("Super Kart", source="feedC")
    assert cat == "Karting"
    assert score >= det.confidence_threshold
    # Verifica tipo aplicado via custom types
    assert meta.get("category_type") == "other"
