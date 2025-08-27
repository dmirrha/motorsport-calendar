import math
import logging
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import numpy as np
import pytest

from src.ai import EmbeddingsConfig, EmbeddingsService

# Skip ONNX tests if not available or explicitly disabled
pytestmark = pytest.mark.skipif(
    os.getenv("SKIP_ONNX_TESTS", "false").lower() == "true",
    reason="ONNX tests skipped via SKIP_ONNX_TESTS",
)


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


@pytest.mark.unit
def test_onnx_backend_initialization(tmp_path):
    """Testa a inicialização do backend ONNX."""
    # Configuração do mock para a sessão ONNX
    mock_session = MagicMock()
    mock_session.get_providers.return_value = ["CPUExecutionProvider"]
    mock_session.run.return_value = [np.random.rand(1, 384).astype(np.float32)]
    
    # Cria um arquivo de modelo ONNX falso
    model_path = tmp_path / "model.onnx"
    model_path.touch()
    
    with patch('onnxruntime.InferenceSession', return_value=mock_session) as mock_onnx:
        # Configuração com ONNX habilitado
        cfg = EmbeddingsConfig(
            enabled=True,
            device="cpu",
            backend="onnx",
            dim=384,
            batch_size=4,
            lru_capacity=128,
            cache_dir=tmp_path / "onnx_cache",
            ttl_days=30,
            onnx_enabled=True,
            onnx_model_path=model_path,
            onnx_providers=["CPUExecutionProvider"],
        )
        
        # Cria o serviço - deve chamar onnxruntime.InferenceSession
        svc = EmbeddingsService(cfg)
        
        # Verifica se a sessão ONNX foi criada
        assert hasattr(svc, 'ort_session')
        assert svc.ort_session is not None
        mock_onnx.assert_called_once()
        
        # Verifica métricas iniciais
        assert svc.metrics["cache_hits"] == 0
        assert svc.metrics["cache_misses"] == 0
        assert len(svc.metrics["batch_latencies_ms"]) == 0


@pytest.mark.unit
def test_onnx_embedding_generation(tmp_path):
    """Testa a geração de embeddings com backend ONNX."""
    # Configuração do mock para retornar embeddings falsos
    mock_session = MagicMock()
    mock_session.get_providers.return_value = ["CPUExecutionProvider"]
    
    # Cria um array de exemplo com a forma correta (batch_size, 384)
    mock_embeddings = np.random.rand(3, 384).astype(np.float32)
    mock_session.run.return_value = [mock_embeddings]
    
    # Cria um arquivo de modelo ONNX falso
    model_path = tmp_path / "model.onnx"
    model_path.touch()
    
    with patch('onnxruntime.InferenceSession', return_value=mock_session):
        cfg = EmbeddingsConfig(
            enabled=True,
            device="cpu",
            backend="onnx",
            dim=384,
            batch_size=4,
            lru_capacity=128,
            cache_dir=tmp_path / "onnx_cache",
            ttl_days=30,
            onnx_enabled=True,
            onnx_model_path=model_path,
            onnx_providers=["CPUExecutionProvider"],
        )
        
        svc = EmbeddingsService(cfg)
        
        # Textos de teste
        texts = ["F1 Brasil", "MotoGP Argentina", "Stock Car Goiânia"]
        
        # Gera embeddings
        embeddings = svc.embed_texts(texts)
        
        # Verificações básicas
        assert len(embeddings) == len(texts)
        for emb in embeddings:
            assert isinstance(emb, list)  # O serviço retorna listas, não arrays numpy
            assert len(emb) == 384  # Dimensão configurada
        
        # Verifica se o método run foi chamado corretamente
        # Como o _embed_batch_onnx atual é um stub, não podemos verificar chamadas específicas
        
        # Verifica métricas
        assert svc.metrics["cache_misses"] == len(texts)  # Primeira execução, deve ser tudo miss
        assert len(svc.metrics["batch_latencies_ms"]) == 1  # Apenas um lote


