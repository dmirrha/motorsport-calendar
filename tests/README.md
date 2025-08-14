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
  - `pytest -m integration -q` (testes de integração)
  
- Com cobertura:
  - `pytest --cov=src --cov=sources \
    --cov-report=term-missing:skip-covered \
    --cov-report=xml:coverage.xml --cov-report=html \
    --junitxml=test_results/junit.xml`
  - Gate global de cobertura: `--cov-fail-under=45` (issue #63)

  Comandos rápidos (local):

  ```bash
  # Suíte completa com cobertura e relatórios
  pytest --cov=src --cov=sources \
    --cov-report=term-missing:skip-covered \
    --cov-report=xml:coverage.xml --cov-report=html \
    -q --junitxml=test_results/junit.xml
  
  # Foco em módulos críticos
  pytest -q tests/unit/utils/test_payload_manager*.py
  pytest -q tests/unit/ical/test_ical_generator*.py

  # Integração apenas (marcados com @pytest.mark.integration)
  pytest -m integration -q
  # Exemplos de filtros:
  pytest -m "integration and not slow" -q

  # Checagem de estabilidade (zero flakes)
  for i in 1 2 3; do pytest -q; done
  ```

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

 - Fase 1.1 — issue #62
   - Suíte: **156 passed**; cobertura global: **51.92%**
   - Cobertura de `src/ical_generator.py`: **76%**
   - Novos testes: `tests/unit/ical/test_ical_generator_extended.py`
   - Nota: corrigido efeito colateral de monkeypatch global em `pytz.timezone` nos testes de processamento para não interferir nos testes de iCal

 - Fase 1.1 — issue #63
   - Suíte: **170 passed**; cobertura global: **57.86%**
   - Gate global em `pytest.ini`: `--cov-fail-under=45`
   - Novos testes:
     - `tests/unit/category/test_category_detector_basic.py`
     - `tests/unit/utils/test_payload_manager_extended.py`
     - `tests/unit/config/test_config_manager_basic.py`

 - Fase 1.1 — issue #64
   - Suíte: **205 passed**; cobertura global: **61.52%**
   - `src/utils/payload_manager.py`: **90%**
   - `src/ical_generator.py`: **93%**
   - Novos testes: `tests/unit/utils/test_payload_manager_errors.py`, `tests/unit/ical/test_ical_generator_branches.py`
   - Estabilidade: suíte executada 3× localmente sem flakes

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

### Integração Contínua (CI)

O projeto executa a suíte de testes no GitHub Actions via workflow em `.github/workflows/tests.yml`:

- Ambiente: `ubuntu-latest`, Python 3.11
- Instalação: `requirements.txt` (+ `requirements-dev.txt` se existir)
- Execução: `pytest` com cobertura em `src/` e `sources/`
- Relatórios: `junit.xml`, `coverage.xml`, `htmlcov/` (enviados como artefatos)
- Cache de pip habilitado por hash dos arquivos `requirements*.txt`
- Job adicional: `e2e_happy` — executa apenas `tests/integration/test_phase2_e2e_happy.py` com cobertura, ignorando `pytest.ini` via `-c /dev/null`. Artefatos: `test_results_e2e/junit.xml`, `coverage_e2e.xml`, `htmlcov-e2e/`.

## Mocks e Isolamento

- Timezone: fixture autouse define `America/Sao_Paulo` (em `tests/conftest.py`).
- Aleatoriedade: fixture autouse `_fixed_random_seed` fixa `random.seed(0)` por teste, com restauração do estado.
- Rede (shims/padrões de patch):
  - `patch_requests_get`: patch para `sources.tomada_tempo.requests.get`
  - `patch_requests_session`: patch para `sources.base_source.requests.Session`
- Filesystem: use `tmp_path`/`tmp_path_factory` para interações com disco.
- Variáveis de ambiente: use `monkeypatch.setenv`/`delenv` para configurar/limpar `os.environ`.
- Tempo congelado: use `freeze_datetime()` para fixar `datetime.now()/today()` em módulos-chave (`src.logger`, `src.event_processor`, `src.utils.payload_manager`, `src.ical_generator`, `src.data_collector`, `motorsport_calendar`, `sources.base_source`, `sources.tomada_tempo`).
- UUID determinístico: use `fixed_uuid()` para tornar `uuid.uuid4()` previsível durante os testes.

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

```python
from datetime import datetime

def test_freeze_time(freeze_datetime):
    fixed = datetime(2024, 1, 1, 12, 0, 0)
    freeze_datetime(dt=fixed)
    # chamadas internas a datetime.now() em módulos-alvo retornarão 2024-01-01T12:00:00
```

```python
import uuid

def test_fixed_uuid(fixed_uuid):
    fixed_uuid()  # aplica UUID constante
    assert str(uuid.uuid4()) == "00000000-0000-0000-0000-000000000000"
```

### Referências de testes (mocks essenciais)

- Isolamento de filesystem: `tests/unit/utils/test_payload_manager.py` (uso de `tmp_path`)
- Variáveis de ambiente: `tests/unit/test_env_vars.py` (uso de `monkeypatch.setenv/delenv`)
- Cenários de rede:
  - `tests/unit/sources/base_source/test_make_request.py` (sucesso/timeout/HTTPError)
  - `tests/unit/sources/tomada_tempo/test_parse_calendar_page.py` (HTML válido/malformado)

### Integração — Referências

- Cenários Fase 2: `docs/tests/scenarios/phase2_scenarios.md`
- Índice de cenários: `docs/tests/scenarios/SCENARIOS_INDEX.md`
- Governança Fase 2: PR #87 (https://github.com/dmirrha/motorsport-calendar/pull/87) — épico #78

### Integração — Snapshots ICS (Issue #86)

- Local dos snapshots canônicos: `tests/snapshots/phase2/phase2_basic.ics`.
- Normalização para comparação estável: `tests/utils/ical_snapshots.py` normaliza UID e remove campos voláteis, além de padronizar quebras de linha.
  - UID: normalizado para token fixo (`UID:FIXED-UID`).
  - Campos removidos: `DTSTAMP`, `CREATED`, `LAST-MODIFIED`, `SEQUENCE`, `PRODID`.
  - Quebras de linha normalizadas para `\n`.
- Execução dos testes de integração (básico fase 2):
  - `pytest -m integration -q`
  - `pytest -q tests/integration/test_phase2_basic.py`
- Atualização de snapshot:
  - Gere o ICS via teste e, se a mudança for intencional, atualize `tests/snapshots/phase2/phase2_basic.ics` com a versão normalizada (ver `compare_or_write_snapshot()` e `normalize_ics_text()` em `tests/utils/ical_snapshots.py`).

### Integração — E2E Caminho Feliz (Issue #82)
- Teste: `tests/integration/test_phase2_e2e_happy.py`
- Snapshot: `tests/snapshots/phase2/phase2_e2e_happy.ics`
- Execução local (sem cobertura/gate; ignorando `pytest.ini`):
  - Comando: `pytest -q -c /dev/null tests/integration/test_phase2_e2e_happy.py -k happy`
  - Run 1: 1 passed in 1.95s
  - Run 2: 1 passed in 2.02s
  - Run 3: 1 passed in 2.00s
- Média: ~1.99s; Estabilidade: 3/3 passes (<30s). Sem flakes.
- Nota: o aviso de marker `integration` ocorre apenas com `-c /dev/null`; no fluxo normal, os markers estão registrados em `pytest.ini`.
- CI: o job `e2e_happy` no GitHub Actions executa exatamente este teste e publica artefatos dedicados.

### Integração — Edge cases ICS (Issue #80)

- Testes:
  - `tests/integration/test_phase2_optionals.py`
  - `tests/integration/test_phase2_overnight.py`
  - `tests/integration/test_phase2_timezones.py`
- Fixtures:
  - `tests/fixtures/integration/scenario_optionals_missing.json`
  - `tests/fixtures/integration/scenario_overnight.json`
  - `tests/fixtures/integration/scenario_timezones.json`
- Snapshots canônicos:
  - `tests/snapshots/phase2/phase2_optionals.ics`
  - `tests/snapshots/phase2/phase2_overnight.ics`
  - `tests/snapshots/phase2/phase2_timezones.ics`
- Normalização: `tests/utils/ical_snapshots.py` (UID fixo, remoção de campos voláteis, `\n`).
- Execução:
  - `pytest -m integration -q` (suíte de integração)
  - `pytest -q tests/integration/test_phase2_*.py`
- Atualização de snapshot: se a mudança for intencional, gere a saída e atualize o arquivo `.ics` correspondente após normalizar via utilitário (ver `compare_or_write_snapshot()` e `normalize_ics_text()`).

### Integração — Deduplicação, Ordenação e Consistência de TZ (Issue #84)

- Teste: `tests/integration/test_phase2_dedupe_order_consistency.py`
- Fixture: `tests/fixtures/integration/scenario_dedupe_order.json`
- Snapshot: `tests/snapshots/phase2/phase2_dedupe_order_consistency.ics`
- Normalização: `tests/utils/ical_snapshots.py` (UID fixo; remove `DTSTAMP/CREATED/LAST-MODIFIED/SEQUENCE/PRODID`; quebras `\n`).
- Execução:
  - `pytest -q tests/integration/test_phase2_dedupe_order_consistency.py`
  - `pytest -m integration -q -k dedupe`
- Estabilidade: executar 3× localmente; esperado sem flakes e <30s.

## Diretrizes

- Centralize helpers/fixtures reutilizáveis em `tests/utils/` e/ou `tests/conftest.py`.
- Evite dependências entre testes. Prefira dados de teste determinísticos.
- Se um teste depender de timezone/date, use a fixture de TZ e datas fixas.
- Testes de integração/regressão não devem afetar a descoberta de unit tests.
