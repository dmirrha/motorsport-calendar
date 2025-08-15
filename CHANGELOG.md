-### Integração — Codecov Components e Tests Analytics (Issue #104)

- Componentes no `codecov.yml`: adicionado componente `sources` para cobrir arquivos em `sources/` (evita cobertura "unassigned").
- Tests Analytics: passos `codecov/test-results-action@v1` adicionados aos jobs `tests` (flag `unit`), `e2e_happy` (flag `e2e`) e `integration` (flag `integration`) com `if: always()` e `CODECOV_TOKEN` via Secrets.
- Workflow: `pytest` com `-o junit_family=legacy` para compatibilidade de nomes no JUnit.
- Links: corrigidos para slug `/github` no Codecov em `README.md` e `tests/README.md`.
- Documentação: `docs/TEST_AUTOMATION_PLAN.md` atualizado com Components + Tests Analytics; `docs/issues/open/issue-104.{md,json}` sincronizados.
- Higiene: `.gitignore` ampliado para `tmp/`, `coverage_*.xml`, `htmlcov-*/`, `test_results_*/`.
# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Integração — Codecov (Issue #98)

- Uploads informativos de cobertura adicionados ao workflow (`codecov/codecov-action@v4`) para os jobs `tests` (flag `unit`, `coverage.xml`) e `integration` (flag `integration`, `coverage_integration.xml`), com `fail_ci_if_error: false`.
- Badge do Codecov adicionado ao `README.md`.
- Documentação atualizada: `tests/README.md` (acesso Codecov), `docs/TEST_AUTOMATION_PLAN.md` (uploads concluídos; gates pendentes).
### Integração — Codecov Hardening (Issue #103)

- Segurança: habilitado OIDC no `codecov/codecov-action@v4` (`use_oidc: true`), eliminando necessidade de token secreto.
- Previsibilidade: desabilitada a varredura automática de arquivos (`disable_search: true`); apenas arquivos explícitos são enviados.
- Configuração mínima adicionada em `codecov.yml`: statuses informativos (`project`/`patch`) e `comment: false`.
- Cobertura expandida: upload adicional no job `e2e_happy` (`coverage_e2e.xml`, flag `e2e`).
- Documentação atualizada: `tests/README.md` e `docs/TEST_AUTOMATION_PLAN.md`.
### CI — Cobertura visível por job (Issue #105)

- `.github/workflows/tests.yml` atualizado para melhorar a visibilidade da cobertura por job:
  - `pytest`: `--cov-report=term:skip-covered` para imprimir sumário de cobertura no console.
  - Passo pós-`pytest` por job (unit/e2e/integration): extração do atributo `line-rate` dos XMLs (`coverage*.xml`) via `grep/sed/awk`, impressão no log, publicação no `$GITHUB_STEP_SUMMARY` e exposição como output do step (`steps.coverage_*/outputs.percent`).
- Baseline: cobertura global 91,27% (Codecov, commit `2096dd8`, branch `chore/issue-105`).
- Documentação sincronizada: `docs/issues/open/issue-105.{md,json}`.
### Integração — Lote 1 (Issue #105)

- Testes de integração adicionados para módulos prioritários: `src/utils/config_validator.py`, `src/config_manager.py`, `src/silent_period.py`, `src/category_detector.py`.
- Total: 13 testes, 0 skips; execução local estável.
- Cobertura aproximada (integration): `config_validator` ~58%, `config_manager` ~70%, `silent_period` ~65%, `category_detector` ~52%.
- Baseline (local): Integration ~40%; E2E (happy) ~40%.
- Documentação sincronizada: `docs/issues/open/issue-105.{md,json}`, `RELEASES.md`.
### Integração — Lote 2 (Issue #105)

- Novos testes de integração focados em orquestração e configuração:
  - `tests/integration/test_phase2_orchestration_silent_manager.py`: valida a integração entre `SilentPeriodManager` e `ConfigManager`, filtrando eventos em período silencioso que cruza a meia-noite (sex/sáb 22:00→06:00) e verificando metadados/estatísticas.
  - `tests/integration/test_phase2_config_manager.py`: complementos para `ConfigManager` cobrindo merge profundo com defaults e persistência (save/load) com arquivos temporários.
- Execução local: ambos passam de forma determinística usando configuração mínima do pytest (`-c /dev/null`) para evitar gates globais; aviso de marker `integration` é esperado nesse modo e não ocorre quando usando `pytest.ini`.
- Próximos passos: ampliar cenários de integração para `sources/tomada_tempo.py`, `src/data_collector.py`, `src/event_processor.py` e `src/ical_generator.py` conforme plano da issue #105.
### Integração — CI: Job de Integração (Issue #81)

