import hashlib
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.preprocessing import normalize

from .cache import LRUCache, DiskCache, CombinedCache, CacheConfig


logger = logging.getLogger(__name__)


@dataclass
class EmbeddingsConfig:
    # Core
    enabled: bool = False
    device: str = "cpu"  # 'auto'|'cpu'|'cuda'|'mps' (sklearn backend usa CPU)
    batch_size: int = 16

    # Embeddings sub-config
    backend: str = "hashing"  # 'hashing' (fase 1, 100% offline)
    dim: int = 256
    lru_capacity: int = 10000

    # Cache (diretório e TTL vêm da seção ai.cache)
    cache_dir: Path = Path("cache/embeddings")
    ttl_days: int = 30


class EmbeddingsService:
    def __init__(self, cfg: EmbeddingsConfig):
        self.cfg = cfg
        # Ajustes e validações
        self.cfg.dim = max(1, int(self.cfg.dim))
        self.cfg.batch_size = max(1, int(self.cfg.batch_size))
        self.cfg.lru_capacity = max(1, int(self.cfg.lru_capacity))

        # Cache (memória + disco)
        db_path = Path(self.cfg.cache_dir) / "embeddings_cache.sqlite"
        memory = LRUCache(self.cfg.lru_capacity)
        disk = DiskCache(db_path=db_path, ttl_days=self.cfg.ttl_days)
        self.cache = CombinedCache(memory=memory, disk=disk)

        # Métricas simples
        self.metrics = {
            "batch_latencies_ms": [],
            "cache_hits": 0,
            "cache_misses": 0,
        }

        # Backend
        if self.cfg.backend != "hashing":
            logger.warning(
                "Backend '%s' não suportado nesta fase. Usando 'hashing'.",
                self.cfg.backend,
            )
        self.backend = "hashing"
        self._init_hashing_backend()

        logger.info(
            "EmbeddingsService iniciado (backend=%s, dim=%d, batch_size=%d, cache_dir=%s)",
            self.backend,
            self.cfg.dim,
            self.cfg.batch_size,
            str(self.cfg.cache_dir),
        )

    def _init_hashing_backend(self):
        # HashingVectorizer não precisa de fit; determinístico e 100% offline
        self.vectorizer = HashingVectorizer(
            n_features=self.cfg.dim,
            alternate_sign=True,
            norm=None,  # normalização manual após transform
            ngram_range=(1, 2),
            analyzer="word",
            lowercase=True,
            stop_words=None,
        )

    def _key_for(self, text: str) -> str:
        # A chave inclui backend e dim para evitar colisão de versões/configs
        base = f"{self.backend}:{self.cfg.dim}:".encode("utf-8")
        return hashlib.sha256(base + text.encode("utf-8")).hexdigest()

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        X = self.vectorizer.transform(texts)  # sparse matrix
        X = normalize(X, norm="l2", axis=1, copy=False)
        # Converte para denso apenas para retorno (dim típico pequeno p/ fase 1)
        dense = X.toarray().astype(np.float32)
        return [row.tolist() for row in dense]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para uma lista de textos.
        - Usa cache (memória+disco) por item
        - Faz batching para os misses
        - Retorna na mesma ordem dos textos de entrada
        """
        if texts is None:
            texts = []
        if not isinstance(texts, list):
            raise TypeError("texts deve ser uma lista de strings")

        # Primeiro tenta recuperar do cache
        results: List[Optional[List[float]]] = [None] * len(texts)
        to_compute: List[Tuple[int, str]] = []
        for i, t in enumerate(texts):
            t = "" if t is None else str(t)
            k = self._key_for(t)
            v = self.cache.get(k)
            if v is not None:
                results[i] = v
            else:
                to_compute.append((i, t))

        # Métricas de cache
        self.metrics["cache_hits"] += self.cache.hits
        self.metrics["cache_misses"] += self.cache.misses
        # zera contadores internos para medição por chamada
        self.cache.hits = 0
        self.cache.misses = 0

        # Processa em lotes os itens faltantes
        for start in range(0, len(to_compute), self.cfg.batch_size):
            chunk = to_compute[start : start + self.cfg.batch_size]
            batch_indices = [idx for idx, _ in chunk]
            batch_texts = [t for _, t in chunk]
            t0 = time.time()
            batch_vecs = self._embed_batch(batch_texts)
            latency_ms = (time.time() - t0) * 1000.0
            self.metrics["batch_latencies_ms"].append(latency_ms)

            # Salva no cache e no resultado
            for idx, vec, text in zip(batch_indices, batch_vecs, batch_texts):
                k = self._key_for(text)
                self.cache.put(k, vec)
                results[idx] = vec

        # Por segurança, substitui qualquer None por vetor zero (não deve ocorrer)
        zero = [0.0] * self.cfg.dim
        return [r if r is not None else zero for r in results]


__all__ = [
    "EmbeddingsConfig",
    "EmbeddingsService",
]
