import pytest

from src.category_detector import CategoryDetector

pytestmark = pytest.mark.integration


def test_category_exact_match_formula1():
    det = CategoryDetector()
    cat, score, meta = det.detect_category("Formula 1")
    assert cat == "F1"
    assert score >= 0.99
    assert meta.get("category_type") == "cars"


def test_category_exact_match_endurance_pt():
    det = CategoryDetector()
    cat, score, _ = det.detect_category("Campeonato Mundial de Endurance")
    # Variação mapeada para WEC
    assert cat == "WEC"
    assert score >= 0.9


def test_category_unknown_low_confidence():
    det = CategoryDetector()
    cat, score, _ = det.detect_category("Beach Volleyball Finals 2025")
    # Não garante Unknown, mas a confiança deve ser inferior ao threshold padrão (0.7)
    assert score < det.confidence_threshold
