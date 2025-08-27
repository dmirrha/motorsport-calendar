"""
Serviço de embeddings OFFLINE leve baseado em hashing de n-gramas.

Objetivo: fornecer uma implementação local, sem dependências externas, para
habilitar a integração semântica do `CategoryDetector` quando `ai.enabled=true`.

Interface esperada pelo `CategoryDetector`:
- Classe: EmbeddingsService(config, logger)
- Método: embed_texts(texts: List[str]) -> List[List[float]]

Notas:
- Implementa vetorização por hashing de n-gramas de caracteres (bag-of-char-ngrams).
- Normaliza cada vetor para norma L2 = 1.0, possibilitando uso com similaridade do cosseno.
- Respeita `ai.batch_size` (utilizado apenas para logging e processamento em chunks).
- Inclui cache em memória por processo para acelerar textos repetidos durante a execução.
"""
from __future__ import annotations

import math
import time
import logging
from typing import Any, Dict, List, Optional, Tuple


class EmbeddingsService:
    """Implementação simples de embeddings via hashing de n-gramas.

    Parâmetros de configuração relevantes (se existirem):
    - ai.batch_size: int (default 16)
    - ai.cache.enabled: bool (default True) [neste serviço apenas cache em memória]
    - ai.cache.ttl_days: int (ignorado nesta implementação simples)
    - ai.device: str (ignorado, sem aceleração nesta versão)
    - ai.onnx.enabled/provider: ignorados nesta versão.
    """

    def __init__(self, config: Optional[Any] = None, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or logging.getLogger(__name__)
        self.config = config

        # Parâmetros
        self.batch_size: int = 16
        try:
            if self.config:
                # config pode ser um ConfigManager ou dict com get
                get = getattr(self.config, "get", None)
                if callable(get):
                    self.batch_size = int(self.config.get("ai.batch_size", 16))
                else:
                    # tenta acessar como dict
                    ai = (self.config.get("ai") if isinstance(self.config, dict) else None) or {}
                    self.batch_size = int(ai.get("batch_size", 16))
        except Exception:
            # fallback silencioso
            self.batch_size = 16

        # Hiperparâmetros simples para hashing
        self.dim: int = 384  # dimensão do vetor (compatível com uso leve)
        self.min_n: int = 3  # n-gram mínimo
        self.max_n: int = 5  # n-gram máximo
        self._cache: Dict[str, List[float]] = {}

        self.logger.info(
            f"[EmbeddingsService] Inicializado (dim={self.dim}, ngrams={self.min_n}-{self.max_n}, batch_size={self.batch_size})"
        )

    # ----------------------
    # API pública
    # ----------------------
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para uma lista de textos.

        - Normaliza entradas nulas para string vazia.
        - Usa cache em memória para textos idênticos no mesmo processo.
        - Processa em pequenos batches para logs e eventual evolução futura.
        """
        if texts is None:
            return []

        start = time.time()
        outputs: List[List[float]] = []

        # Processamento em chunks
        bs = max(1, int(self.batch_size))
        total = len(texts)
        for i in range(0, total, bs):
            chunk = texts[i : i + bs]
            for t in chunk:
                s = (t or "").strip()
                # Cache in-memory
                if s in self._cache:
                    outputs.append(self._cache[s])
                    continue
                vec = self._hash_embed(s)
                self._cache[s] = vec
                outputs.append(vec)

        dur_ms = (time.time() - start) * 1000.0
        try:
            self.logger.debug(
                f"[EmbeddingsService] embed_texts: {len(texts)} itens em {dur_ms:.1f} ms (batch_size={bs})"
            )
        except Exception:
            pass
        return outputs

    # ----------------------
    # Implementação interna
    # ----------------------
    def _hash_embed(self, text: str) -> List[float]:
        """Converte texto em vetor por hashing de n-gramas e normalização L2."""
        # Gera contagem de n-gramas com hashing em dimensão fixa
        vec = [0.0] * self.dim
        if not text:
            return vec

        # Normalização simples
        s = text.lower()

        # Extração de n-gramas de caracteres
        for n in range(self.min_n, self.max_n + 1):
            if len(s) < n:
                continue
            for j in range(len(s) - n + 1):
                ngram = s[j : j + n]
                h = self._stable_hash(ngram)
                idx = h % self.dim
                vec[idx] += 1.0

        # TF-like log scaling opcional + normalização L2
        for k in range(self.dim):
            if vec[k] > 0.0:
                vec[k] = 1.0 + math.log(1.0 + vec[k])

        self._l2_normalize(vec)
        return vec

    @staticmethod
    def _stable_hash(s: str) -> int:
        """Hash estável independente da execução (diferente de hash() nativo do Python)."""
        # FNV-1a 64-bit
        h = 1469598103934665603
        fnv_prime = 1099511628211
        for ch in s:
            h ^= ord(ch)
            h = (h * fnv_prime) & 0xFFFFFFFFFFFFFFFF
        return h

    @staticmethod
    def _l2_normalize(vec: List[float]) -> None:
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            inv = 1.0 / norm
            for i in range(len(vec)):
                vec[i] *= inv
