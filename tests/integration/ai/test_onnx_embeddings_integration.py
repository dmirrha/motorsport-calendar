"""Integration tests for ONNX embeddings service."""
import os
import time
from pathlib import Path

import numpy as np
import pytest
from onnxruntime import get_available_providers

from src.ai import EmbeddingsService, EmbeddingsConfig

# Skip if ONNX is not available or if explicitly disabled
pytestmark = pytest.mark.skipif(
    os.getenv("SKIP_ONNX_TESTS", "false").lower() == "true",
    reason="ONNX tests skipped via SKIP_ONNX_TESTS",
)

# Test model configuration
TEST_MODEL_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TEST_MODEL_DIR = Path("tests/data/onnx")
TEST_MODEL_PATH = TEST_MODEL_DIR / "model.onnx"


def has_gpu():
    """Check if CUDA is available."""
    return "CUDAExecutionProvider" in get_available_providers()


def has_apple_silicon():
    """Check if running on Apple Silicon."""
    import platform
    return platform.system() == "Darwin" and platform.machine() == "arm64"


@pytest.mark.integration
@pytest.mark.slow
class TestONNXEmbeddingsIntegration:
    """Integration tests for ONNX embeddings service."""

    @pytest.fixture(scope="class")
    def onnx_model_path(self):
        """Ensure ONNX model is available for testing."""
        if not TEST_MODEL_PATH.exists():
            pytest.skip(f"ONNX model not found at {TEST_MODEL_PATH}. "
                      "Run 'python scripts/eval/export_onnx.py' first.")
        return TEST_MODEL_PATH

    @pytest.fixture
    def test_texts(self):
        """Sample texts for testing."""
        return [
            "F1 Grande Prêmio do Brasil - Corrida",
            "MotoGP Argentina - Treino Livre",
            "Stock Car Brasil - Corrida em Goiânia",
            "Fórmula E - E-Prix de São Paulo",
            "WEC - 6 Horas de Spa-Francorchamps",
        ]

    def _get_providers(self):
        """Get available providers based on the current system."""
        if has_gpu():
            return ["CUDAExecutionProvider", "CPUExecutionProvider"]
        if has_apple_silicon():
            return ["CoreMLExecutionProvider", "CPUExecutionProvider"]
        return ["CPUExecutionProvider"]

    def test_onnx_embeddings_generation(self, onnx_model_path, tmp_path, test_texts):
        """Test that ONNX embeddings can be generated with the actual runtime."""
        cfg = EmbeddingsConfig(
            enabled=True,
            backend="onnx",
            onnx_enabled=True,
            onnx_model_path=str(onnx_model_path),
            onnx_providers=self._get_providers(),
            dim=384,  # Dimension for the test model
            batch_size=2,
            lru_capacity=100,
            cache_dir=tmp_path / "cache",
            ttl_days=1,
        )

        # Create service with ONNX backend
        svc = EmbeddingsService(cfg)
        
        # Generate embeddings
        start_time = time.time()
        embeddings = svc.embed_texts(test_texts)
        duration = time.time() - start_time
        
        # Basic validation
        assert len(embeddings) == len(test_texts)
        for emb in embeddings:
            assert isinstance(emb, np.ndarray)
            assert emb.shape == (cfg.dim,)
            assert emb.dtype == np.float32
        
        # Check metrics
        assert svc.metrics["cache_misses"] == len(test_texts)
        assert len(svc.metrics["batch_latencies_ms"]) == (len(test_texts) + cfg.batch_size - 1) // cfg.batch_size
        
        print(f"\nGenerated {len(test_texts)} embeddings in {duration:.3f}s "
              f"({len(test_texts)/duration:.1f} embeddings/s)")

    def test_onnx_cache_performance(self, onnx_model_path, tmp_path, test_texts):
        """Test that caching improves performance on repeated queries."""
        cfg = EmbeddingsConfig(
            enabled=True,
            backend="onnx",
            onnx_enabled=True,
            onnx_model_path=str(onnx_model_path),
            onnx_providers=self._get_providers(),
            dim=384,
            batch_size=2,
            lru_capacity=100,
            cache_dir=tmp_path / "cache",
            ttl_days=1,
        )
        
        svc = EmbeddingsService(cfg)
        
        # First run - should hit the model
        start_time = time.time()
        embeddings1 = svc.embed_texts(test_texts)
        first_run_time = time.time() - start_time
        
        # Second run - should hit cache
        start_time = time.time()
        embeddings2 = svc.embed_texts(test_texts)
        second_run_time = time.time() - start_time
        
        # Results should be the same
        for e1, e2 in zip(embeddings1, embeddings2):
            assert np.allclose(e1, e2, rtol=1e-4)
        
        # Cache should be much faster
        assert second_run_time < first_run_time / 10, \
            f"Cache not effective: {first_run_time=:.3f}s vs {second_run_time=:.3f}s"
        
        # Should have hits equal to the number of texts
        assert svc.metrics["cache_hits"] == len(test_texts)
        
        print(f"\nFirst run: {first_run_time:.3f}s, "
              f"Second run (cached): {second_run_time:.3f}s, "
              f"Speedup: {first_run_time/max(second_run_time, 1e-6):.1f}x")

    def test_onnx_batching(self, onnx_model_path, tmp_path):
        """Test that batching works as expected."""
        batch_sizes = [1, 2, 4, 8]
        results = []
        
        for batch_size in batch_sizes:
            cfg = EmbeddingsConfig(
                enabled=True,
                backend="onnx",
                onnx_enabled=True,
                onnx_model_path=str(onn_model_path),
                onnx_providers=self._get_providers(),
                dim=384,
                batch_size=batch_size,
                lru_capacity=1000,
                cache_dir=tmp_path / f"cache_{batch_size}",
                ttl_days=1,
            )
            
            # Generate more texts to see batching effects
            test_texts = [f"Test text {i} for batching" for i in range(10)]
            
            svc = EmbeddingsService(cfg)
            
            # Warmup run (ignore)
            _ = svc.embed_texts(test_texts[:1])
            
            # Time the actual run
            start_time = time.time()
            embeddings = svc.embed_texts(test_texts)
            duration = time.time() - start_time
            
            # Store results
            results.append({
                'batch_size': batch_size,
                'time': duration,
                'throughput': len(test_texts) / duration,
                'batch_count': len(svc.metrics["batch_latencies_ms"]),
            })
        
        # Print results for analysis
        print("\nBatch size performance comparison:")
        print(f"{'Batch Size':>10} | {'Time (s)':>10} | {'Texts/s':>10} | {'Batches':>7}")
        print("-" * 50)
        for r in results:
            print(f"{r['batch_size']:>10} | {r['time']:>10.3f} | "
                  f"{r['throughput']:>10.1f} | {r['batch_count']:>7}")
        
        # At least some batching should be better than no batching
        if len(results) > 1:
            best_throughput = max(r['throughput'] for r in results)
            assert results[0]['throughput'] < best_throughput * 0.9, \
                "No throughput improvement with batching"
