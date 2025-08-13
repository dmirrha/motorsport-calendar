import io
import json
import builtins
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


def test_save_and_load_learned_categories_roundtrip(tmp_path):
    logger = LoggerStub()
    det = CategoryDetector(logger=logger)

    # Gera aprendizado: similar a "Formula One" porém não exato (score < 1.0, >= threshold)
    cat, score, meta = det.detect_category("Formul One", source="feedA")
    assert cat == "F1"
    assert score < 1.0
    assert det.learned_variations

    fpath = tmp_path / "learned.json"
    det.save_learned_categories(str(fpath))

    # Novo detector sem estado, carrega o arquivo salvo
    logger2 = LoggerStub()
    det2 = CategoryDetector(logger=logger2)
    assert not det2.learned_variations

    det2.load_learned_categories(str(fpath))

    # learned_variations deve conter a variação aprendida e os mappings devem ser estendidos
    assert "F1" in det2.learned_variations
    learned_vars = [v["variation"] for v in det2.learned_variations["F1"]]
    assert any("Formul One" == v for v in learned_vars)

    assert "F1" in det2.category_mappings
    assert any(v.lower() == "formul one" for v in det2.category_mappings["F1"]) or any(
        v == "Formul One" for v in det2.category_mappings["F1"]
    )


def test_load_missing_file_no_crash(tmp_path):
    logger = LoggerStub()
    det = CategoryDetector(logger=logger)

    missing = tmp_path / "does_not_exist.json"
    det.load_learned_categories(str(missing))

    # Sem exceções e sem erros logados
    assert not logger.error_calls


def test_save_failure_logs_error(monkeypatch, tmp_path):
    logger = LoggerStub()
    det = CategoryDetector(logger=logger)

    # Força um erro em open() durante escrita
    def boom(*args, **kwargs):
        raise IOError("disk full")

    monkeypatch.setattr(builtins, "open", boom)

    det.save_learned_categories(str(tmp_path / "out.json"))

    assert logger.error_calls
    msg, exc_info = logger.error_calls[-1]
    assert "Failed to save learned categories" in msg


def test_load_invalid_json_logs_error(tmp_path):
    logger = LoggerStub()
    det = CategoryDetector(logger=logger)

    bad = tmp_path / "bad.json"
    bad.write_text("{ not: json }", encoding="utf-8")

    det.load_learned_categories(str(bad))

    assert logger.error_calls
    msg, exc_info = logger.error_calls[-1]
    assert "Failed to load learned categories" in msg


def test_get_statistics_values():
    logger = LoggerStub()
    det = CategoryDetector(logger=logger)

    # 3 detecções em 2 fontes e 2 categorias.
    det.detect_category("Formula One", source="feedA")
    det.detect_category("Moto GP", source="feedB")
    # Gera uma variação aprendida
    det.detect_category("Formul One", source="feedA")

    stats = det.get_statistics()

    # total de detecções = 3
    assert stats["total_detections"] == 3

    # categorias únicas >= 2 (F1 e MotoGP)
    assert stats["unique_categories"] >= 2
    assert set(stats["categories_detected"]) >= {"F1", "MotoGP"}

    # pelo menos uma variação aprendida
    assert stats["learned_variations"] >= 1

    # duas fontes processadas
    assert stats["sources_processed"] >= 2

    # flags configuradas
    assert stats["confidence_threshold"] == det.confidence_threshold
    assert stats["learning_enabled"] is True
