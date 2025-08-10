# Suíte de Testes

Este diretório contém a suíte de testes do projeto. A descoberta de testes é limitada a `tests/` via `pytest.ini` (`testpaths = tests`).

## Convenções

- Nome dos arquivos: `test_*.py`
- Estrutura por domínio/componente em `tests/unit/`:
  - `tests/unit/sources/<source_name>/...`
  - `tests/unit/utils/...`
  - `tests/unit/<feature>/...` (ex.: `silent_period`)
- Não usar `__init__.py` nos diretórios de teste (evita pacotes e conflitos de descoberta do Pytest).
- Fixtures reutilizáveis e configurações comuns em `tests/conftest.py`.
- Timezone fixo para testes: `America/Sao_Paulo` (fixture autouse em `tests/conftest.py`).
- Marcadores registrados em `pytest.ini`:
  - `@pytest.mark.unit`
  - `@pytest.mark.integration`

## Estrutura Atual

- `tests/unit/`
  - `sources/tomada_tempo/test_tomada_tempo.py`
  - `utils/test_config_validator.py`
  - `silent_period/test_silent_period.py`
- `tests/integration/` (reservado para testes de integração)
- `tests/regression/` (artefatos e testes de regressão/manual)

## Execução

- Todos os testes: `pytest`
- Unit tests: `pytest -m unit`
- Cobertura: `pytest --cov` (gate de cobertura temporário `--cov-fail-under=25` — estabilização dos mocks essenciais, issue #48)

Relatórios são gerados em:
- JUnit XML: `test_results/junit.xml`
- Cobertura HTML: `htmlcov/`
- Cobertura XML: `coverage.xml`

## Mocks e Isolamento

- Timezone: fixture autouse define `America/Sao_Paulo` (em `tests/conftest.py`).
- Aleatoriedade: fixture autouse `_fixed_random_seed` fixa `random.seed(0)` por teste, com restauração do estado.
- Rede (shims/padrões de patch):
  - `patch_requests_get`: patch para `sources.tomada_tempo.requests.get`
  - `patch_requests_session`: patch para `sources.base_source.requests.Session`
- Filesystem: use `tmp_path`/`tmp_path_factory` para interações com disco.
- Variáveis de ambiente: use `monkeypatch.setenv`/`delenv` para configurar/limpar `os.environ`.

Exemplos:

```python
def test_parse_from_html_ok(patch_requests_get, dummy_response):
    html = "<html>...</html>"
    patch_requests_get(lambda url, **kw: dummy_response(text=html))
    # execute função que consome TomadaTempoSource
```

```python
import requests

def test_timeout_session(patch_requests_session):
    sess = patch_requests_session(exception_to_raise=requests.Timeout())
    # instanciar source que usa BaseSource -> requests.Session() será a sessão dummy
    #
    # execute função que consome TomadaTempoSource
    #
    # assertions
```

### Referências de testes (mocks essenciais)

- Isolamento de filesystem: `tests/unit/utils/test_payload_manager.py` (uso de `tmp_path`)
- Variáveis de ambiente: `tests/unit/test_env_vars.py` (uso de `monkeypatch.setenv/delenv`)
- Cenários de rede:
  - `tests/unit/sources/base_source/test_make_request.py` (sucesso/timeout/HTTPError)
  - `tests/unit/sources/tomada_tempo/test_parse_calendar_page.py` (HTML válido/malformado)

## Diretrizes

- Centralize helpers/fixtures reutilizáveis em `tests/utils/` e/ou `tests/conftest.py`.
- Evite dependências entre testes. Prefira dados de teste determinísticos.
- Se um teste depender de timezone/date, use a fixture de TZ e datas fixas.
- Testes de integração/regressão não devem afetar a descoberta de unit tests.