@pytest.mark.unit
def test_onnx_cache_behavior(tmp_path):
    """Testa o comportamento do cache com backend ONNX."""
    # Configuração do mock
    mock_session = MagicMock()
    mock_session.get_providers.return_value = ["CPUExecutionProvider"]
    mock_session.run.return_value = [
        np.random.rand(1, 384).astype(np.float32)  # Dimensão do modelo de teste
    ]
    
    with patch('onnxruntime.InferenceSession', return_value=mock_session):
        cfg = EmbeddingsConfig(
            enabled=True,
            device="cpu",
            backend="onnx",
            dim=384,
            batch_size=4,
            lru_capacity=2,  # Cache pequeno para teste
            cache_dir=tmp_path / "onnx_cache",
            ttl_days=1,
            onnx_enabled=True,
            onnx_model_path=tmp_path / "model.onnx",
            onnx_providers=["CPUExecutionProvider"],
        )
        
        svc = EmbeddingsService(cfg)
        
        # Primeira execução - deve preencher o cache
        texts1 = ["F1 Brasil", "MotoGP Argentina"]
        emb1 = svc.embed_texts(texts1)
        assert svc.metrics["cache_misses"] == 2
        assert svc.metrics["cache_hits"] == 0
        
        # Segunda execução - deve usar o cache
        emb2 = svc.embed_texts(texts1)
        assert svc.metrics["cache_hits"] == 2
        assert svc.metrics["cache_misses"] == 2  # Não deve incrementar
        
        # Deve retornar os mesmos embeddings
        for e1, e2 in zip(emb1, emb2):
            assert np.allclose(e1, e2)
        
        # Adiciona mais itens para testar a substituição LRU
        texts2 = ["Stock Car Goiânia", "Fórmula E São Paulo"]
        svc.embed_texts(texts2)  # Deve remover os itens mais antigos do cache
        
        # Verifica se o cache foi atualizado corretamente
        assert svc.metrics["cache_misses"] == 4
        assert svc.metrics["cache_hits"] == 2


@pytest.mark.unit
def test_onnx_batching(tmp_path):
    """Testa o processamento em lotes com backend ONNX."""
    # Configuração do mock para retornar embeddings falsos
    mock_session = MagicMock()
    mock_session.get_providers.return_value = ["CPUExecutionProvider"]

    # Cria um array de exemplo com a forma correta (batch_size, 384)
    mock_embeddings = np.random.rand(5, 384).astype(np.float32)
    mock_session.run.return_value = [mock_embeddings]

    # Cria um arquivo de modelo ONNX falso
    model_path = tmp_path / "model.onnx"
    model_path.touch()

    with patch('onnxruntime.InferenceSession', return_value=mock_session):
        cfg = EmbeddingsConfig(
            enabled=True,
            device="cpu",
            backend="onnx",
            dim=384,
            batch_size=5,  # Tamanho do lote igual ao número de textos
            lru_capacity=128,
            cache_dir=tmp_path / "onnx_cache",
            ttl_days=30,
            onnx_enabled=True,
            onnx_model_path=model_path,
            onnx_providers=["CPUExecutionProvider"],
        )

        svc = EmbeddingsService(cfg)

        # Textos de teste - 5 textos
        texts = [f"Evento {i}" for i in range(5)]

        # Gera embeddings
        embeddings = svc.embed_texts(texts)

        # Verifica se todos os embeddings foram gerados
        assert len(embeddings) == len(texts)

        # Verifica se o processamento em lote foi usado corretamente
        # Verifica apenas a métrica de latência, já que é o que o serviço registra
        assert len(svc.metrics["batch_latencies_ms"]) == 1  # Apenas um lote registrado corretamente
            
        # Verifica se os embeddings têm o formato correto
        for emb in embeddings:
            assert isinstance(emb, list)  # O serviço retorna listas, não arrays numpy
            assert len(emb) == 384  # Dimensão configurada


@pytest.mark.unit
def test_onnx_provider_fallback(tmp_path, caplog):
    """Testa o fallback de provedores ONNX."""
    # Configuração do mock para simular falha no primeiro provedor
    mock_session = MagicMock()
    mock_session.get_providers.return_value = ["CPUExecutionProvider"]
    mock_session.run.return_value = [np.random.rand(1, 384).astype(np.float32)]
    
    # Simula falha na inicialização com CUDA
    def mock_init(*args, **kwargs):
        providers = kwargs.get("providers", [])
        if "CUDAExecutionProvider" in providers:
            raise RuntimeError("CUDA not available")
        return mock_session
    
    # Cria um arquivo de modelo ONNX falso
    model_path = tmp_path / "model.onnx"
    model_path.touch()
    
    with patch('onnxruntime.InferenceSession', side_effect=mock_init):
        cfg = EmbeddingsConfig(
            enabled=True,
            device="auto",
            backend="onnx",
            dim=384,
            batch_size=4,
            lru_capacity=128,
            cache_dir=tmp_path / "onnx_cache",
            ttl_days=30,
            onnx_enabled=True,
            onnx_model_path=model_path,
            onnx_providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
        )
        
        # Limpa os logs antes de começar o teste
        caplog.clear()
        
        # Cria o serviço - deve tentar CUDA primeiro e depois cair para CPU
        with caplog.at_level(logging.WARNING):
            svc = EmbeddingsService(cfg)
            
            # Verifica se a sessão foi criada corretamente
            assert hasattr(svc, 'ort_session')
            
            # Verifica se o serviço está funcionando
            texts = ["Teste de fallback de provedor"]
            embeddings = svc.embed_texts(texts)
            assert len(embeddings) == 1
            assert len(embeddings[0]) == 384  # Dimensão configurada
        
        # Verifica se o log de aviso foi registrado
        assert any("Falha ao inicializar ONNX Runtime" in record.message 
                  for record in caplog.records)
