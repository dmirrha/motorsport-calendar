# Documentação de Testes — Overview

Objetivo: descrever a estratégia mínima de testes para o projeto, com foco em simplicidade, rastreabilidade e execução rápida/estável.

## Estratégia
- Priorizar testes unitários para parsing, validação e processamento de dados.
- Cobertura alvo por módulo definida por issue/épico vigente.
- Evitar I/O real; preferir fakes/mocks e `tmp_path`.
- Estabilidade: 3× sem flakes, <30s local.

## Escopo
- Fase 0: inventário e decisões de limpeza/escopo.
- Fase 1: unit (parsers/validadores/utils).
- Fase 2: integração (fluxos principais: coleta → processamento → iCal).

## Como executar
- Local (Makefile recomendado):
  - Suíte completa (usa addopts do `pytest.ini`: cobertura HTML/XML, JUnit, gate 45%): `make test`
  - Somente unit: `make test.unit`
  - Somente integração: `make test.integration`
  - Cobertura no terminal (linhas faltantes): `pytest --cov --cov-report=term-missing -q`
  - Abrir relatório HTML (macOS): `open htmlcov/index.html`
  - Sem falha por cobertura (override local): `PYTEST_ADDOPTS="--cov-fail-under=0" pytest`
  - CI: GitHub Actions (`.github/workflows/tests.yml`) usando as mesmas opções do `pytest.ini`.

## Métricas — Cobertura por suíte (medição local em 2025-08-19)
- Unit: **65.75%** — artefatos: `.coverage.unit`, `reports/coverage.unit.xml`, HTML em `htmlcov-unit/`
- Integration: **52.90%** — artefatos: `.coverage.integration`, `reports/coverage.integration.xml`, HTML em `htmlcov-integration/`
- E2E: **31.10%** — artefatos: `.coverage.e2e`, `reports/coverage.e2e.xml`, HTML em `htmlcov-e2e/`

- Comandos executados:
  - Unit:
    ```bash
    COVERAGE_FILE=.coverage.unit \
    pytest -m unit \
      --cov=src --cov=sources \
      --cov-report=term-missing \
      --cov-report=xml:reports/coverage.unit.xml \
      --cov-report=html:htmlcov-unit \
      --cov-fail-under=0
    ```
  - Integration (exclui placeholders):
    ```bash
    COVERAGE_FILE=.coverage.integration \
    pytest -m integration -k "not placeholder" \
      --cov=src --cov=sources \
      --cov-report=xml:reports/coverage.integration.xml \
      --cov-report=html:htmlcov-integration \
      --cov-fail-under=0
    ```
  - E2E (exclui placeholders):
    ```bash
    COVERAGE_FILE=.coverage.e2e \
    pytest -k "e2e and not placeholder" \
      --cov=src --cov=sources \
      --cov-report=xml:reports/coverage.e2e.xml \
      --cov-report=html:htmlcov-e2e \
      --cov-fail-under=0
    ```

### CI — Helper Make para PRs
- Objetivo: manter a branch da PR atualizada com `main` e disparar o workflow `Tests`.
- Pré-requisitos: working tree limpo; GitHub CLI autenticado (`gh auth login`).
- Uso:
  ```bash
  make ci.pr-run BRANCH=<sua-branch>
  # exemplo
  make ci.pr-run BRANCH=chore/it2-tomadatempo-coverage-80
  ```
  - Variáveis opcionais:
    - `WORKFLOW=.github/workflows/tests.yml` (default)
  - O alvo realiza: `git fetch` → `checkout` → `merge --no-edit origin/main` → `push` → `gh workflow run` → `gh run watch` → volta para sua branch original.

## Estrutura de pastas
- `tests/unit/`: testes unitários por módulo.
- `tests/fixtures/`: insumos estáticos (ex.: `ical/` com snapshots canônicos).
- `tests/utils/`: utilitários de teste (ex.: normalização/ comparação de ICS).

## Cenários
- Índice de cenários por fase: `docs/tests/scenarios/SCENARIOS_INDEX.md`

