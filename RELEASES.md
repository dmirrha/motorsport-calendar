# Notas de Versão

Este arquivo contém um registro acumulativo de todas as versões lançadas do projeto, com notas detalhadas sobre as mudanças em cada versão.

## Não Lançado
Documentação — Issue #83: documentação e rastreabilidade sincronizadas (sem mudanças de código/funcionalidade).

- Integração — Codecov Hardening (Issue #103): OIDC habilitado nos uploads do Codecov (`use_oidc: true`), varredura automática desabilitada (`disable_search: true`), `codecov.yml` mínimo (statuses informativos `project`/`patch`, `comment: false`) e upload adicional do E2E (flag `e2e`). Documentação atualizada (`tests/README.md`, `docs/TEST_AUTOMATION_PLAN.md`).

- Integração — Codecov Components e Tests Analytics (Issue #104): componentes no `codecov.yml` (inclui `sources/` para evitar cobertura "unassigned"); habilitado Tests Analytics via `codecov/test-results-action@v1` com uploads por job (`tests`/`unit`, `integration`, `e2e_happy`/`e2e`) e `if: always()`; ajustado `pytest` com `-o junit_family=legacy`; links do Codecov corrigidos para slug `/github`; `.gitignore` ampliado para `tmp/`, `coverage_*.xml`, `htmlcov-*/`, `test_results_*/`; documentação atualizada (`README.md`, `tests/README.md`, `docs/TEST_AUTOMATION_PLAN.md`, `docs/issues/open/issue-104.{md,json}`).

- Atualizados: `docs/issues/open/issue-83.{md,json}`, `docs/TEST_AUTOMATION_PLAN.md`, `tests/README.md`, `docs/tests/scenarios/phase2_scenarios.md`, `docs/tests/scenarios/SCENARIOS_INDEX.md`, `CHANGELOG.md`.
- Branch: `tests/issue-83-docs-traceability`.

## Versão 0.5.15 (2025-08-14)
Integração — Deduplicação, Ordenação e Consistência (Issue #84)

- Teste: `tests/integration/test_phase2_dedupe_order_consistency.py`
- Fixture: `tests/fixtures/integration/scenario_dedupe_order.json`
- Snapshot: `tests/snapshots/phase2/phase2_dedupe_order_consistency.ics`
- Normalização: `tests/utils/ical_snapshots.py` (UID fixo; remove `DTSTAMP/CREATED/LAST-MODIFIED/SEQUENCE/PRODID`; quebras `\n`).
- Regras validadas: dedupe por similaridade (nome/categoria/local) com tolerância de horário, ordenação por `DTSTART`, consistência de TZ via configuração.
- Estabilidade local: 3× sem flakes (<30s) com snapshot canônico estável.
- Documentação sincronizada: `CHANGELOG.md`, `RELEASES.md`, `tests/README.md`, `docs/tests/scenarios/phase2_scenarios.md`, `docs/issues/open/issue-84.{md,json}`.

## Versão 0.5.14 (2025-08-14)
Integração — Edge cases ICS (Issue #80)

- Fixtures de integração:
  - `tests/fixtures/integration/scenario_optionals_missing.json`
  - `tests/fixtures/integration/scenario_overnight.json`
  - `tests/fixtures/integration/scenario_timezones.json`
- Testes de integração:
  - `tests/integration/test_phase2_optionals.py`
  - `tests/integration/test_phase2_overnight.py`
  - `tests/integration/test_phase2_timezones.py`
- Snapshots ICS canônicos:
  - `tests/snapshots/phase2/phase2_optionals.ics`
  - `tests/snapshots/phase2/phase2_overnight.ics`
  - `tests/snapshots/phase2/phase2_timezones.ics`
- Normalização de snapshots via `tests/utils/ical_snapshots.py` (UID fixo, remoção de campos voláteis, `\n`).
- Estabilidade: cada teste executado 3× localmente, sem flakes (<30s por execução).
- Documentação sincronizada: `CHANGELOG.md`, `RELEASES.md`, `tests/README.md`, `docs/TEST_AUTOMATION_PLAN.md`.
- Rastreabilidade: `docs/issues/open/issue-80.{md,json}` atualizados.
- Versionamento: bump para `0.5.14` em `src/__init__.py`.

## Versão 0.5.13 (2025-08-13)
Correções de `EventProcessor` e integração E2E com snapshots ICS (Issues #82, #86)

- Correções na normalização do `EventProcessor` (campos/retornos, preservação de `display_name`).
- Ajustes no `ICalGenerator` para preservação de siglas em `display_category` (F1/F2/F3/WEC/WRC/WSBK/NASCAR) e mapeamento consistente para `SUMMARY`, `CATEGORIES` e `X-MOTORSPORT-CATEGORY`.
- Snapshots ICS estáveis (básico e E2E) após normalização via `tests/utils/ical_snapshots.py`.
- Novo job de CI `e2e_happy` em `.github/workflows/tests.yml` executando somente o E2E caminho feliz com cobertura e artefatos dedicados (`coverage_e2e.xml`, `htmlcov-e2e/`, `test_results_e2e/junit.xml`).
- Métricas locais: **339 passed**, **0 failed**; cobertura total **~91%**; E2E (3×): ~1.99s médio.
- Documentação sincronizada: `CHANGELOG.md`, `RELEASES.md`, `tests/README.md`, `docs/TEST_AUTOMATION_PLAN.md`, `docs/tests/scenarios/phase2_scenarios.md`.

## Próximo (Não Lançado)
Manutenção — Testes/Automação (issue #48, PR #55)

- Mocks essenciais para estabilidade da suíte:
  - Timezone fixo (`America/Sao_Paulo`) e aleatoriedade determinística (`random.seed(0)`).
  - Shims de rede: `sources.tomada_tempo.requests.get` e `sources.base_source.requests.Session`.
  - Isolamento de filesystem com `tmp_path`/`tmp_path_factory`.
  - Variáveis de ambiente com `monkeypatch.setenv`/`delenv`.
- Gate de cobertura temporário ajustado para 25% em `pytest.ini` durante estabilização.
- Documentação atualizada:
  - `tests/README.md` — seção de mocks essenciais e exemplos.
  - `README.md` — seção “🧪 Testes” com gate 25% e referências aos exemplos.
  - `CHANGELOG.md` — registro em “Não Lançado”.
  - Suíte estável: `79 passed`; cobertura total: 37.00%

- CI — Workflow de testes (Issue #72, PR #77 — draft)
  - Adicionado `.github/workflows/tests.yml` para execução de `pytest` com cobertura no CI (Ubuntu, Python 3.11)
  - Cache de pip por hash de `requirements*.txt`
  - Relatórios: `junit.xml`, `coverage.xml`, `htmlcov/` enviados como artefatos
  - Concurrency com `cancel-in-progress`
  - Documentação atualizada: `README.md`, `tests/README.md`, `CHANGELOG.md`

### Governança — Fase 2 (Testes Integrados e Validação de ICS)

- Épico: #78; Sub-issues: #79–#86
- Documentação sincronizada: `docs/TEST_AUTOMATION_PLAN.md`, `README.md`, `CHANGELOG.md`, `RELEASES.md`
- Rastreabilidade: `docs/issues/open/issue-{78..86}.{md,json}`
 - PR: #87 (https://github.com/dmirrha/motorsport-calendar/pull/87)

### Integração — Infra mínima e markers (Issue #85)

- Criado diretório `tests/integration/` (sem `__init__.py`, por convenção)
- Registrado marker `integration` em `pytest.ini` (markers registrados para evitar warnings)
 - Documentação atualizada: `tests/README.md`, `docs/tests/overview.md`, `docs/TEST_AUTOMATION_PLAN.md`
 - Smoke test `pytest -m integration -q -o addopts=""` executado localmente 3× (<30s): 0.84s, 0.68s, 0.71s
 - Arquivados artefatos da issue em `docs/issues/closed/issue-85-2025-08-13.{md,json}`

### Integração — Fixtures e Snapshots ICS (Issue #86)

- Estrutura para testes de integração com snapshots ICS estáveis:
  - Fixtures: `tests/fixtures/integration/scenario_basic.json`
  - Teste: `tests/integration/test_phase2_basic.py` (gera ICS e compara com snapshot normalizado)
  - Utilitário: `tests/utils/ical_snapshots.py` (`normalize_ics_text`, `compare_or_write_snapshot`)
  - Snapshot canônico: `tests/snapshots/phase2/phase2_basic.ics`
- Normalização de snapshots:
  - `UID` normalizado para token fixo; remoção de `DTSTAMP`, `CREATED`, `LAST-MODIFIED`, `SEQUENCE`, `PRODID`; quebras de linha unificadas para `\n`.
- Estabilidade: teste de integração executado 3× localmente sem flakes (<2s cada) com `-o addopts=""` (gate de cobertura desativado no comando). Gate global permanece configurado no projeto.
- Documentação sincronizada: `tests/README.md` (seção de snapshots) e `docs/tests/scenarios/phase2_scenarios.md` (cenário básico concluído).

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

### (movido para 0.5.10) Mocks/Fakes e Fixtures (Issue #79 — Fase 2)

### Integração — Job de Integração no CI (Issue #81)

- Adicionado job `integration` ao workflow `.github/workflows/tests.yml` executando `pytest -m integration` com cobertura via `pytest-cov`.
- Artefatos publicados: `test_results_integration/junit.xml`, `coverage_integration.xml`, `htmlcov-integration/`.
- Estratégia consistente com jobs existentes (Ubuntu, Python 3.11, cache pip, `-c /dev/null` para ignorar gates globais).

 - Fase 1.1 — Checklist reorganizada por issues (#59–#64) com sincronismo automático entre plano (`docs/TEST_AUTOMATION_PLAN.md`) e issues (docs/issues/open/issue-<n>.{md,json}); rastreabilidade 58–64 adicionada.

Issue #61 (PR #68 — draft)

- Cobertura de `src/event_processor.py`: **83%** (meta ≥60% atingida)
- Novos testes adicionados:
  - `tests/unit/processing/test_event_processor_normalization.py`
  - `tests/unit/processing/test_event_processor_dedup.py`
  - `tests/unit/processing/test_event_processor_stats_repr.py`
  - `tests/unit/processing/test_event_processor_pipeline.py`
- Escopo coberto: normalização (links/data/hora/categoria/local/país/sessão), deduplicação (threshold/tolerância/merge), pipeline (`process_events`), categorias (`_detect_categories`), weekend target (`_detect_target_weekend`), estatísticas e logs
- Execução local direcionada com `--cov=src/event_processor.py` para aferição do alvo sem afetar gate global durante estabilização

Issue #64 (concluída)

- Elevação de qualidade dos testes (qualidade-first) — ConfigManager
- Novos testes adicionados (determinísticos, isolados):
  - `tests/unit/config/test_config_manager_merge_and_nested_set.py`
  - `tests/unit/config/test_config_manager_validation_and_streaming.py`
  - `tests/unit/config/test_config_manager_save_errors.py`
- Escopo coberto: merge profundo com defaults, `get`/`set` com paths aninhados, validação (timezone inválida, diretório inacessível, seções ausentes), `get_streaming_providers` por região, e erros em `save_config` (mkdir/open) com rethrow e logs
- Métricas atuais: **191 passed**; cobertura global: **59.15%**; `src/config_manager.py`: **83%**
- Observação: sem duplicar testes existentes; alinhado ao guia `.windsurf/rules/tester.md` (determinismo <30s, isolamento de FS/TZ, oráculos claros)
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
  - Conclusão do P1 — `sources/tomada_tempo.py`: cobertura **90%** e **3×** execução estável (<30s); documentação sincronizada (`CHANGELOG.md`, `docs/TEST_AUTOMATION_PLAN.md`) e PR #73 atualizado com resumo.
  - P2 — `src/category_detector.py`:
     - Testes: persistência `save_learned_categories`/`load_learned_categories` (mock FS via `tmp_path`) e estatísticas `get_statistics`.
     - Ajustes: prioridade determinística de matches exatos sobre fuzzy; no batch, tentar `raw_category` antes de combinar com `name`.
     - Métricas: **258 passed**; cobertura global **67.78%**; módulo `category_detector` ~**96%**; estabilidade **3×** (<30s).
     - Docs sincronizadas: `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`, `docs/issues/open/issue-64.{md,json}`. PR #73 (draft) atualizado.

   - P3 — `src/utils/error_codes.py`:
     - Testes: mapeamentos específicos em `get_error_suggestions`, fallback para códigos desconhecidos e tipos inválidos, extração de severidade em `get_error_severity` (Enum vs string via `.value`).
     - Métricas: suíte **267 passed**; módulo `error_codes` > **90%**; cobertura global **68.04%**; estabilidade **3×** (<30s).
     - Docs sincronizadas: `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`, `docs/issues/open/issue-64.{md,json}`; PR #73 (draft) atualizado.
     - Versão: bump para `0.5.4`.

   - P4 — `src/data_collector.py`:
     - Testes mínimos com mocks (sem rede), cobrindo fluxos críticos, concorrência, remoção de fonte e estatísticas.
     - Métricas: módulo ~**67%**; cobertura global **71.98%** (na época); estabilidade **3×** (<30s).
     - Docs sincronizadas: `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`, `docs/issues/open/issue-64.{md,json}`; PR #73 (draft) atualizado.
     - Versão: bump para `0.5.5`.

    - P5 — `src/ui_manager.py`:
      - Testes adicionados: `tests/unit/ui_manager/test_ui_manager_basic.py` e `tests/unit/ui_manager/test_ui_manager_more.py` cobrindo progressão de etapas, resumos, mensagens, geração de iCal e instruções de importação; respeito a flags de UI (cores/ícones/desabilitado) sem I/O real.
      - Métricas: módulo **100%**; estabilidade **3×** (<30s).
      - Docs sincronizadas: `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`, `docs/issues/open/issue-64.{md,json}`; PR #73 (draft) atualizado.
      - Versão: bump para `0.5.6`.
    - P6 — `src/logger.py`:
      - Testes adicionados: `tests/unit/logger/test_logger_basic.py` e `tests/unit/logger/test_logger_misc.py` cobrindo inicialização/configuração (handlers/formatters/níveis), rotação, emissão de níveis, `save_payload` (json/html/text) incluindo exceções, `set_console_level`, `get_logger`, resumo/finalização de execução e helpers de domínio (category detection, remoção de duplicados, weekend, iCal, eventos por fonte) com fallbacks de config.
      - Estratégia: isolamento total de I/O real (uso de `tmp_path`), monkeypatch para desabilitar limpezas `_cleanup_old_logs` e `_cleanup_rotated_logs`, e handlers custom para capturar registros.
      - Métricas: módulo **83%**; suíte **295 passed**; estabilidade **3×** (<30s).
      - Docs sincronizadas: `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`, `docs/issues/open/issue-64.{md,json}`; PR #73 (draft) atualizado.
      - Versão: bump para `0.5.8`.

Issue #59 (PR #66 — draft)

- Testes unitários adicionais para `sources/tomada_tempo.py` (parsers e funções auxiliares)
- Cobertura do arquivo `sources/tomada_tempo.py`: 63%
- Suíte: 101 passed; cobertura global: 40.64%
- Documentação sincronizada: `docs/TEST_AUTOMATION_PLAN.md` e `docs/issues/open/issue-59.{md,json}`
- Nota: subtarefas avançadas originalmente listadas para #59 foram replanejadas para as issues #60–#64.
- Nota: bug de precedência ISO vs BR em `_extract_date()` será importado em lote ao final da Fase 1.1; arquivos mantidos no importador: `.github/import_issues/open/025-tomadatemposource-extract-date-parsing-precedence.{json,md}`.

Issue #60 (PR #67 — draft)

- Testes unitários para `BaseSource.make_request`
 - Cobertura do arquivo `sources/base_source.py`: **97%** (meta ≥60% atingida)
 - Suíte: **132 passed**; cobertura global: **38.57%**
 - Abrange: erros HTTP 4xx/5xx com retries e logs; backoff exponencial/rate-limit com monkeypatch em `time.sleep` (sem sleeps reais); comportamento seguro quando `logger=None` via `getattr` para métodos customizados; verificação de logs e salvamento de payload; teste opcional de rotação de `User-Agent` na 10ª requisição (determinístico via `random.choice`). Helpers/parsers cobertos: `parse_date_time`, `normalize_event_data`, `filter_weekend_events`, `_setup_session` (headers), `get_streaming_links`.
 - Incrementais entregues: campos ausentes/HTML malformado, `recent_errors` slice em `get_statistics`, `filter_weekend_events(None)`, formatos adicionais de data/segundos e timezone custom, estabilidade/variação de `_generate_event_id`.
 - Atualização (branch coverage): cobertos ramos adicionais — exceção em `filter_weekend_events`, limpeza de campos com espaços em `normalize_event_data`, e uso do context manager (`__enter__/__exit__`), `__str__`/`__repr__`.
- Bug corrigido (mantido para importação em lote): `.github/import_issues/open/026-basesource-logger-none-attributeerror.{md,json}` — remoção de fallback para `logging.getLogger(__name__)` quando `logger=None` e proteção de chamadas a métodos customizados com `getattr`.

Issue #62 (PR #69 — draft)

- Cobertura de `src/ical_generator.py`: **76%**
- Suíte: **156 passed**; cobertura global: **51.92%**
- Novos testes: `tests/unit/ical/test_ical_generator_extended.py`
- Observação: corrigido side-effect de monkeypatch global em `pytz.timezone` nos testes de processamento para não interferir nos testes de iCal

Issue #63

- Gate global de cobertura ajustado em `pytest.ini`: `--cov-fail-under=45`
- Suíte: **170 passed**; cobertura global: **57.86%**
- Novos testes adicionados:
  - `tests/unit/category/test_category_detector_basic.py`
  - `tests/unit/utils/test_payload_manager_extended.py`
  - `tests/unit/config/test_config_manager_basic.py`
- Documentação sincronizada: `tests/README.md`, `docs/TEST_AUTOMATION_PLAN.md`, `README.md`, `CHANGELOG.md`, `RELEASES.md`, `docs/issues/open/issue-63.{md,json}`

Fase 1 — Cenários (issue #50, PR #57 draft)

- Fixtures HTML adicionados para o parser `TomadaTempoSource`:
  - `tests/fixtures/html/tomada_tempo_weekend_minimal.html`
  - `tests/fixtures/html/tomada_tempo_weekend_alt_header.html`
  - `tests/fixtures/html/tomada_tempo_weekend_edge_cases.html` (AM/PM, ponto como separador, categoria `Unknown`)
  - `tests/fixtures/html/tomada_tempo_weekend_no_minutes.html` ("8h", "14 horas", "21", "às 10")
  - `tests/fixtures/html/tomada_tempo_weekend_overnight.html` (23:50 → 00:10 em dias distintos)
- Teste paramétrico atualizado consumindo os fixtures:
  - `tests/unit/sources/tomada_tempo/test_parse_calendar_page_fixtures.py`
  - Inclui assert de presença mínima de categoria `Unknown` para o fixture de edge cases
- Documentação atualizada:
  - `docs/tests/scenarios/SCENARIOS_INDEX.md`
  - `docs/tests/scenarios/phase1_scenarios.md`

Prioritários Fase 1 (issue #49, PR #56)

- Testes unitários focados em parsers de data/hora e timezone em `sources/tomada_tempo.py` e validações em `sources/base_source.py`.
- Testes unitários para processadores/validadores em `src/event_processor.py` (`_is_event_valid`, `_filter_weekend_events`).
- Casos de borda adicionados/ajustados para refletir precedência atual dos padrões de data.
 - Documentação e checklists sincronizados em `docs/TEST_AUTOMATION_PLAN.md` e `docs/issues/closed/issue-49.md`.
 - Testes adicionais implementados: `ICalGenerator.generate_calendar`/`validate_calendar` e `SilentPeriodManager.log_filtering_summary`.
 - PR #56 mergeada; issue #49 fechada automaticamente.

## Versão 0.5.10 (2025-08-13)
Mocks/Fakes e Fixtures (Issue #79 — Fase 2)

- Fixtures e fakes para testes determinísticos:
  - `freeze_datetime`: congela `datetime.now()`/`today()` nos módulos relevantes para tempo determinístico nos testes.
  - `fixed_uuid`: substitui `uuid.uuid4()` por UUID fixo para oráculos estáveis.
  - Fakes de HTTP consolidados: `_DummyResponse` e `_DummySession` com `patch_requests_get`/`patch_requests_session` em `tests/conftest.py` (sem rede real).
- Dados de teste:
  - Diretório `tests/data/` criado com `README.md` para artefatos mínimos (HTML/JSON/etc.).
- Documentação:
  - `tests/README.md` atualizado com instruções e exemplos das novas fixtures.
- Estabilidade e performance:
  - Suíte executada 3× consecutivas localmente sem flakes, cada run <30s; métricas atuais: 335 passed; cobertura ~90%.
- Rastreabilidade:
  - Branch de trabalho: `chore/issue-79-fakes-phase2`.
  - Plano e artefatos em `docs/issues/open/issue-79.{md,json}` atualizados.
- PR: #90 (merge via squash)

## Versão 0.5.2 (2025-08-09)
Manutenção — Testes/Automação

- Ajustado ambiente de testes para evitar `ModuleNotFoundError` por imports de `sources` via `tests/conftest.py` (inclusão de caminhos da raiz e `src/`).
- Tornado determinístico o teste de filtragem de fim de semana em `tests/test_tomada_tempo.py` usando data fixa 01/08/2025 com timezone `America/Sao_Paulo`.
- Suíte validada localmente: 37 testes passando.

## Versão 0.5.1 (2025-08-09)
Rollback técnico da branch main para o snapshot exato do commit `9362503`.

### 🔄 Contexto
- PR #34: rollback seguro aplicando restauração completa da árvore para `9362503` em um único commit (histórico preservado).
- Tag de backup criada anteriormente: `backup/pre-rollback-9362503-20250808-222821`.

### 📌 O que mudou
- Revertidas mudanças introduzidas após `9362503` (algumas funcionalidades avançadas de logging, períodos de silêncio, workflow de issues e arquivamento iCal podem não estar disponíveis temporariamente).
- Reaplicado `.gitignore` para evitar versionamento de artefatos de teste e diretórios locais.
- CI/regression-tests não reintroduzido neste release (será revisitado futuramente).

### ✅ Impactos práticos
- O código volta a um estado estável anterior; documentação contém notas de pós-rollback para sinalizar possíveis divergências temporárias.
- Nenhuma migração de dados é necessária.

## Versão 0.5.0 (2025-08-04)
**Melhorias no Sistema de Logging e Configuração**

### 🚀 Novas Funcionalidades

- **Sistema de Logging Aprimorado**
  - Implementados códigos de erro estruturados para melhor rastreamento
  - Adicionado suporte a mensagens de erro com sugestões de correção
  - Melhorada a rotação e limpeza automática de logs
  - Níveis de log configuráveis por saída (console/arquivo)

- **Gerenciamento de Payloads**
  - Rotação automática baseada em quantidade e idade
  - Organização por fonte de dados
  - Configuração flexível de retenção
  - Limpeza inteligente de arquivos antigos

- **Validação de Configuração**
  - Módulo `config_validator.py` para validação centralizada
  - Validação de tipos e valores
  - Mensagens de erro detalhadas
  - Valores padrão sensatos

- **Períodos de Silêncio**
  - Validação robusta de configurações
  - Suporte a múltiplos períodos
  - Configuração flexível de dias e horários

- **Documentação**
  - Exemplos detalhados de configuração
  - Guia de códigos de erro
  - Referência completa das opções
  - Melhores práticas

## Versão 0.4.1 (2025-08-04)
**Correções de Bugs**

### 🐛 Correções de Bugs

- **Correção na Filtragem de Períodos de Silêncio**
  - Corrigido problema que causava a remoção de todos os eventos durante a filtragem
  - Melhorada a lógica de verificação de períodos ativos
  - Adicionada validação para eventos sem data
  - Melhorada a documentação dos métodos de filtragem

- **Correção no UIManager**
  - Atualizada chamada incorreta de `show_warning` para `show_warning_message`
  - Adicionada verificação de existência do método
  - Melhorada a mensagem de aviso exibida ao usuário

## Versão 0.4.0 (2025-08-03)
**Períodos de Silêncio**

### 🔇 Períodos de Silêncio

**Nova Funcionalidade Principal**: Implementação de períodos de silêncio configuráveis para filtrar eventos por horário.

#### Funcionalidades Adicionadas
- **Classe SilentPeriod**: Gerenciamento individual de períodos de silêncio
- **Classe SilentPeriodManager**: Gerenciamento de múltiplos períodos e filtragem de eventos
- **Configuração Flexível**: Períodos configuráveis via arquivo JSON
- **Suporte a Meia-Noite**: Períodos que cruzam a meia-noite (ex: 22:00-06:00)
- **Logs Detalhados**: Registro completo de eventos filtrados
- **Estatísticas**: Contadores de eventos filtrados nas estatísticas de processamento

#### Configuração
```json
{
  "general": {
    "silent_periods": [
      {
        "enabled": true,
        "name": "Noite",
        "start_time": "22:00",
        "end_time": "06:00",
        "days_of_week": ["monday", "tuesday", "wednesday", "thursday", "sunday"]
      }
    ]
  }
}
```

#### Comportamento
- Eventos durante períodos de silêncio são filtrados do arquivo iCal
- Eventos filtrados são registrados nos logs para auditoria
- Resumo de eventos filtrados exibido no terminal
- Não afeta a coleta ou processamento inicial dos eventos

#### Melhorias Técnicas
- Testes unitários completos (15 casos de teste)
- Validação robusta de configuração
- Tratamento de erros e casos extremos
- Integração transparente com o pipeline de processamento existente

#### Issue Relacionada
- **Issue #22**: ✨ Adicionar suporte a período de silêncio para eventos

## Versão 0.3.0 (2025-08-03)
**Correção de Links de Transmissão e Arquivos iCal**

### 🐛 Correções
- **Links de Transmissão**
  - Corrigida a perda de links de transmissão durante o processamento de eventos
  - Implementado tratamento adequado para diferentes formatos de links de streaming
  - Adicionada validação de URLs de streaming
  - Melhorada a formatação de links no arquivo iCal final

- **Arquivos iCal**
  - Implementada rotação automática de arquivos iCal antigos
  - Arquivos antigos são movidos para a subpasta `output/history/`
  - Mantido apenas o arquivo mais recente na pasta raiz de saída
  - Adicionada documentação sobre o sistema de arquivamento

### 🔧 Melhorias Técnicas
- Aprimorado o método `_normalize_streaming_links` para suportar múltiplos formatos de entrada
- Adicionada verificação de duplicação de links de streaming
- Melhor tratamento de erros durante o processamento de links
- Otimização no armazenamento de metadados dos eventos

## Versão 0.2.0 (2025-08-02)
**Workflow Unificado de Gestão de Issues**

### ✨ Novas Funcionalidades
- **Sistema de Importação de Issues**
  - Script `import_issues.py` para criação automática de issues no GitHub
  - Suporte a formatação Markdown completa nos corpos das issues
  - Importação em lote de múltiplas issues
  - Rastreamento de issues importadas

- **Estrutura de Diretórios Padronizada**
  - `open/`: Issues a serem processadas
  - `imported/`: Issues já importadas (com timestamp)
  - `closed/`: Issues resolvidas e fechadas
  - `templates/`: Modelos para novas issues

- **Templates de Issues**
  - Modelo para relatórios de bugs
  - Modelo para solicitações de funcionalidades
  - Documentação detalhada para cada tipo de issue

### 📚 Documentação
- Atualizado `README.md` com instruções detalhadas
- Adicionada seção de boas práticas
- Documentado fluxo completo de trabalho
- Incluídos exemplos de uso

### 🔧 Melhorias Técnicas
- Validação de dados nas issues
- Tratamento de erros aprimorado
- Suporte a metadados avançados
- Rastreamento de issues relacionadas

## Versão 0.1.3 (2025-08-02)
**Melhorias no Sistema de Logs e Configuração**

### 🐛 Correções
- **Sistema de Logs**: Corrigido acesso seguro às configurações
  - Resolvido erro `'ConfigManager' object is not subscriptable` na limpeza de logs
  - Implementado método `_get_log_config` para acesso consistente às configurações
  - Melhorado tratamento de erros na rotação e limpeza de logs
  - Adicionada verificação de existência de diretórios antes de operações de arquivo

### 📚 Documentação
- Adicionado arquivo `LOGGING_AND_CONFIGURATION.md` com documentação detalhada sobre:
  - Configuração de níveis de log
  - Estrutura de diretórios de logs
  - Políticas de retenção e rotação
  - Solução de problemas comuns
  - Boas práticas para uso do sistema de logs

## Versão 0.1.2 (2025-08-02)
**Melhorias na Estrutura do Projeto**

### 🚀 Melhorias
- **Reorganização da Estrutura de Diretórios**:
  - Movidos arquivos de configuração para diretório `config/`
  - Atualizados imports para usar caminhos absolutos
  - Melhorada a organização do código fonte
  - Documentação atualizada para refletir a nova estrutura

## Versão 0.1.1 (2025-08-02)
**Correção Crítica de Filtragem de Fim de Semana**

### 🐛 Correções
- **Issue #5**: Corrigida detecção do final de semana atual na TomadaTempoSource
  - **Problema Resolvido**: Sistema estava incluindo eventos de finais de semana futuros
  - **Correção de Parsing**: Datas brasileiras (DD/MM/YYYY) agora interpretadas corretamente
  - **Correção de Timezone**: Implementado suporte consistente ao timezone America/Sao_Paulo
  - **Filtro Aprimorado**: Implementado filtro por range de datas para limitar coleta ao fim de semana vigente
  - **Testes Adicionados**: Criados testes automatizados para validação da filtragem

### 📋 Detalhes Técnicos
- Método `parse_date_time` na BaseSource atualizado para priorizar formato brasileiro
- Método `collect_events` na TomadaTempoSource corrigido para calcular range correto do fim de semana
- Método `_get_next_weekend` ajustado para retornar sexta-feira do fim de semana atual
- Script de debug criado para análise detalhada da filtragem

### ✅ Critérios de Aceitação Atendidos
- 100% dos eventos exibidos pertencem ao final de semana atual
- Nenhum evento futuro incluído indevidamente
- Transição de semanas funciona corretamente
- Desempenho mantido
- Timezone America/Sao_Paulo respeitado

## Versão 0.1.0 (2025-08-02)
**Versão Inicial**

### 🚀 Novas Funcionalidades
- **Sistema de Coleta de Eventos**
  - Coleta automática de eventos de múltiplas fontes
  - Suporte a diferentes categorias de automobilismo
  - Geração de arquivos iCal para importação no Google Calendar

- **Interface de Linha de Comando**
  - Interface intuitiva com feedback visual
  - Opções de configuração flexíveis
  - Logs detalhados para depuração

- **Sistema de Logging**
  - Rotação automática de arquivos de log
  - Níveis de log configuráveis
  - Retenção personalizável de logs

- **Gerenciamento de Issues**
  - Importação automatizada de issues via JSON
  - Rastreamento de bugs e melhorias
  - Documentação detalhada do processo

### 🛠 Melhorias
- Aprimoramento na detecção de categorias
- Melhor processamento de datas e fusos horários
- Tratamento de erros mais robusto

### 🐛 Correções
- Corrigida detecção de eventos sem data explícita
- Ajustada filtragem de eventos de fim de semana
- Corrigidos problemas de codificação de caracteres

### 📦 Dependências
- Python 3.8+
- Bibliotecas listadas em `requirements.txt`

### 📝 Notas de Atualização
Esta é a versão inicial do projeto, contendo toda a funcionalidade básica para coleta e exportação de eventos de automobilismo.

## Release (2025-08-09)
- Tipo: Fix
- Descrição: Corrige comparações naive/aware ao filtrar eventos por fim de semana.
- Impacto: Geração de iCal sem erros; 75 eventos processados.
- Arquivo: `output/motorsport_events_20250808.ics`
- Notas: Garantir timezone na configuração do projeto.
