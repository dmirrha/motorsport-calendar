import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import numpy as np
import pytest
from onnxruntime import InferenceSession, SessionOptions

from src.ai import EmbeddingsService, EmbeddingsConfig

# Skip if ONNX dependencies are not available
pytestmark = pytest.mark.skipif(
    os.getenv("SKIP_ONNX_TESTS", "false").lower() == "true",
    reason="ONNX tests skipped via SKIP_ONNX_TESTS",
)

# Test model path for ONNX (will be mocked)
TEST_MODEL_PATH = "tests/data/onnx/test_model.onnx"


def create_mock_onnx_session():
    """Create a mock ONNX session that returns deterministic embeddings."""
    mock_session = MagicMock(spec=InferenceSession)
    
    # Mock run() to return deterministic embeddings based on input text
    def mock_run(_, input_feed):
        # Simple deterministic hash-based embedding for testing
        input_text = input_feed["input_ids"][0][0].decode('utf-8')
        seed = sum(ord(c) for c in input_text) % (2**32)
        np.random.seed(seed)
        return {"embeddings": np.random.rand(1, 256).astype(np.float32)}
    
    mock_session.run.side_effect = mock_run
    mock_session.get_inputs.return_value = [MagicMock(name="input_ids")]
    mock_session.get_outputs.return_value = [MagicMock(name="embeddings")]
    return mock_session


@pytest.fixture
def mock_onnx_model(tmp_path: Path):
    """Fixture that creates a mock ONNX model file and cleans up after."""
    model_path = tmp_path / "test_model.onnx"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.touch()  # Create empty file
    return str(model_path)


@pytest.mark.unit
def test_onnx_backend_initialization(mock_onnx_model, tmp_path: Path):
    """Test that ONNX backend initializes correctly with valid config."""
    cfg = EmbeddingsConfig(
        enabled=True,
        backend="onnx",
        onnx_enabled=True,
        onnx_model_path=mock_onnx_model,
        onnx_providers=["CPUExecutionProvider"],
        dim=256,
        batch_size=4,
        lru_capacity=128,
        cache_dir=tmp_path / "cache",
        ttl_days=30,
    )
    
    with patch('onnxruntime.InferenceSession', return_value=create_mock_onnx_session()):
        svc = EmbeddingsService(cfg)
        assert svc.backend == "onnx"
        assert hasattr(svc, '_onnx_session')
        assert svc._onnx_session is not None


@pytest.mark.unit
def test_onnx_embeddings_generation(mock_onnx_model, tmp_path: Path):
    """Test that ONNX backend generates embeddings with expected properties."""
    cfg = EmbeddingsConfig(
        enabled=True,
        backend="onnx",
        onnx_enabled=True,
        onnx_model_path=mock_onnx_model,
        onnx_providers=["CPUExecutionProvider"],
        dim=256,
        batch_size=4,
        lru_capacity=128,
        cache_dir=tmp_path / "cache",
        ttl_days=30,
    )
    
    test_texts = ["F1 Grand Prix", "MotoGP Argentina", "Stock Car Brasil"]
    
    with patch('onnxruntime.InferenceSession', return_value=create_mock_onnx_session()):
        svc = EmbeddingsService(cfg)
        embeddings = svc.embed_texts(test_texts)
        
        # Check output shape and type
        assert len(embeddings) == len(test_texts)
        for emb in embeddings:
            assert isinstance(emb, np.ndarray)
            assert emb.shape == (cfg.dim,)
            assert emb.dtype == np.float32
        
        # Check metrics
        assert svc.metrics["cache_misses"] == len(test_texts)  # First run, all misses
        assert len(svc.metrics["batch_latencies_ms"]) == 1  # Single batch


@pytest.mark.unit
def test_onnx_cache_behavior(mock_onnx_model, tmp_path: Path):
    """Test that ONNX backend properly caches embeddings."""
    cfg = EmbeddingsConfig(
        enabled=True,
        backend="onnx",
        onnx_enabled=True,
        onnx_model_path=mock_onnx_model,
        onnx_providers=["CPUExecutionProvider"],
        dim=256,
        batch_size=4,
        lru_capacity=128,
        cache_dir=tmp_path / "cache",
        ttl_days=30,
    )
    
    test_texts = ["F1 Grand Prix", "MotoGP Argentina"]
    
    with patch('onnxruntime.InferenceSession', return_value=create_mock_onnx_session()) as mock_session:
        svc = EmbeddingsService(cfg)
        
        # First run - should call ONNX
        embeddings1 = svc.embed_texts(test_texts)
        assert mock_session.return_value.run.call_count == 1
        assert svc.metrics["cache_misses"] == len(test_texts)
        
        # Second run with same texts - should hit cache
        embeddings2 = svc.embed_texts(test_texts)
        assert mock_session.return_value.run.call_count == 1  # No additional calls
        assert svc.metrics["cache_hits"] == len(test_texts)
        
        # Results should be identical
        for e1, e2 in zip(embeddings1, embeddings2):
            assert np.array_equal(e1, e2)


@pytest.mark.unit
def test_onnx_fallback_to_hashing(mock_onnx_model, tmp_path: Path):
    """Test that service falls back to hashing when ONNX fails."""
    cfg = EmbeddingsConfig(
        enabled=True,
        backend="onnx",
        onnx_enabled=True,
        onnx_model_path="nonexistent_model.onnx",  # Will cause ONNX to fail
        onnx_providers=["CPUExecutionProvider"],
        dim=256,
        batch_size=4,
        lru_capacity=128,
        cache_dir=tmp_path / "cache",
        ttl_days=30,
    )
    
    # Should log warning but not raise
    with patch('logging.Logger.warning') as mock_warning:
        svc = EmbeddingsService(cfg)
        assert svc.backend == "hashing"  # Should fall back to hashing
        mock_warning.assert_called()
    
    # Should still work with hashing backend
    test_texts = ["F1 Grand Prix"]
    embeddings = svc.embed_texts(test_texts)
    assert len(embeddings) == len(test_texts)
    assert len(embeddings[0]) == cfg.dim