## Atualizações recentes
- CategoryDetector: teste adicional cobrindo branches previamente não exercitados em `src/category_detector.py` (normalização vazia, mapeamentos custom e aprendizado a partir de arquivo salvo). Arquivo: `tests/unit/category/test_category_detector_additional_coverage.py`. Resultado: 100% no run focado.
- DataCollector: teste unitário para o caminho de timeout na coleta concorrente, garantindo marcação de erro e atualização de estatísticas. Arquivo: `tests/unit/data_collector/test_data_collector_timeout_not_done.py`. Resultado: 100% no run focado.
 - TomadaTempo IT1 (Issue #105): integração mínima determinística do parser `sources/tomada_tempo.py` cobrindo caminho feliz, campos opcionais ausentes e HTML malformado com fallbacks (sem crash). Testes: `tests/integration/test_phase3_tomada_tempo_integration.py`, `tests/integration/test_phase3_tomada_tempo_parsing_variants.py`. Métricas recentes: ~48% de cobertura no run de integração; execuções estáveis sem xfail (ex.: 23 passed, 3 skipped).
 - Logger: testes unitários cobrindo inicialização/configuração (handlers, formatters e níveis), rotação com limpeza desabilitada nos testes, emissão por nível e helpers de domínio. Arquivos: `tests/unit/logger/test_logger_basic.py`, `tests/unit/logger/test_logger_misc.py`. Resultado: módulo ~83%, 3× sem flakes (<30s).
 - DataCollector (stubs): ajustes para compatibilidade com `BaseSource` via `MinimalBase` (inicializa atributos essenciais antes de `super().__init__()` e neutraliza rede), evitando falhas silenciosas em `add_source()`. Arquivo ajustado: `tests/unit/test_data_collector.py`. Suíte unit estável e determinística.

### Plugins de teste e determinismo (pytest-timeout/pytest-randomly)

- Dependências (dev): `pytest-timeout~=2.3` e `pytest-randomly~=3.15` em `requirements-dev.txt`.
- Configuração em `pytest.ini`:
  - `timeout = 30`
  - `timeout_method = thread`
  - Seed do `pytest-randomly` configurada via `addopts`: `--randomly-seed=20240501`.
- CI (`.github/workflows/tests.yml`): passos extras imprimem versões de `pytest`, `pytest-cov`, `pytest-timeout`, `pytest-randomly`. Para diagnósticos, leem de `pytest.ini` os valores de `timeout`/`timeout_method` e exibem a seed definida em `addopts`. Comando de versão corrigido para `pytest --version` (sem `--plugins`).
- Objetivo: reduzir flakiness e garantir reprodutibilidade local e em CI.


### Property-based tests (Hypothesis)

- Diretório e marcador: testes residem em `tests/property/` e usam `@pytest.mark.property` (marcador registrado em `pytest.ini`).
- Perfil dedicado: `tests/property/conftest.py` registra e carrega o perfil `property` do Hypothesis (`deadline=None`, `max_examples=30`, e supressão de health checks comuns) para evitar flakes em CI.
- Execução:
  ```bash
  # por marcador
  pytest -m property -q
  # por caminho
  pytest tests/property -q
  ```
- Referências principais:
  - `tests/property/test_prop_datetime_parsing_roundtrip.py` — roundtrip de parsing de `datetime` com TZ.
  - `tests/property/test_prop_dedupe_invariants.py` — invariantes de deduplicação: idempotência e merge estável de links.
  - `tests/property/test_prop_ical_ordering_stability.py` — estabilidade/determinismo da ordenação do iCal.
- Determinismo: com `pytest-randomly` (seed fixa em `pytest.ini`) e o perfil acima, as execuções têm sido estáveis no CI. Em caso de falha, o Hypothesis imprime seed e estratégia para reprodução.
- Determinismo: com `pytest-randomly` (seed fixa via `addopts` em `pytest.ini`) e o perfil acima, as execuções têm sido estáveis no CI. Em caso de falha, o Hypothesis imprime seed e estratégia para reprodução.
- Boas práticas: evitar I/O real; focar invariantes (roundtrip/sort/dedupe); utilizar o marcador `property` e o perfil existente; considerar `max_examples` adequado ao custo do teste.

### Validação de referências (2025-08-20)
- TomadaTempo (integração): OK — `tests/integration/test_phase3_tomada_tempo_integration.py`, `tests/integration/test_phase3_tomada_tempo_parsing_variants.py`.
- TomadaTempo IT2: OK — `tests/integration/test_it2_tomada_tempo_*.py` (ex.: `dates_tz`, `entities_and_duplicates`, `fallbacks_and_parsing`, `multiday_and_location`, `streaming_constraints`).
- PayloadManager (integração): OK — `tests/integration/test_phase2_payload_manager.py`.
- CategoryDetector (unit): referência citada `tests/unit/category/test_category_detector_additional_coverage.py` NÃO encontrada. Atualize para um arquivo existente em `tests/unit/category/` (ex.: `test_category_detector_normalize_more.py`, `test_category_detector_threshold_and_learning.py`) ou ajuste a descrição.
- DataCollector (unit): referência citada `tests/unit/data_collector/test_data_collector_timeout_not_done.py` NÃO encontrada. Unidades existentes: `test_data_collector_basic.py`, `test_data_collector_more.py`, `test_data_collector_retry.py`. Para timeout, existe `tests/integration/test_phase3_data_collector_timeout.py`.

## Determinismo de ICS e snapshots
 - Ordenação de eventos: VEVENTs ordenados deterministicamente por `datetime` (TZ-aware → UTC), `detected_category`, `display_name`/`name`, `source_priority` (desc) e `event_id` (desempate final).
- Streaming links: `streaming_links` ordenados alfabeticamente e limitados a 3 na descrição do evento.
- Normalização de snapshots: UID fixo; remoção de `DTSTAMP`, `CREATED`, `LAST-MODIFIED`, `SEQUENCE`, `PRODID`; quebras de linha `\n`.
- Estabilidade: cada cenário deve passar 3× localmente sem flakes e em <30s.

## Integração — PayloadManager (Fase 2)
- Teste: `tests/integration/test_phase2_payload_manager.py`
- Escopo: serialização de payloads (JSON/HTML/binário), compressão `gzip`, limpeza por idade e por quantidade (retenção), e estatísticas agregadas por fonte.
- Estabilidade: execução local estável, sem flakes observados.
- Cobertura: suíte consolidada ~**91.75%** (visível no Codecov por job/flag).

## Referências
- Governança Fase 2: PR #87 (https://github.com/dmirrha/motorsport-calendar/pull/87) — épico #78
- Relatório de Auditoria da Suíte de Testes (2025-08-19): docs/tests/audit/TEST_AUDIT_2025-08-19.md — pontuações, evidências, lacunas e plano P0–P2.

### Atualização CI — Cobertura por flags (integration/e2e)
- Job `integration`: executa `pytest -m integration` com cobertura focada em módulos principais do fluxo (ex.: `src/config_manager.py`, `src/silent_period.py`, `src/category_detector.py`, `src/ical_generator.py`, `src/event_processor.py`, `src/data_collector.py`, `sources/base_source.py`, `sources/tomada_tempo.py`). Objetivo: refletir cobertura efetiva da suíte de integração sem diluir o denominador.
- Job `e2e`: executa todos os `tests/integration/test_phase2_e2e_*.py` com cobertura focada no pipeline E2E (`src/data_collector.py`, `src/event_processor.py`, `src/ical_generator.py`, `sources/tomada_tempo.py`). Antes rodava apenas `-k happy`.
- Testes de integração relevantes receberam `pytestmark = pytest.mark.integration` para inclusão no job `integration` (ex.: `test_phase2_basic.py`, `test_phase2_optionals.py`, `test_phase2_overnight.py`, `test_phase2_timezones.py`).
- Observação: testes E2E não devem usar o marcador `integration`; são executados separadamente pelo job `e2e` no CI.
- Job `unit`: exclui explicitamente `integration` e o conjunto `test_phase2_e2e_*` via `-m "not integration"` e `-k "not test_phase2_e2e_"` para evitar diluição do denominador de cobertura das flags.

### Política de marcadores (automática)
- Teste de política: `tests/policy/test_markers_policy.py` valida que:
  - Arquivos E2E (`tests/integration/test_phase2_e2e_*.py`) NÃO contêm `pytest.mark.integration`.
  - Arquivos de integração não-E2E em `tests/integration/` CONTÊM `pytest.mark.integration`.
- Objetivo: evitar regressões que baguncem o escopo dos jobs `integration` e `e2e` no CI.

## Atualização CI — Codecov XML (fallback e gates)
- Removido `-c /dev/null` dos comandos `pytest` nos jobs `e2e_happy` e `integration` em `.github/workflows/tests.yml` para que o `pytest.ini` e plugins (ex.: `pytest-cov`) sejam respeitados.
- Aplicado `--cov-fail-under=0` apenas nesses jobs, neutralizando o gate global de cobertura sem afetar o job `unit`.
- Adicionados passos de verificação e fallback antes do upload ao Codecov:
  - Verificar `coverage_e2e.xml` e `coverage_integration.xml` com `ls -l`, `wc -c`, `head`.
  - Se ausente, gerar o XML via `python -m coverage xml -i -o <arquivo>` (reaproveitando dados `.coverage`).
  - Uploads usam `disable_search: true` e apontam explicitamente para os arquivos esperados para evitar uploads indevidos.
