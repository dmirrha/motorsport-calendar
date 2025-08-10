# Ajuste de path para permitir imports como `from sources...` e pacotes em `src/`
from pathlib import Path
import sys
import os
import time

import pytest

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
    def __init__(self, text="", status_code=200, json_data=None, raise_http_error=False):
        self.text = text
        self.status_code = status_code
        self._json_data = json_data
        self._raise_http_error = raise_http_error

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

    def get(self, url, **kwargs):
        if self._exception:
            raise self._exception
        if callable(self._response_or_callable):
            return self._response_or_callable(url, **kwargs)
        return self._response_or_callable or _DummyResponse()

    def post(self, url, **kwargs):
        return self.get(url, **kwargs)


@pytest.fixture
def dummy_response():
    """Factory para criar `_DummyResponse` de forma concisa em testes."""
    def _factory(text="", status_code=200, json_data=None, raise_http_error=False):
        return _DummyResponse(text=text, status_code=status_code, json_data=json_data, raise_http_error=raise_http_error)
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
