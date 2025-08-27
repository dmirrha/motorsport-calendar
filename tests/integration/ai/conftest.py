"""Configurações de teste para integração de IA.

Este módulo contém fixtures e configurações específicas para os testes de integração
do serviço de embeddings com suporte a ONNX.
"""
import os
from pathlib import Path
from typing import Generator, Optional

import numpy as np
import pytest

from src.ai.embeddings_service import EmbeddingsService, EmbeddingsConfig

# Caminho para o modelo ONNX de teste
TEST_MODEL_PATH = Path("tests/data/onnx/model.onnx")


def has_onnx() -> bool:
    """Verifica se as dependências do ONNX estão instaladas."""
    try:
        import onnx
        import onnxruntime
        return True
    except ImportError:
        return False


def has_gpu() -> bool:
    """Verifica se há suporte a GPU via CUDA."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def has_apple_silicon() -> bool:
    """Verifica se está rodando em um Mac com Apple Silicon."""
    import platform
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def get_default_providers() -> list[str]:
    """Retorna a lista de provedores padrão com base no hardware disponível."""
    if has_gpu():
        return ["CUDAExecutionProvider", "CPUExecutionProvider"]
    if has_apple_silicon():
        return ["CoreMLExecutionProvider", "CPUExecutionProvider"]
    return ["CPUExecutionProvider"]


@pytest.fixture(scope="session")
def onnx_model_path() -> Path:
    """Retorna o caminho para o modelo ONNX de teste."""
    if not TEST_MODEL_PATH.exists():
        pytest.skip(f"Modelo ONNX de teste não encontrado em {TEST_MODEL_PATH}")
    return TEST_MODEL_PATH


@pytest.fixture(scope="session")
def onnx_providers() -> list[str]:
    """Retorna a lista de provedores ONNX disponíveis para teste."""
    if not has_onnx():
        pytest.skip("Dependências do ONNX não estão instaladas")
    
    providers = []
    try:
        import onnxruntime as ort
        available_providers = ort.get_available_providers()
        
        # Ordem de preferência
        preferred_order = [
            "CUDAExecutionProvider",
            "CoreMLExecutionProvider",
            "CPUExecutionProvider"
        ]
        
        # Filtra apenas os provedores disponíveis e na ordem de preferência
        for provider in preferred_order:
            if provider in available_providers:
                providers.append(provider)
        
        # Se nenhum provedor preferencial estiver disponível, usa o primeiro disponível
        if not providers and available_providers:
            providers = [available_providers[0]]
            
    except Exception as e:
        pytest.skip(f"Não foi possível determinar os provedores ONNX: {e}")
    
    if not providers:
        pytest.skip("Nenhum provedor ONNX disponível para teste")
        
    return providers


@pytest.fixture
def embeddings_config(tmp_path, onnx_model_path, onnx_providers) -> EmbeddingsConfig:
    """Configuração básica para o serviço de embeddings."""
    return EmbeddingsConfig(
        enabled=True,
        device="auto",
        backend="onnx",
        batch_size=32,
        dim=384,  # Dimensão do modelo de teste
        lru_capacity=100,
        cache_dir=tmp_path / "embeddings_cache",
        ttl_days=1,
        onnx_enabled=True,
        onnx_model_path=onnx_model_path,
        onnx_providers=onnx_providers,
    )


@pytest.fixture
def embeddings_service(embeddings_config) -> Generator[EmbeddingsService, None, None]:
    """Instância do serviço de embeddings para testes."""
    service = EmbeddingsService(embeddings_config)
    try:
        yield service
    finally:
        # Limpa recursos após os testes
        if hasattr(service, '_onnx_session'):
            del service._onnx_session


@pytest.fixture
def test_texts() -> list[str]:
    """Textos de exemplo para testes de embeddings."""
    return [
        "F1 Grande Prêmio do Brasil - Corrida",
        "MotoGP Argentina - Treino Livre",
        "Stock Car Brasil - Corrida em Goiânia",
        "Fórmula E - E-Prix de São Paulo",
        "WEC - 6 Horas de Spa-Francorchamps",
    ]


@pytest.fixture
def assert_embeddings_similar():
    """Função auxiliar para verificar similaridade de embeddings."""
    def _assert_embeddings_similar(
        emb1: np.ndarray, 
        emb2: np.ndarray, 
        threshold: float = 0.9
    ) -> None:
        """Verifica se dois embeddings são similares usando similaridade de cosseno."""
        from numpy.linalg import norm
        
        # Normaliza os vetores
        emb1_norm = emb1 / (norm(emb1) + 1e-9)
        emb2_norm = emb2 / (norm(emb2) + 1e-9)
        
        # Calcula similaridade de cosseno
        similarity = np.dot(emb1_norm, emb2_norm)
        
        assert similarity >= threshold, (
            f"Similaridade {similarity:.4f} é menor que o limiar {threshold}"
        )
    
    return _assert_embeddings_similar


# Marcação para testes que requerem ONNX
skip_if_no_onnx = pytest.mark.skipif(
    not has_onnx(),
    reason="Requer dependências do ONNX (onnx, onnxruntime)"
)

# Marcação para testes que requerem GPU
skip_if_no_gpu = pytest.mark.skipif(
    not has_gpu(),
    reason="Requer suporte a GPU CUDA"
)

# Marcação para testes que requerem Apple Silicon
skip_if_no_apple_silicon = pytest.mark.skipif(
    not has_apple_silicon(),
    reason="Requer Apple Silicon (M1/M2)"
)
