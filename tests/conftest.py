# Ajuste de path para permitir imports como `from sources...` e pacotes em `src/`
from pathlib import Path
import sys
import os
import time
from typing import Dict, Any, Optional, List

import numpy as np
import pytest

# Adiciona o diretório raiz ao path para importar módulos do projeto
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

ROOT = Path(__file__).resolve().parent.parent  # raiz do repositório
SRC = ROOT / "src"

# Inserir raiz do repo (para `sources/`, etc.)
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

# Inserir `src/` se existir (para `motorsport_calendar`, etc.)
src_str = str(SRC)
if SRC.exists() and src_str not in sys.path:
    sys.path.insert(0, src_str)


@pytest.fixture(autouse=True, scope="session")
def _tz_america_sao_paulo():
    """Define TZ padrão para America/Sao_Paulo para garantir determinismo nos testes.

    Restaura o valor anterior ao final da sessão de testes.
    """
    prev_tz = os.environ.get("TZ")
    os.environ["TZ"] = "America/Sao_Paulo"
    if hasattr(time, "tzset"):
        time.tzset()
    try:
        yield
    finally:
        if prev_tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = prev_tz
        if hasattr(time, "tzset"):
            time.tzset()


@pytest.fixture(autouse=True)
def _fixed_random_seed():
    """Garante determinismo do RNG por teste.

    Salva/recupera o estado do RNG para não interferir em outros testes.
    """
    import random
    state = random.getstate()
    random.seed(0)
    try:
        yield
    finally:
        random.setstate(state)


class _DummyResponse:
    """Resposta mínima para simular `requests.Response`."""
    def __init__(self, text="", status_code=200, json_data=None, raise_http_error=False, url=None, headers=None):
        self.text = text
        self.status_code = status_code
        self._json_data = json_data
        self._raise_http_error = raise_http_error
        # Atributos esperados por usos no código
        self.url = url
        self.headers = headers or {}

    def json(self):
        if self._json_data is None:
            raise ValueError("No JSON data provided")
        return self._json_data

    def raise_for_status(self):
        if self._raise_http_error or not (200 <= self.status_code < 400):
            import requests
            raise requests.HTTPError(f"HTTP {self.status_code}")


class _DummySession:
    """Sessão mínima para substituir `requests.Session`."""
    def __init__(self, response_or_callable=None, exception_to_raise=None):
        # `response_or_callable` pode ser _DummyResponse ou uma função(url, **kwargs) -> _DummyResponse
        self._response_or_callable = response_or_callable
        self._exception = exception_to_raise
        # Compatível com BaseSource._setup_session (headers.update)
        self.headers = {}
    
    # Compatível com BaseSource._setup_session (self.session.mount)
    def mount(self, *_args, **_kwargs):  # no-op
        return None

    def _dispatch(self, url, **kwargs):
        """Gera uma resposta sem depender de `request`.
        
        Evita recursão quando testes sobrescrevem `request()` para chamar `get()`.
        """
        if self._exception:
            raise self._exception
        if callable(self._response_or_callable):
            resp = self._response_or_callable(url, **kwargs)
        else:
            resp = self._response_or_callable or _DummyResponse()
        # Garantir atributos mínimos
        if getattr(resp, "url", None) is None:
            resp.url = url
        if getattr(resp, "headers", None) is None:
            resp.headers = {}
        return resp

    # Compatível com BaseSource.make_request (self.session.request)
    def request(self, method, url, **kwargs):
        return self._dispatch(url, **kwargs)

    def get(self, url, **kwargs):
        return self._dispatch(url, **kwargs)

    def post(self, url, **kwargs):
        return self._dispatch(url, **kwargs)


@pytest.fixture
def dummy_response():
    """Factory para criar `_DummyResponse` de forma concisa em testes."""
    def _factory(text="", status_code=200, json_data=None, raise_http_error=False, url=None, headers=None):
        return _DummyResponse(text=text, status_code=status_code, json_data=json_data, raise_http_error=raise_http_error, url=url, headers=headers)
    return _factory


@pytest.fixture
def patch_requests_get(monkeypatch):
    """Padrão de patch para `sources.tomada_tempo.requests.get`.

    Uso:
        resp = dummy_response(text="<html>...</html>")
        patch_requests_get(lambda url, **kw: resp)
    """
    target = "sources.tomada_tempo.requests.get"

    def _apply(replacement):
        # `replacement`: callable(url, **kwargs) -> _DummyResponse
        monkeypatch.setattr(target, replacement, raising=False)
        return replacement

    return _apply


@pytest.fixture
def patch_requests_session(monkeypatch):
    """Padrão de patch para `sources.base_source.requests.Session`.

    Uso:
        session = _DummySession(response_or_callable=...)  # ou exception_to_raise=requests.Timeout()
        patch_requests_session(session)
    """
    target = "sources.base_source.requests.Session"

    def _apply(session_instance=None, *, response_or_callable=None, exception_to_raise=None):
        sess = session_instance or _DummySession(response_or_callable=response_or_callable, exception_to_raise=exception_to_raise)
        monkeypatch.setattr(target, lambda: sess)
        return sess

    return _apply


