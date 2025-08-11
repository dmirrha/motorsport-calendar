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
  - `sources/base_source/test_helpers_and_parsers.py`
  - `utils/test_config_validator.py`
  - `silent_period/test_silent_period.py`
- `tests/integration/` (reservado para testes de integração)
- `tests/regression/` (artefatos e testes de regressão/manual)

## Execução

- Execução rápida:
  - `pytest -q`
  - `pytest -m unit -q`
  
- Com cobertura:
  - `pytest --cov=src --cov=sources \
    --cov-report=term-missing:skip-covered \
    --cov-report=xml:coverage.xml --cov-report=html \
    --junitxml=test_results/junit.xml`
  - Gate temporário de cobertura: `--cov-fail-under=25` (estabilização dos mocks essenciais, issue #48)
  
### Métricas recentes
- Fase 1.1 — issue #60
  - Suíte: **125 passed (~13.9s)**
  - Cobertura global: **41.72%**
  - `sources/base_source.py`: **92%**
 
 - Fase 1.1 — issue #61
   - Suíte (foco no módulo): **24 passed, 125 deselected**
   - Cobertura de `src/event_processor.py`: **83%**
   - Escopo: normalização (links/data/hora/categoria/local/país/sessão), deduplicação (threshold/tolerância/merge), pipeline (`process_events`), categorias (`_detect_categories`), weekend target (`_detect_target_weekend`), estatísticas e logs
   - Novos testes:
     - `tests/unit/processing/test_event_processor_normalization.py`
     - `tests/unit/processing/test_event_processor_dedup.py`
     - `tests/unit/processing/test_event_processor_stats_repr.py`
     - `tests/unit/processing/test_event_processor_pipeline.py`

### Destaques — BaseSource (issue #60)
- HTTP 4xx com retries e logs
- Backoff exponencial/rate-limit com monkeypatch em `time.sleep` (sem sleeps reais)
- Comportamento seguro quando `logger=None` via `getattr` para métodos customizados
- Verificações de logs de debug e salvamento de payloads
- Teste opcional: rotação de `User-Agent` na 10ª requisição (determinístico via monkeypatch em `random.choice`)
- Helpers e parsers cobertos: `parse_date_time`, `normalize_event_data`, `filter_weekend_events`, `_setup_session` (headers), `get_streaming_links`
  - Incrementais: campos ausentes/HTML malformado, `recent_errors` slice em `get_statistics`, `filter_weekend_events(None)`, formatos adicionais de data e timezone custom, estabilidade de `_generate_event_id`

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