- Adicionado job `integration` ao workflow `.github/workflows/tests.yml` executando `pytest -m integration` com cobertura (`pytest-cov`).
- Artefatos publicados: `test_results_integration/junit.xml`, `coverage_integration.xml`, `htmlcov-integration/`.
- Estratégia alinhada aos jobs existentes: Ubuntu, Python 3.11, cache de pip, `-c /dev/null` para ignorar gates globais via `pytest.ini`.
### Documentação — Issue #83

- Sincronização de documentação e rastreabilidade (sem mudanças de código/funcionalidade):
  - `docs/issues/open/issue-83.{md,json}`
  - `docs/TEST_AUTOMATION_PLAN.md` (seção “Progresso — Issue #83”)
  - `tests/README.md` (referência de Fase 2/Issue #83)
  - `docs/tests/scenarios/phase2_scenarios.md` e `docs/tests/scenarios/SCENARIOS_INDEX.md` (referências)
  - `RELEASES.md` (seção “Não Lançado”)
- Objetivo: garantir rastreabilidade entre issues/PRs e documentação padrão.

## [0.5.14] - 2025-08-14
### Integração — Edge cases ICS (Issue #80)

- Fixtures de integração adicionadas:
  - `tests/fixtures/integration/scenario_optionals_missing.json`
  - `tests/fixtures/integration/scenario_overnight.json`
  - `tests/fixtures/integration/scenario_timezones.json`
- Testes de integração correspondentes:
  - `tests/integration/test_phase2_optionals.py`
  - `tests/integration/test_phase2_overnight.py`
  - `tests/integration/test_phase2_timezones.py`
- Snapshots ICS canônicos:
  - `tests/snapshots/phase2/phase2_optionals.ics`
  - `tests/snapshots/phase2/phase2_overnight.ics`
  - `tests/snapshots/phase2/phase2_timezones.ics`
- Normalização de snapshots via `tests/utils/ical_snapshots.py` (UID fixo, remoção de campos voláteis, quebras de linha `\n`).
- Estabilidade validada: cada teste executado 3× localmente, sem flakes (<30s por execução).
- Documentação sincronizada: `CHANGELOG.md`, `RELEASES.md`, `tests/README.md`, `docs/TEST_AUTOMATION_PLAN.md`.
- Rastreabilidade: `docs/issues/open/issue-80.{md,json}` atualizados.
- Versionamento: bump para `0.5.14` em `src/__init__.py`.

## [0.5.13] - 2025-08-13
### Correções e Integração (Issues #82, #86)

- Correção de normalização no `EventProcessor` (campos e retorno de `_normalize_single_event`, preservação de `display_name`).
- Ajuste no `ICalGenerator`: preservação de siglas para categoria de exibição (`F1`, `F2`, `F3`, `WEC`, `WRC`, `WSBK`, `NASCAR`); mapeamento consistente para `SUMMARY`, `CATEGORIES`, `X-MOTORSPORT-CATEGORY` e descrição.
- Snapshots ICS estáveis (básico e E2E): divergências sanadas sem quebrar snapshots canônicos.
- Job de CI dedicado `e2e_happy` no GitHub Actions para executar apenas o E2E caminho feliz com cobertura e artefatos próprios.
- Suíte completa: **339 passed**, **0 failed**; cobertura total **~91.21%**.
- Documentação sincronizada: `CHANGELOG.md`, `RELEASES.md`, `tests/README.md`, `docs/TEST_AUTOMATION_PLAN.md`.

## [0.5.10] - 2025-08-13
### Mocks/Fakes e Fixtures (Issue #79 — Fase 2)

- Fixtures e fakes determinísticos para a suíte:
  - `freeze_datetime`: congela `datetime.now()`/`today()` para tempo determinístico nos módulos relevantes.
  - `fixed_uuid`: substitui `uuid.uuid4()` por UUID fixo para oráculos estáveis.
  - Fakes de HTTP: `_DummyResponse` e `_DummySession` + `patch_requests_get`/`patch_requests_session` em `tests/conftest.py` (sem rede real).
- Dados de teste:
  - Diretório `tests/data/` criado com `README.md` para artefatos mínimos.
- Documentação:
  - `tests/README.md` atualizado com instruções e exemplos das novas fixtures.
- Estabilidade e performance:
  - Suíte executada 3× consecutivas localmente sem flakes, cada execução <30s; métricas atuais: 335 passed; cobertura ~90%.
- Rastreabilidade:
  - Branch de trabalho: `chore/issue-79-fakes-phase2`.
  - Plano e artefatos em `docs/issues/open/issue-79.{md,json}` atualizados.
- PR: #90 (merge via squash)

## [0.5.2] - 2025-08-09
### Manutenção — Testes/Automação
- Ajustado ambiente de testes para evitar `ModuleNotFoundError` via `tests/conftest.py` (inclusão de caminhos da raiz e `src/`).
- Tornado determinístico o teste de filtragem de fim de semana em `tests/test_tomada_tempo.py` (data fixa 01/08/2025 com timezone America/Sao_Paulo).
- Suíte validada: `37 passed`.

## [0.5.1] - 2025-08-09
### Manutenção
- Rollback técnico da branch `main` para o snapshot do commit `9362503` (PR #34), preservando histórico.
- Reaplicação do `.gitignore` para ignorar artefatos de testes e diretórios locais (`tests/regression/test_data/output/`, `test_results/`, `test_results_github/`, `pytest.log`, `junit.xml`, `report.html`).
- CI/Workflow de testes não reintroduzido neste release.

## [Não Lançado]
### Governança — Fase 2 (Testes Integrados e Validação de ICS)
- Épico #78 e sub-issues #79–#86 registrados e vinculados (checklist no épico)
- Documentação sincronizada: `docs/TEST_AUTOMATION_PLAN.md`, `README.md`, `RELEASES.md`, `CHANGELOG.md`
- Rastreabilidade criada/atualizada: `docs/issues/open/issue-{78..86}.{md,json}`
- README — seção "🧪 Testes": adicionada nota de Fase 2 (governança)
- PR: #87 (https://github.com/dmirrha/motorsport-calendar/pull/87)

### Integração — Infra mínima e markers (Issue #85)
- Criado diretório `tests/integration/` (sem `__init__.py`, por convenção)
- Registrado marker `integration` em `pytest.ini` (markers registrados para evitar warnings)
- Documentação atualizada: `tests/README.md`, `docs/tests/overview.md`, `docs/TEST_AUTOMATION_PLAN.md`
- Smoke test `pytest -m integration -q -o addopts=""` executado localmente 3× (<30s): 0.84s, 0.68s, 0.71s
- Arquivados artefatos da issue em `docs/issues/closed/issue-85-2025-08-13.{md,json}`

### Integração — Fixtures e Snapshots ICS (Issue #86)

- Estrutura criada e documentada para testes de integração com snapshots ICS estáveis:
  - Fixtures: `tests/fixtures/integration/scenario_basic.json`
  - Teste: `tests/integration/test_phase2_basic.py` (gera ICS e compara com snapshot normalizado)
  - Utilitário: `tests/utils/ical_snapshots.py` (`normalize_ics_text`, `compare_or_write_snapshot`)
  - Snapshot canônico: `tests/snapshots/phase2/phase2_basic.ics`
- Normalização de snapshots:
  - `UID` normalizado para token fixo; remoção de `DTSTAMP`, `CREATED`, `LAST-MODIFIED`, `SEQUENCE`, `PRODID`; quebras de linha unificadas para `\n`.
- Estabilidade: teste de integração executado 3× localmente sem flakes (<2s cada) com `-o addopts=""` (gate de cobertura desativado no comando). Gate global permanece configurado no projeto.
- Documentação sincronizada: `tests/README.md` (seção de snapshots), `docs/tests/scenarios/phase2_scenarios.md` (cenário básico marcado como concluído).

### Integração — E2E Caminho Feliz (Issue #82)

- Teste: `tests/integration/test_phase2_e2e_happy.py` (gera ICS e compara com snapshot normalizado)
- Snapshot: `tests/snapshots/phase2/phase2_e2e_happy.ics`
- Execução local (sem cobertura/gate; ignorando `pytest.ini`):
  - Comando: `pytest -q -c /dev/null tests/integration/test_phase2_e2e_happy.py -k happy`
  - Run 1: 1 passed in 1.95s
  - Run 2: 1 passed in 2.02s
  - Run 3: 1 passed in 2.00s
- Média: ~1.99s; Estabilidade: 3/3 passes (<30s). Sem flakes.
- Observação: aviso de marker `integration` ocorre apenas com `-c /dev/null`; com `pytest.ini` normal os markers estão registrados.

### Integração — Deduplicação, Ordenação e Consistência (Issue #84)

- Teste: `tests/integration/test_phase2_dedupe_order_consistency.py`
- Fixture: `tests/fixtures/integration/scenario_dedupe_order.json`
- Snapshot: `tests/snapshots/phase2/phase2_dedupe_order_consistency.ics`
- Normalização de snapshots via `tests/utils/ical_snapshots.py` (UID fixo; remoção de `DTSTAMP`, `CREATED`, `LAST-MODIFIED`, `SEQUENCE`, `PRODID`; `\n`).
- Regras validadas: deduplicação por similaridade (nome/categoria/local) e tolerância de horário, ordenação por `DTSTART`, consistência de timezone conforme configuração.
- Estabilidade: 3× local sem flakes (<30s) com snapshots estáveis.
- Documentação sincronizada: `docs/issues/open/issue-84.{md,json}`, `docs/tests/scenarios/phase2_scenarios.md`, `tests/README.md`.

### (movido para 0.5.10) Mocks/Fakes e Fixtures (Issue #79 — Fase 2)

### Adicionado
- **Documentação de Configuração**
  - Criado `CONFIGURATION_GUIDE.md` com documentação detalhada de todas as opções de configuração
  - Adicionadas descrições detalhadas para cada parâmetro do arquivo de configuração
  - Incluídos exemplos e valores padrão para todas as configurações
  - Adicionada seção de solução de problemas para configurações comuns

- **Reestruturação do Projeto**
  - Movido arquivo `config.json` para a pasta `config/`
  - Atualizadas referências ao arquivo de configuração no código-fonte
  - Atualizada documentação para refletir a nova estrutura de diretórios
  - Adicionado suporte a caminhos relativos para o arquivo de configuração
- **Melhorias no Sistema de Logging e Configuração**
  - Implementados códigos de erro estruturados para melhor rastreamento de problemas
  - Adicionado sistema de rotação e limpeza automática de payloads
  - Criado módulo `config_validator.py` para validação centralizada de configurações
  - Adicionada função `validate_silent_periods` para validação de períodos de silêncio
  - Implementados testes unitários abrangentes para validação de configuração
  - Atualizada documentação com exemplos detalhados de configuração
  - Adicionado suporte a mensagens de erro estruturadas com sugestões de correção
  - Melhorado o gerenciamento de arquivos de log e payloads com retenção configurável
  - Adicionada validação de tipos e valores nas configurações
  - Implementada documentação detalhada para todas as opções de configuração

### Corrigido
 - Issue #74 — PytestCollectionWarning: eliminada a coleta indevida de classe auxiliar em `tests/unit/sources/base_source/test_helpers_and_parsers.py` marcando `__test__ = False`.
 - Issue #75 — TomadaTempo `_extract_date`: ajustada a precedência para priorizar ISO completo (`YYYY-MM-DD`/`YYYY/MM/DD`) e evitar matches parciais; testes atualizados em `tests/unit/sources/tomada_tempo/`.
 - Issue #76 — BaseSource `logger=None`: remoção de fallback para `logging.getLogger(__name__)` e proteção de chamadas a métodos customizados via `getattr`, evitando `AttributeError`.

### Manutenção — Testes/Automação
 - Fase 0: revisão do ambiente de testes conforme plano
   - Python 3.11.5 e pip verificados
   - `pytest` 8.4.1 e `pytest-cov` 6.2.1 instalados e presentes em `requirements.txt`
   - Criado `pytest.ini` com `testpaths = tests` e `addopts = --cov=src --cov-report=term-missing`
   - Padronização confirmada: apenas `tests/` como diretório canônico
   - Limpeza: remoção do índice de artefatos gerados (`.pytest_cache/`, `test_results/`, `test_results_github/`, `pytest.log`, `junit.xml`, `report.html`)
   - Documentados cenários em `docs/tests/scenarios/phase0_scenarios.md`
   - Scripts adicionados: `scripts/tests_phase0_inventory.sh`, `scripts/tests_phase0_move_outside_tests.sh`, `scripts/tests_phase0_cleanup.sh`
  - Issue #72 — Documentação de Testes (PR #77 — draft)
    - Criados/atualizados:
      - `docs/tests/overview.md`
      - `docs/tests/scenarios/SCENARIOS_INDEX.md`
      - `docs/tests/scenarios/phase0_scenarios.md`
      - `docs/tests/scenarios/phase1_scenarios.md`
      - `docs/tests/scenarios/phase2_scenarios.md`
    - Matrizes de cenários adicionadas: Fase 0 e Fase 1 (ToDo/Doing/Done com referências a testes/PRs)
    - Rastreabilidade sincronizada: `docs/issues/open/issue-72.{md,json}` e `docs/TEST_AUTOMATION_PLAN.md`
    - CI — Workflow de testes criado em `.github/workflows/tests.yml` (Ubuntu, Python 3.11, cache de pip, pytest com cobertura em `src/` e `sources/`, relatórios `junit.xml`/`coverage.xml`/`htmlcov/`, upload de artefatos, concurrency/cancel-in-progress). Documentação atualizada em `README.md`, `tests/README.md` e `RELEASES.md`. Refs: Issue #72, PR #77.

  - Issue #61 (PR #68 — draft): cobertura de `src/event_processor.py`
    - Cobertura do arquivo: **83%** (meta ≥60% atingida)
    - Novos testes unitários:
      - `tests/unit/processing/test_event_processor_normalization.py`
      - `tests/unit/processing/test_event_processor_dedup.py`
      - `tests/unit/processing/test_event_processor_stats_repr.py`
      - `tests/unit/processing/test_event_processor_pipeline.py`
    - Escopo: normalização (links/data/hora/categoria/local/país/sessão), deduplicação (threshold/tolerância/merge), pipeline (`process_events`), categorias (`_detect_categories`), weekend target (`_detect_target_weekend`), estatísticas e logs
    - Execução local focada no módulo com gate temporário por arquivo (sem afetar gate global do projeto durante estabilização)
  - Issue #62 (PR #69 — draft): cobertura de `src/ical_generator.py`
    - Cobertura do arquivo: **76%**; suíte: **156 passed**; cobertura global: **51.92%**
    - Novos testes: `tests/unit/ical/test_ical_generator_extended.py`
    - Nota: corrigido efeito colateral de monkeypatch global em `pytz.timezone` nos testes de processamento para não interferir nos testes de iCal
   - Fase 1: configuração mínima do Pytest com cobertura e documentação
    - `pytest.ini`: `testpaths=tests`; cobertura em `src/` e `sources/` com `--cov=src --cov=sources`
    - Relatórios: `--cov-report=term-missing:skip-covered`, `--cov-report=xml:coverage.xml`, `--cov-report=html`, `--junitxml=test_results/junit.xml`
    - Gate de cobertura inicial: `--cov-fail-under=40`
    - Marcadores registrados: `unit`, `integration`
    - `tests/conftest.py`: fixture autouse de TZ `America/Sao_Paulo` e ajuste de `sys.path` (raiz e `src/`)
    - `requirements-dev.txt`: `pytest~=8`, `pytest-cov~=5`
    - [x] Documentação: `README.md` (seção "🧪 Testes") e atualização do plano em `docs/TEST_AUTOMATION_PLAN.md`
  - Reorganização da suíte unitária por domínio em `tests/unit/` (sources/tomada_tempo, silent_period, utils)
  - Remoção de hacks de `sys.path` nos testes (uso de `tests/conftest.py`)
  - Criado `tests/README.md` com convenções e estrutura
  - Suíte estável: `45 passed`; cobertura total: 28.75%
  - Issue #64 — P1 (TomadaTempo): módulo `sources/tomada_tempo.py` com cobertura **90%** e **3×** execução estável (<30s). Documentação sincronizada (`docs/TEST_AUTOMATION_PLAN.md`, `RELEASES.md`) e PR #73 atualizado com o resumo do incremento.
  - Issue #64 — P2 (CategoryDetector):
    - Testes adicionados: persistência `save_learned_categories`/`load_learned_categories` com mock de filesystem (`tmp_path`) e estatísticas via `get_statistics`.
    - Ajustes no algoritmo:
      - `detect_category`: priorização determinística de matches exatos sobre fuzzy (evita fuzzy 1.0 sobrepor exato), atualização de stats e aprendizado controlado.
      - `detect_categories_batch`: tenta primeiro `raw_category` isolado; só combina com `name` quando necessário.
    - Métricas: módulo `src/category_detector.py` ~96% de cobertura; suíte **258 passed**, cobertura global **67.78%**; estabilidade confirmada **3×** (<30s).
    - Documentação sincronizada: `docs/TEST_AUTOMATION_PLAN.md`, `CHANGELOG.md`, `RELEASES.md`, `docs/issues/open/issue-64.{md,json}`. PR #73 (draft) atualizado.

  - Issue #64 — P3 (ErrorCodes):
    - Testes adicionados: mapeamentos específicos em `get_error_suggestions`, fallback genérico para códigos desconhecidos e tipos inválidos, e equivalência Enum vs string (`.value`) em `get_error_severity`.
    - Estabilidade: suíte **267 passed** em 3 execuções consecutivas (<30s em todas).
    - Cobertura global atual: **68.04%**. Sem regressões.
    - Documentação sincronizada: `docs/TEST_AUTOMATION_PLAN.md` (P3 marcado como concluído) e `docs/issues/open/issue-64.md` (incremento P3).
  - Issue #64 — P5 (UIManager):
    - Testes adicionados: `tests/unit/ui_manager/test_ui_manager_basic.py` e `tests/unit/ui_manager/test_ui_manager_more.py` cobrindo: progressão de etapas (`start_step_progress`/`show_step`), resumos (`show_event_summary`, `show_events_by_category`), mensagens (`show_success_message`, `show_error_message`, `show_warning_message`, `show_step_result`), geração de iCal (`show_ical_generation`) e instruções de importação (`show_import_instructions`).
    - Estratégia: fakes de console/progresso (sem I/O real), asserts sobre contagem e conteúdo; respeito a flags de UI (cores/ícones/desabilitado).
    - Métricas: `src/ui_manager.py` **100%**; diretório `ui_manager`: **13 testes**; estabilidade **3×** (<30s).
    - Versionamento: bump para `0.5.6` em `src/__init__.py`.
  - Issue #64 — P6 (Logger):
    - Testes adicionados: `tests/unit/logger/test_logger_basic.py` e `tests/unit/logger/test_logger_misc.py` cobrindo inicialização/configuração (handlers/formatters/níveis), rotação de logs, emissão de níveis (success/error/warning/info/debug), `save_payload` (json/html/text) com exceções, `set_console_level`, `get_logger`, resumo/finalização de execução e helpers de domínio (category detection, remoção de duplicados, weekend, iCal, eventos por fonte) com fallbacks de config.
    - Estratégia: isolamento total de I/O real (uso de `tmp_path`), monkeypatch para desabilitar limpezas `_cleanup_old_logs` e `_cleanup_rotated_logs`, e handlers custom para capturar registros.
    - Métricas: módulo `src/logger.py` **83%**; suíte **295 passed**; estabilidade **3×** (<30s) nos testes de logger.
    - Versionamento: bump para `0.5.8` em `src/__init__.py`.
  - Mocks essenciais (issue #48, PR #55):
    - Fixação de timezone (`America/Sao_Paulo`) e aleatoriedade (`random.seed(0)`)
    - Shims de rede: `sources.tomada_tempo.requests.get` e `sources.base_source.requests.Session`
    - Isolamento de filesystem com `tmp_path`/`tmp_path_factory`
    - Variáveis de ambiente com `monkeypatch.setenv`/`delenv`
    - Exemplos: `tests/unit/utils/test_payload_manager.py`, `tests/unit/test_env_vars.py`,
      `tests/unit/sources/base_source/test_make_request.py`, `tests/unit/sources/tomada_tempo/test_parse_calendar_page.py`
  - Gate de cobertura temporário reduzido para 25% em `pytest.ini` (estabilização dos mocks essenciais)
  - Documentação atualizada:
    - `tests/README.md` — seção de mocks essenciais
    - `README.md` — seção “🧪 Testes” com gate 25% e exemplos
    - `RELEASES.md` — nota de próximo patch (não lançado)
   - Fase 1.1 — checklist reorganizada por issues (#59–#64) com sincronismo automático entre plano e issues (docs/issues/open/issue-<n>.{md,json}); rastreabilidade 58–64 adicionada.
   - Issue #59 (PR #66 — draft): testes unitários adicionais para `sources/tomada_tempo.py`; cobertura atual do arquivo: 63%; suíte: 101 passed; cobertura global: 40.64%; documentação sincronizada (`docs/TEST_AUTOMATION_PLAN.md`, `docs/issues/open/issue-59.{md,json}`).
   - Issue #60 (PR #67 — draft): testes de `BaseSource.make_request`
     - Cobertura do arquivo `sources/base_source.py`: 97% (meta ≥60% atingida)
     - Suíte: 132 passed; cobertura global: 38.57%
     - Abrange: erros HTTP 4xx/5xx com retries e logs; backoff exponencial/rate-limit com monkeypatch em `time.sleep` (sem sleeps reais); comportamento seguro quando `logger=None` via `getattr` para métodos customizados; verificação de logs e salvamento de payload; teste opcional de rotação de `User-Agent` na 10ª requisição (determinístico via `random.choice`). Cobertos helpers/parsers: `parse_date_time`, `normalize_event_data`, `filter_weekend_events`, `_setup_session` (headers), `get_streaming_links`.
     - Atualização (branch coverage): cobertos ramos adicionais — exceção em `filter_weekend_events`, limpeza de campos com espaços em `normalize_event_data`, e uso do context manager (`__enter__/__exit__`), `__str__`/`__repr__`.
     - Incrementais entregues: campos ausentes/HTML malformado, slice de `recent_errors` em `get_statistics`, `filter_weekend_events(None)`, formatos adicionais de data/segundos e timezone custom, estabilidade/variação de `_generate_event_id`.
     - Bug corrigido (mantido para importação em lote): `.github/import_issues/open/026-basesource-logger-none-attributeerror.{md,json}` — remoção de fallback para `logging.getLogger(__name__)` quando `logger=None` e proteção de chamadas a métodos customizados com `getattr`.
     - Nota: subtarefas avançadas originalmente listadas para #59 foram replanejadas para as issues #60–#64.
     - Nota: bug de precedência ISO vs BR em `_extract_date()` documentado para importação em lote ao final da Fase 1.1; arquivos mantidos em `.github/import_issues/open/025-tomadatemposource-extract-date-parsing-precedence.{json,md}`.
  - Fase 1 — Cenários (issue #50, PR #57 draft)
    - Criados fixtures HTML compatíveis com o parser `TomadaTempoSource`:
      - `tests/fixtures/html/tomada_tempo_weekend_minimal.html`
      - `tests/fixtures/html/tomada_tempo_weekend_alt_header.html`
      - `tests/fixtures/html/tomada_tempo_weekend_edge_cases.html` (AM/PM, ponto como separador, categoria `Unknown`)
      - `tests/fixtures/html/tomada_tempo_weekend_no_minutes.html` ("8h", "14 horas", "21", "às 10")
      - `tests/fixtures/html/tomada_tempo_weekend_overnight.html` (23:50 → 00:10 em dias distintos)
    - Adicionado teste paramétrico consumindo os fixtures:
      - `tests/unit/sources/tomada_tempo/test_parse_calendar_page_fixtures.py`
      - Inclui assert de presença mínima de categoria `Unknown` para o fixture de edge cases e casos de "sem minutos" e "overnight"
    - Documentação de cenários atualizada:
      - `docs/tests/scenarios/SCENARIOS_INDEX.md`
      - `docs/tests/scenarios/phase1_scenarios.md`
   - Issue #63: Gate de cobertura global elevado para 45%
     - `pytest.ini`: `--cov-fail-under=45`
     - Suíte: **170 passed**; cobertura global: **57.86%**
     - Novos testes:
       - `tests/unit/category/test_category_detector_basic.py`
       - `tests/unit/utils/test_payload_manager_extended.py`
       - `tests/unit/config/test_config_manager_basic.py`
     - Documentação sincronizada: `tests/README.md`, `docs/TEST_AUTOMATION_PLAN.md`, `README.md`, `CHANGELOG.md`, `RELEASES.md`, `docs/issues/open/issue-63.{md,json}`
   - Issue #64 (PR — draft): elevação de qualidade dos testes (qualidade-first)
     - Novos testes para `ConfigManager` (determinísticos, isolados):
       - `tests/unit/config/test_config_manager_merge_and_nested_set.py`
       - `tests/unit/config/test_config_manager_validation_and_streaming.py`
       - `tests/unit/config/test_config_manager_save_errors.py`
     - Escopo coberto: merge profundo com defaults, `get`/`set` com paths aninhados, validação (timezone inválida, diretório inacessível, seções ausentes), `get_streaming_providers` por região, e erros em `save_config` (mkdir/open) com rethrow e logs.
     - Métricas atuais: **191 passed**; cobertura global: **59.15%**; `src/config_manager.py`: **83%**.
     - Observação: sem duplicar testes existentes; alinhado ao guia `.windsurf/rules/tester.md` (determinismo <30s, isolamento de FS/TZ, oráculos claros).
     - Incremento atual: `PayloadManager` e `ICalGenerator`
       - Novos testes:
         - `tests/unit/utils/test_payload_manager_errors.py`
         - `tests/unit/ical/test_ical_generator_branches.py`
       - Ajustes de testes:
         - Construtor de `ICalGenerator`: uso correto do parâmetro `config_manager` no teste
         - `PayloadManager.save_payload`: exceção encapsulada validada como `IOError`
       - Métricas (pós-incremento):
         - Suíte: **205 passed**; cobertura global: **61.52%**
         - `src/utils/payload_manager.py`: **90%**
         - `src/ical_generator.py`: **93%**
       - Próximos passos:
         - Rodar a suíte 3× localmente para confirmar zero flakes
         - Atualizar documentação correlata (`README.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`, `docs/issues/open/issue-64.{md,json}`)
         - Manter PR #73 como draft na branch `chore/issue-64-coverage-80`
  - Fase 1 — Alvos prioritários (issue #49, PR #56)
    - Testes unitários para parsers de data/hora em `sources/tomada_tempo.py` e validações em `sources/base_source.py`
    - Testes unitários para processadores/validadores em `src/event_processor.py` (`_is_event_valid`, `_filter_weekend_events`)
    - Ajuste de casos de borda para refletir precedência atual dos padrões de data
    - Testes adicionais: `ICalGenerator.generate_calendar`/`validate_calendar` e `SilentPeriodManager.log_filtering_summary`
   - Validação: suíte estável `79 passed`; cobertura total 37.00% (2025-08-10)

### Corrigido
- **Issue #23**: Corrigido bug na filtragem de períodos de silêncio
  - Corrigida lógica de filtragem que estava removendo todos os eventos
  - Melhorada a verificação de períodos de silêncio ativos
  - Adicionada validação adicional para garantir que eventos sem data não sejam filtrados incorretamente
  - Atualizada a documentação dos métodos relacionados
- Corrigida chamada incorreta para `show_warning` no UIManager
  - Atualizado para usar o método correto `show_warning_message`
  - Adicionada verificação de existência do método para evitar erros
  - Melhorada a mensagem de aviso exibida ao usuário

### Adicionado
- **Gerenciamento de Arquivos iCal**
  - Implementado sistema de arquivamento automático de arquivos iCal antigos
  - Arquivos antigos são movidos para a subpasta `output/history/`
  - Mantido apenas o arquivo mais recente na pasta raiz de saída
  - Adicionada documentação sobre o sistema de arquivamento
- **Workflow de Issues**: Novo sistema unificado para gerenciamento de issues
  - Estrutura de diretórios padronizada (open/imported/closed/templates)
  - Script de importação automática com suporte a Markdown
  - Templates padronizados para issues
  - Documentação completa do fluxo de trabalho
  - Suporte a metadados e rastreamento de issues relacionadas
  - Processo automatizado para fechamento de issues
  - Integração com o CHANGELOG.md
- **Períodos de Silêncio**: Funcionalidade para filtrar eventos por horário configurável (Issue #22)
  - Classe `SilentPeriod` para gerenciar períodos individuais de silêncio
  - Classe `SilentPeriodManager` para gerenciar múltiplos períodos e filtragem de eventos
  - Configuração flexível de períodos de silêncio via arquivo JSON
  - Suporte a períodos que cruzam a meia-noite
  - Logs detalhados de eventos filtrados por período de silêncio

### Corrigido
- **Issue #20**: Corrigida perda de links de transmissão durante o processamento
  - Implementado tratamento adequado para diferentes formatos de links de streaming
  - Adicionada validação de URLs de streaming
  - Melhorada a formatação de links no arquivo iCal final
  - Adicionada verificação de duplicação de links de streaming
  - Melhor tratamento de erros durante o processamento de links
- Correção na preservação de links de transmissão durante o processamento de eventos (Issue #20)
- Melhoria na normalização de links de streaming para suportar diferentes formatos
- Validação e deduplicação de URLs de streaming
- **Issue #3**: Corrigida detecção de eventos sem data explícita na fonte Tomada de Tempo
  - Implementado suporte ao formato de data "SÁBADO – 02/08/2025"
  - Adicionada extração do contexto da programação do título/URL da página
  - Implementada associação de eventos sem data explícita ao contexto da programação
  - Melhorado suporte a formatos variados de horário (14h30, às 14:30, 14 horas e 30, etc.)
  - Adicionado campo `from_context` para rastreabilidade da origem da data
  - Criado script de teste automatizado para validação das correções
  - Todos os critérios de aceitação da issue atendidos com 100% dos testes passando

### Corrigido
- **Ambiente Python**: Atualizado para Python 3.11.5
  - Resolvido aviso de compatibilidade entre urllib3 v2+ e OpenSSL
  - Configurado ambiente via pyenv para gerenciamento de versões
  - Atualizadas dependências para versões compatíveis
  - Removido arquivo de debug não mais necessário (`debug_weekend_filter.py`)
  - Atualizado `.gitignore` para excluir arquivos de log e dados temporários

### Corrigido
- **Issue #5**: Corrigida detecção do final de semana atual na TomadaTempoSource
  - Corrigido parsing de datas brasileiras (DD/MM/YYYY vs MM/DD/YYYY)
  - Corrigida lógica de timezone para America/Sao_Paulo
  - Implementado filtro por range de datas para incluir apenas eventos do fim de semana vigente
  - Excluídos eventos de finais de semana futuros conforme especificado
  - Adicionados testes automatizados para validação da filtragem

- **Sistema de Logs**: Corrigido acesso seguro às configurações
  - Resolvido erro `'ConfigManager' object is not subscriptable` na limpeza de logs
  - Implementado método `_get_log_config` para acesso consistente às configurações
  - Melhorado tratamento de erros na rotação e limpeza de logs
  - Adicionada verificação de existência de diretórios antes de operações de arquivo

### Melhorado
- **Estrutura do Projeto**: Reorganização dos diretórios para melhor organização
  - Movidos arquivos de configuração para pasta `config/`
  - Atualizados imports para usar caminhos absolutos
  - Melhorada a organização do código fonte
  - Atualizada documentação para refletir a nova estrutura

### Adicionado
- Sistema de versionamento semântico
- Documentação do processo de releases
- Automação de geração de changelog
- Script de debug para análise de filtragem de fim de semana

## [0.1.0] - 2025-08-02
### Adicionado
- Sistema inicial de coleta de eventos de automobilismo
- Suporte a múltiplas fontes de dados
- Geração de arquivos iCal
- Interface de linha de comando
- Sistema de logging avançado
- Rotação automática de logs
- Sistema de importação de issues via JSON

### Melhorado
- Detecção de categorias de automobilismo
- Processamento de datas e fusos horários
- Tratamento de erros e recuperação

### Corrigido
- Problemas na detecção de eventos sem data
- Filtragem incorreta de eventos de fim de semana
- Problemas de codificação de caracteres

---
Nota: Este arquivo é gerado automaticamente. Para adicionar uma nova entrada, use o formato convencional de commit.

## Fix - timezone-aware weekend boundaries (2025-08-09)
- Ajuste em `src/event_processor.py`: normalização e localização de `target_weekend` (datetime/tupla) para timezone da configuração.
- `_detect_target_weekend()` usando `datetime.now(tz)`.
- Pipeline validado; iCal gerado sem erros de timezone.
- test(integration): adicionar parsing TomadaTempoSource e resiliência DataCollector; sem rede; <1s (#105)