@pytest.fixture
def freeze_datetime(monkeypatch):
    """Congela ``datetime.now()/today()`` em módulos-chave do projeto.

    Por padrão, aplica o patch em:
    - ``src.logger.datetime``
    - ``src.event_processor.datetime``
    - ``src.utils.payload_manager.datetime``
    - ``src.ical_generator.datetime``
    - ``src.data_collector.datetime``
    - ``motorsport_calendar.datetime``
    - ``sources.base_source.datetime``
    - ``sources.tomada_tempo.datetime``

    Exemplo:
        def test_something(freeze_datetime):
            from datetime import datetime as _dt
            freeze_datetime(dt=_dt(2024, 1, 1, 12, 0, 0))
            # chamadas a datetime.now() nos módulos acima retornarão 2024-01-01 12:00:00

    É possível customizar os alvos via parâmetro ``targets=[...]``.
    """

    def _freeze(*, targets=None, dt=None):
        from datetime import datetime as _dt

        fixed_dt = dt or _dt(2000, 1, 1, 0, 0, 0)

        class _FrozenDateTime(_dt):
            @classmethod
            def now(cls, tz=None):
                d = fixed_dt
                if tz is not None:
                    try:
                        # Se o fixed_dt tiver tz, respeita e converte
                        if d.tzinfo is not None:
                            return d.astimezone(tz)
                        # Caso contrário, tenta usar API de timezone (ex.: pytz)
                        if hasattr(tz, "localize"):
                            return tz.localize(d)
                        return d.replace(tzinfo=tz)
                    except Exception:
                        return d
                return d

            @classmethod
            def today(cls):
                return cls.now()

        default_targets = [
            "src.logger.datetime",
            "src.event_processor.datetime",
            "src.utils.payload_manager.datetime",
            "src.ical_generator.datetime",
            "src.data_collector.datetime",
            "motorsport_calendar.datetime",
            "sources.base_source.datetime",
            "sources.tomada_tempo.datetime",
        ]

        for t in (targets or default_targets):
            monkeypatch.setattr(t, _FrozenDateTime, raising=False)

        return fixed_dt

    return _freeze


@pytest.fixture
def fixed_uuid(monkeypatch):
    """Torna ``uuid.uuid4()`` determinístico.

    Por padrão, retorna sempre ``00000000-0000-0000-0000-000000000000``.
    É possível fornecer uma sequência customizada via ``sequence=[UUID(...), ...]``.

    Exemplo:
        def test_uuids(fixed_uuid):
            import uuid
            fixed_uuid()  # aplica padrão
            assert str(uuid.uuid4()) == "00000000-0000-0000-0000-000000000000"
    """
    import uuid
    from unittest.mock import patch

    def _fixed_uuid(sequence=None):
        if sequence is None:
            sequence = [uuid.UUID(int=0)]  # 00000000-0000-0000-0000-000000000000
        elif not sequence:
            raise ValueError("sequence não pode estar vazia")

        it = iter(sequence)

        def _uuid4():
            try:
                return next(it)
            except StopIteration:
                return sequence[-1]  # repete o último

        patch_uuid = patch('uuid.uuid4', _uuid4)
        patch_uuid.start()
        return patch_uuid

    return _fixed_uuid


@pytest.fixture
def tmp_embeddings_dir(tmp_path):
    """Cria um diretório temporário para armazenar embeddings em disco."""
    cache_dir = tmp_path / "embeddings_cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


@pytest.fixture
def embeddings_config(tmp_embeddings_dir):
    """Configuração padrão para o serviço de embeddings em testes."""
    from src.ai.embeddings_service import EmbeddingsConfig
    
    return EmbeddingsConfig(
        enabled=True,
        device="cpu",
        backend="hashing",  # Backend padrão para testes rápidos
        dim=128,  # Dimensão para o hashing backend
        batch_size=4,
        lru_capacity=100,
        cache_dir=tmp_embeddings_dir,
        ttl_days=1,
        onnx_enabled=False,  # Desativado por padrão, ativar apenas quando necessário
    )


@pytest.fixture
def onnx_embeddings_config(tmp_embeddings_dir):
    """Configuração para testes com backend ONNX."""
    from src.ai.embeddings_service import EmbeddingsConfig
    
    return EmbeddingsConfig(
        enabled=True,
        device="cpu",
        backend="onnx",
        dim=384,  # Dimensão típica para modelos sentence-transformers
        batch_size=4,
        lru_capacity=100,
        cache_dir=tmp_embeddings_dir,
        ttl_days=1,
        onnx_enabled=True,
        onnx_model_path=Path("tests/data/onnx/model.onnx"),  # Caminho para o modelo de teste
        onnx_providers=["CPUExecutionProvider"],
    )


@pytest.fixture
def test_texts():
    """Textos de exemplo para testes de embeddings."""
    return [
        "F1 Grande Prêmio do Brasil - Corrida",
        "MotoGP Argentina - Treino Livre",
        "Stock Car Brasil - Corrida em Goiânia",
        "Fórmula E - E-Prix de São Paulo",
        "WEC - 6 Horas de Spa-Francorchamps",
    ]


@pytest.fixture
def mock_onnx_session():
    """Cria uma sessão ONNX mockada para testes."""
    from unittest.mock import MagicMock
    
    mock_session = MagicMock()
    mock_session.get_providers.return_value = ["CPUExecutionProvider"]
    mock_session.run.return_value = [
        np.random.rand(1, 384).astype(np.float32)  # Dimensão para o modelo de teste
    ]
    return mock_session


@pytest.fixture
def patch_onnx_session(mock_onnx_session):
    """Patch para substituir a criação de sessões ONNX por um mock."""
    from unittest.mock import patch
    
    with patch('onnxruntime.InferenceSession', return_value=mock_onnx_session) as mock:
        yield mock
