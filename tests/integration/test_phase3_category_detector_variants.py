import json
import pytest

from src.category_detector import CategoryDetector

pytestmark = pytest.mark.integration


class _StubConfig:
    def __init__(self, threshold=0.7, learning=True, custom=None, types=None):
        self._thr = threshold
        self._learn = learning
        self._custom = custom or {}
        self._types = types or {}

    def get_category_confidence_threshold(self):
        return self._thr

    def is_learning_mode_enabled(self):
        return self._learn

    def get(self, key, default=None):
        if key == 'category_mapping.custom_mappings':
            return self._custom
        if key == 'category_mapping.type_classification':
            return self._types
        return default


# --- Núcleo do detector -----------------------------------------------------

def test_noise_and_accent_for_f1_and_wec():
    det = CategoryDetector()

    cat1, score1, meta1 = det.detect_category("Fórmula-1!!! Grand Prix")
    assert cat1 == "F1"
    assert score1 >= det.confidence_threshold
    assert meta1.get("category_type") == "cars"

    cat2, score2, meta2 = det.detect_category("Campeonato de Endurânce (WEC)")
    # deve mapear para WEC
    assert cat2 == "WEC"
    assert score2 >= det.confidence_threshold
    assert meta2.get("category_type") in {"cars", "mixed"}


def test_jaro_winkler_typo_formula1():
    det = CategoryDetector()
    # erro de digitação propositado
    cat, score, _ = det.detect_category("formla 1 world gp")
    assert cat == "F1"
    assert score >= det.confidence_threshold


def test_unknown_other_sport_low_conf():
    det = CategoryDetector()
    cat, score, _ = det.detect_category("FIFA World Cup Finals")
    assert score < det.confidence_threshold


# --- Aprendizado dinâmico ---------------------------------------------------

def test_learning_enabled_adds_variation_and_persists(tmp_path):
    cfg = _StubConfig(learning=True)
    det = CategoryDetector(config_manager=cfg)

    # texto não mapeado literalmente, mas muito próximo de F1
    raw = "formlua onne"
    cat, score, _ = det.detect_category(raw)
    assert cat == "F1"
    assert score >= det.confidence_threshold

    # deve ter aprendido a variação
    assert "F1" in det.learned_variations
    assert any(v["variation"] == raw for v in det.learned_variations["F1"]) \
        or any(v.get("variation") == raw for v in det.learned_variations["F1"])

    # salvar e recarregar em nova instância
    fpath = tmp_path / "learned.json"
    det.save_learned_categories(str(fpath))

    det2 = CategoryDetector()
    det2.load_learned_categories(str(fpath))

    # após carregar, a nova variação deve estar nos mappings efetivos
    assert any(raw == v for v in det2.category_mappings.get("F1", []))


def test_learning_disabled_does_not_add_variation():
    cfg = _StubConfig(learning=False)
    det = CategoryDetector(config_manager=cfg)

    raw = "formlua onne"
    cat, score, _ = det.detect_category(raw)
    assert cat == "F1"
    assert score >= det.confidence_threshold

    # não deve aprender quando learning desabilitado
    assert "F1" not in det.learned_variations or not det.learned_variations["F1"]
    assert raw not in det.category_mappings.get("F1", [])


# --- Mapeamentos customizados ----------------------------------------------

def test_custom_mappings_and_type_classification():
    # usar um termo único que não colida com mapeamentos padrão
    custom = {"FuscaSeries": ["fusca cup", "fusca"]}
    types = {"vintage": ["FuscaSeries"]}
    cfg = _StubConfig(custom=custom, types=types)

    det = CategoryDetector(config_manager=cfg)

    cat, score, meta = det.detect_category("Fusca Cup")
    assert cat == "FuscaSeries"
    assert score >= det.confidence_threshold
    assert meta.get("category_type") == "vintage"


# --- Processamento em lote --------------------------------------------------

def test_batch_detect_categories_enrichment():
    det = CategoryDetector()
    events = [
        {"name": "Bahrain Grand Prix", "raw_category": "Formula 1", "source": "siteA"},
        {"name": "24 Hours of Le Mans", "raw_category": "Le mans", "source": "siteB"},
    ]

    out = det.batch_detect_categories(events)
    assert len(out) == 2

    for ev in out:
        assert "category" in ev and ev["category"] != ""
        assert "category_type" in ev
        assert "category_confidence" in ev and isinstance(ev["category_confidence"], float)
        assert "raw_category_text" in ev
        assert "category_metadata" in ev and isinstance(ev["category_metadata"], dict)


def test_detect_categories_batch_fallback_combination():
    det = CategoryDetector()
    events = [
        {"name": "GT World Challenge Europe", "raw_category": "", "source": "siteC"},
        {"name": "Grand Prix of Spain", "raw_category": "MotoGP", "source": "siteD"},
        {"name": "Indy 500", "raw_category": "indi car", "source": "siteE"},
    ]

    results = det.detect_categories_batch(events)
    assert len(results) == 3

    cats = [r["category"] for r in results]
    assert any(c in cats for c in ["GTWorldChallenge"])  # primeiro
    assert any(c in cats for c in ["MotoGP"])            # segundo
    assert any(c in cats for c in ["IndyCar"])           # terceiro


# --- Filtro e estatísticas --------------------------------------------------

def test_filter_by_confidence():
    det = CategoryDetector()
    events = [
        {"name": "A", "category_confidence": 0.9},
        {"name": "B", "category_confidence": det.confidence_threshold},
        {"name": "C", "category_confidence": det.confidence_threshold - 0.01},
    ]

    out = det.filter_by_confidence(events)
    names = [e["name"] for e in out]
    assert "A" in names and "B" in names and "C" not in names


def test_get_detected_categories_summary_aggregation():
    det = CategoryDetector()

    # gerar estatísticas com fontes distintas
    det.detect_category("Formula 1", source="site1")
    det.detect_category("Fórmula 1", source="site2")
    det.detect_category("moto gp", source="site1")

    summary = det.get_detected_categories_summary()
    assert "F1" in summary and "MotoGP" in summary

    f1 = summary["F1"]
    assert f1["event_count"] >= 2
    assert set(f1["sources"]).issuperset({"site1", "site2"})
    assert f1["confidence"] > 0.0


# --- Persistência -----------------------------------------------------------

def test_save_and_load_learned_categories_roundtrip(tmp_path):
    det = CategoryDetector()

    # forçar aprendizado com variação próxima
    raw = "formula e prix"
    cat, score, _ = det.detect_category(raw)
    # pode detectar FormulaE por similaridade
    assert cat in {"FormulaE", "F1", "F2", "F3", "F4"}

    # somente aprende quando acima do threshold
    if score >= det.confidence_threshold and cat != "Unknown":
        assert any(cat == k for k in det.category_mappings)
        # salvar e recarregar
        f = tmp_path / "learned_round.json"
        det.save_learned_categories(str(f))

        det2 = CategoryDetector()
        det2.load_learned_categories(str(f))
        # ao menos manter estrutura
        assert isinstance(det2.learned_variations, dict)
        # se aprendeu, presença nos mappings
        if cat in det.learned_variations:
            for v in det.learned_variations.get(cat, []):
                assert v.get("variation") in det2.category_mappings.get(cat, [])
