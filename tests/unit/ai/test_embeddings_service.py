import math
from pathlib import Path

import numpy as np
import pytest

from src.ai import EmbeddingsService, EmbeddingsConfig


@pytest.mark.unit
def test_embeddings_determinism_and_shape(tmp_path: Path):
    cfg = EmbeddingsConfig(
        enabled=True,
        device="cpu",
        batch_size=4,
        backend="hashing",
        dim=128,
        lru_capacity=128,
        cache_dir=tmp_path / "cache",
        ttl_days=30,
    )
    svc = EmbeddingsService(cfg)

    texts = [
        "F1 Grand Prix São Paulo",
        "F1 Grand Prix São Paulo",
        "MotoGP Argentina",
        "Stock Car Brasil Goiânia",
    ]

    embs1 = svc.embed_texts(texts)
    embs2 = svc.embed_texts(texts)

    # Mesmo vetor para entradas iguais
    assert np.allclose(embs1[0], embs1[1])

    # Determinismo entre chamadas
    for a, b in zip(embs1, embs2):
        assert np.allclose(a, b)

    # Checa dimensão
    for e in embs1:
        assert len(e) == cfg.dim


@pytest.mark.unit
def test_cache_hits_and_batching(tmp_path: Path):
    cfg = EmbeddingsConfig(
        enabled=True,
        device="cpu",
        batch_size=4,
        backend="hashing",
        dim=64,
        lru_capacity=64,
        cache_dir=tmp_path / "cache",
        ttl_days=30,
    )

    # 10 itens para gerar 3 lotes (4+4+2)
    texts = [f"evento_{i}" for i in range(10)]

    svc = EmbeddingsService(cfg)
    embs1 = svc.embed_texts(texts)
    assert len(embs1) == len(texts)

    # 3 latências registradas (3 lotes)
    assert len(svc.metrics["batch_latencies_ms"]) == math.ceil(len(texts) / cfg.batch_size)

    # Segunda chamada deve ser 100% cache hit (sem novos lotes)
    before_hits = svc.metrics["cache_hits"]
    embs2 = svc.embed_texts(texts)
    assert len(embs2) == len(texts)

    # hits incrementados em N
    assert svc.metrics["cache_hits"] >= before_hits + len(texts)

    # Não deve registrar novas latências para misses (apenas se houver misses)
    after_batches = len(svc.metrics["batch_latencies_ms"])
    assert after_batches == math.ceil(len(texts) / cfg.batch_size)
