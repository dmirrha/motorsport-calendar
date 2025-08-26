"""AI package: embeddings service and related utilities.

Phase 1 provides a fully offline embeddings service based on hashing features,
with LRU in-memory cache and optional disk persistence.
"""

from .embeddings_service import EmbeddingsService, EmbeddingsConfig  # noqa: F401
