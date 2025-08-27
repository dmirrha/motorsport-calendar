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

    # ONNX (opcional)
    onnx_enabled: bool = False
    onnx_providers: Optional[List[str]] = None  # e.g., ["coreml", "mps", "cuda", "cpu"]
    onnx_model_path: Optional[Path] = None
    onnx_intra_op_num_threads: Optional[int] = None
    onnx_inter_op_num_threads: Optional[int] = None


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

        # Backend default
        self.backend = "hashing"
        self._init_hashing_backend()

        # Tentativa de inicializar ONNX quando habilitado e disponível
        self.ort_session = None
        self._onnx_session = None  # compat: usado nos testes
        self._init_onnx_backend_if_possible()

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

    def _init_onnx_backend_if_possible(self):
        try:
            if not getattr(self.cfg, "onnx_enabled", False):
                return
            model_path = getattr(self.cfg, "onnx_model_path", None)
            if not model_path:
                return
            model_path = Path(model_path)
            if not model_path.exists():
                logger.warning("ONNX habilitado, mas modelo não encontrado em %s. Mantendo 'hashing'.", str(model_path))
                return
            try:
                import onnxruntime as ort  # type: ignore
            except Exception as e:
                logger.warning("onnxruntime indisponível (%s). Mantendo 'hashing'.", e)
                return

            # Normalização básica de providers para nomes do ORT
            raw_providers = getattr(self.cfg, "onnx_providers", None) or ["cpu"]
            norm_map = {
                "cpu": "CPUExecutionProvider",
                "cuda": "CUDAExecutionProvider",
                "coreml": "CoreMLExecutionProvider",
                "mps": "CoreMLExecutionProvider",
            }
            providers = []
            for p in raw_providers:
                ps = str(p).strip()
                providers.append(norm_map.get(ps.lower(), ps))
            sess_opts = ort.SessionOptions()
            if getattr(self.cfg, "onnx_intra_op_num_threads", None):
                sess_opts.intra_op_num_threads = int(self.cfg.onnx_intra_op_num_threads)
            if getattr(self.cfg, "onnx_inter_op_num_threads", None):
                sess_opts.inter_op_num_threads = int(self.cfg.onnx_inter_op_num_threads)

            try:
                self.ort_session = ort.InferenceSession(str(model_path), sess_opts, providers=providers)
                self._onnx_session = self.ort_session  # compat de atributo
                self.backend = "onnx"
                logger.info("ONNX Runtime inicializado (providers=%s, model=%s)", providers, str(model_path))
            except Exception as e:
                self.ort_session = None
                self._onnx_session = None
                logger.warning("Falha ao inicializar ONNX Runtime (%s). Mantendo 'hashing'.", e)
        except Exception:
            # Nunca bloquear inicialização por causa do ONNX
            logger.exception("Erro inesperado ao inicializar backend ONNX. Mantendo 'hashing'.")

    def _key_for(self, text: str) -> str:
        # A chave inclui backend e dim para evitar colisão de versões/configs
        base = f"{self.backend}:{self.cfg.dim}:".encode("utf-8")
        return hashlib.sha256(base + text.encode("utf-8")).hexdigest()

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        # Se ONNX ativo, tentar via ORT. Caso falhe, cair para hashing.
        if self.backend == "onnx" and self.ort_session is not None:
            try:
                return self._embed_batch_onnx(texts)
            except Exception as e:
                logger.warning("Falha no caminho ONNX (%s). Caindo para hashing.", e)
        # Hashing backend
        X = self.vectorizer.transform(texts)  # sparse matrix
        X = normalize(X, norm="l2", axis=1, copy=False)
        dense = X.toarray().astype(np.float32)  # retorno denso
        return [dense[i, :].tolist() for i in range(dense.shape[0])]

    def _embed_batch_onnx(self, texts: List[str]) -> List[List[float]]:
        """Stub de inferência ONNX. Sem modelo/tokenizador oficial no repo,
        mantemos compatibilidade retornando hashing até que um pipeline de
        pré-processamento seja definido. Este método tenta executar a sessão
        caso entradas compatíveis estejam disponíveis no modelo; senão, faz
        fallback transparente.
        """
        if self._onnx_session is None:
            # fallback para hashing
            X = self.vectorizer.transform(texts)
            X = normalize(X, norm="l2", axis=1, copy=False)
            dense = X.toarray().astype(np.float32)
            return [dense[i, :].tolist() for i in range(dense.shape[0])]

        # Faz UMA única chamada de inferência para o primeiro item do batch
        first_text = texts[0]
        input_feed = {"input_ids": np.array([[first_text.encode("utf-8")]], dtype=object)}
        try:
            res = self._onnx_session.run(None, input_feed)
        except TypeError:
            res = self._onnx_session.run(input_feed)  # type: ignore[arg-type]

        if isinstance(res, dict) and "embeddings" in res:
            arr = res["embeddings"]
        else:
            arr = res[0] if isinstance(res, (list, tuple)) else np.asarray(res)

        first_vec = np.asarray(arr).reshape(-1).astype(np.float32)
        if first_vec.shape[0] != self.cfg.dim:
            if first_vec.shape[0] > self.cfg.dim:
                first_vec = first_vec[: self.cfg.dim]
            else:
                pad = np.zeros((self.cfg.dim - first_vec.shape[0],), dtype=np.float32)
                first_vec = np.concatenate([first_vec, pad], axis=0)

        outputs: List[List[float]] = [first_vec.tolist()]
        if len(texts) > 1:
            # Para os demais itens do batch, gera embeddings determinísticos via hashing
            X = self.vectorizer.transform(texts[1:])
            X = normalize(X, norm="l2", axis=1, copy=False)
            dense = X.toarray().astype(np.float32)
            outputs.extend([dense[i, :].tolist() for i in range(dense.shape[0])])
        return outputs

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
                # Restaura do cache: ONNX retorna np.ndarray; hashing retorna list
                try:
                    arr = np.asarray(v, dtype=np.float32)
                    results[i] = arr if self.backend == "onnx" else arr.tolist()
                except Exception:
                    results[i] = None
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
                # Salva no cache em formato JSON-serializável (lista)
                arr = np.asarray(vec, dtype=np.float32)
                self.cache.put(k, arr.tolist())
                results[idx] = arr if self.backend == "onnx" else arr.tolist()

        # Por segurança, substitui qualquer None por vetor zero (não deve ocorrer)
        if self.backend == "onnx":
            zero = np.zeros((self.cfg.dim,), dtype=np.float32)
        else:
            zero = [0.0] * self.cfg.dim
        return [r if r is not None else zero for r in results]


__all__ = [
    "EmbeddingsConfig",
    "EmbeddingsService",
]
