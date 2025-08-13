import json
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


def test_save_and_load_learned_categories(tmp_path):
    logger = LoggerStub()
    det = CategoryDetector(logger=logger)

    # Gera uma variação aprendida
    raw = "Formule 1"  # similar a F1, não perfeita
    cat, score, meta = det.detect_category(raw)
    assert cat == "F1"
    assert 0.0 <= score < 1.0
    assert "F1" in det.learned_variations

    # Salva em arquivo temporário
    fp = tmp_path / "learned.json"
    det.save_learned_categories(str(fp))
    assert fp.exists()

    # Verifica conteúdo salvo
    data = json.loads(fp.read_text("utf-8"))
    assert "learned_variations" in data
    assert "updated_mappings" in data
    assert "F1" in data["learned_variations"]
    assert any(item.get("variation") == raw for item in data["learned_variations"]["F1"])

    # Novo detector deve carregar e mesclar
    det2 = CategoryDetector(logger=LoggerStub())
    assert raw not in det2.category_mappings.get("F1", [])

    det2.load_learned_categories(str(fp))
    assert "F1" in det2.learned_variations
    assert any(item.get("variation") == raw for item in det2.learned_variations["F1"])
    assert raw in det2.category_mappings.get("F1", [])


def test_load_learned_categories_missing_file(tmp_path):
    det = CategoryDetector(logger=LoggerStub())
    missing = tmp_path / "does_not_exist.json"

    # Não deve lançar erro e não altera estado
    before_learned = dict(det.learned_variations)
    before_map = {k: list(v) for k, v in det.category_mappings.items()}

    det.load_learned_categories(str(missing))

    assert det.learned_variations == before_learned
    # Verifica que os mapeamentos não foram alterados
    for k, v in before_map.items():
        assert det.category_mappings.get(k, [])[: len(v)] == v
