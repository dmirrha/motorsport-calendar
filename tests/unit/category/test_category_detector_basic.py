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


def test_normalize_text_removes_noise_and_accents():
    det = CategoryDetector(logger=LoggerStub())
    raw = "Fórmula 1 - World Championship!"
    norm = det.normalize_text(raw)
    # Remove acentos, pontuação e palavras de ruído definidas no código
    assert norm == "formula 1"


def test_detect_exact_match_formula_one():
    det = CategoryDetector(logger=LoggerStub())
    cat, score, meta = det.detect_category("Formula One")
    assert cat == "F1"
    assert score == 1.0
    assert isinstance(meta, dict)
    assert meta.get("best_match") is not None


def test_detect_empty_returns_unknown():
    det = CategoryDetector(logger=LoggerStub())
    cat, score, meta = det.detect_category("")
    assert cat == "Unknown"
    assert score == 0.0
    assert meta.get("raw_text") == ""


def test_detect_wsbk_variation_world_superbike():
    det = CategoryDetector(logger=LoggerStub())
    # Normalização remove 'world' dos dois lados e iguala para 'superbike' → match perfeito
    cat, score, meta = det.detect_category("World Superbike")
    assert cat == "WSBK"
    assert score == 1.0


def test_learning_variation_when_similarity_high_but_not_perfect():
    det = CategoryDetector(logger=LoggerStub())
    # Espera-se similaridade alta, porém < 1.0, para acionar aprendizado
    raw = "Formule 1"  # variação próxima de "Formula 1"
    cat, score, meta = det.detect_category(raw)
    assert cat == "F1"
    assert 0.7 <= score < 1.0  # threshold padrão é 0.7
    # Deve registrar variação aprendida
    assert "F1" in det.learned_variations
    assert any(item.get("variation") == raw for item in det.learned_variations["F1"])


def test_statistics_after_multiple_detections():
    det = CategoryDetector(logger=LoggerStub())
    inputs = ["Formula One", "Moto GP", "Stock Car Brasil", "Unknown Foo"]
    for t in inputs:
        det.detect_category(t)

    stats = det.get_statistics()
    assert isinstance(stats, dict)
    assert stats.get("total_detections", 0) >= len(inputs)
    assert isinstance(stats.get("categories_detected", []), list)
    assert stats.get("learning_enabled") is True
    assert pytest.approx(stats.get("confidence_threshold", 0.0), rel=1e-3) == det.confidence_threshold
