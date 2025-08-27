import hashlib
import math
import pytest

from src.category_detector import CategoryDetector


class StubEmbeddingsService:
    """
    Serviço de embeddings determinístico e local para testes.
    - Usa one-hot por índice derivado de md5(normalized_text) % dim.
    - Determinístico entre chamadas e estável no processo.
    """
    def __init__(self, dim: int = 8192, logger=None, config=None):
        self.dim = dim
        self.logger = logger
        self.config = config

    def embed_texts(self, texts):
        vectors = []
        for t in texts:
            # Fallback para strings vazias
            text = t or ""
            idx = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16) % self.dim
            vec = [0.0] * self.dim
            vec[idx] = 1.0
            vectors.append(vec)
        return vectors


def _patch_embeddings_service(detector: CategoryDetector, monkeypatch, dim: int = 8192):
    """Monkeypatch para injetar o StubEmbeddingsService no detector."""
    def _fake_ensure():
        detector._embeddings_service = StubEmbeddingsService(dim=dim, logger=detector.logger, config=detector.config)
        return True

    monkeypatch.setattr(detector, "_ensure_embeddings_service", _fake_ensure)


@pytest.mark.unit
def test_detect_categories_batch_semantic_with_stub(monkeypatch):
    detector = CategoryDetector(config_manager=None, logger=None)
    detector.ai_enabled = True

    # Injeta serviço de embeddings stub
    _patch_embeddings_service(detector, monkeypatch)

    # Eventos de teste: um com raw_category (não combina contexto) e outro sem (usa nome simples)
    events = [
        {"raw_category": "F1", "name": "Some Event", "source": "test"},
        {"name": "Grand Prix", "source": "test"},
    ]

    results = detector.detect_categories_batch(events)

    assert isinstance(results, list)
    assert len(results) == 2

    # 1) Deve detectar semanticamente F1 (raw_category preserva texto, label "f1" existe nas referências)
    r0 = results[0]
    assert r0["source"] == "semantic"
    assert r0["category"] == "F1"
    assert 0.0 <= r0["confidence"] <= 1.0

    # 2) Para "Grand Prix", variação está mapeada para F1; com embeddings determinísticos, labels e batch coincidem
    r1 = results[1]
    assert r1["source"] == "semantic"
    assert r1["category"] == "F1"
    assert r1["confidence"] >= detector.ai_category_threshold


@pytest.mark.unit
def test_detect_categories_batch_ai_enabled_but_no_service_fallbacks_to_heuristic():
    detector = CategoryDetector(config_manager=None, logger=None)
    detector.ai_enabled = True  # habilita caminho AI, mas não haverá serviço disponível

    # Não injeta serviço; import dinâmico deve falhar e cair para heurística
    events = [
        {"raw_category": "MotoGP", "name": "Some Moto Event", "source": "test"},
    ]

    results = detector.detect_categories_batch(events)
    assert len(results) == 1

    r0 = results[0]
    # Heurística preserva match exato e marca fonte adequada
    assert r0["source"] == "pattern_matching"
    assert r0["category"] == "MotoGP"
    assert math.isclose(r0["confidence"], 1.0, rel_tol=1e-6)
