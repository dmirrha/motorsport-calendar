# Plano de Automação de Testes — Race Calendar

## Objetivo
Estabelecer uma estratégia simples e efetiva para implementar e evoluir testes automatizados, com execução local e no GitHub Actions, incluindo relatórios de cobertura e de execução.

## Escopo e Princípios
- Foco no essencial: parsers, validadores e processadores de dados.
- Pytest como framework principal. Unittest apenas quando necessário.
- Mocks simples para I/O e rede (requests/Session).
- Cobertura pragmática via pytest-cov; metas progressivas.
- Execução local idêntica ao CI (paridade de comandos).

## Tecnologias
- pytest, pytest-cov, pytest-xdist (paralelo opcional)
- unittest.mock (mocks/patches)
- requests, BeautifulSoup (scraping estático)
- actions/setup-python (CI), upload-artifact (artefatos)

## Estrutura do Projeto (relevante a testes)
- Código: `src/motorsport_calendar/` e `sources/`
- Testes: `tests/` (existente, amplo)
- Artefatos: `test_results/`, `junit.xml`, `htmlcov/` (gerados)
- CI: `.github/workflows/tests.yml` (workflow de testes ativo: pytest + cobertura; artefatos junit/coverage/html)
- Job adicional: `e2e_happy` executa apenas `tests/integration/test_phase2_e2e_happy.py` com cobertura, ignorando `pytest.ini` via `-c /dev/null`. Artefatos dedicados: `test_results_e2e/junit.xml`, `coverage_e2e.xml`, `htmlcov-e2e/`.

## Diretrizes de Documentação e Rastreamento
Objetivo: Garantir documentação padrão, simples e completa para explicar a estratégia de testes e permitir rastreabilidade fina das atividades, conforme `.windsurf/rules/tester.md` e políticas do projeto.

## Checklist — Documentação Padrão
- [x] Criar/atualizar visão geral de testes em `docs/tests/overview.md` (estratégia, escopo, como rodar local/CI, estrutura de pastas)
- [x] Criar índice de cenários em `docs/tests/scenarios/SCENARIOS_INDEX.md` (links para cenários por fase)
- [x] Criar/atualizar mapeamento de cenários por fase:
  - [x] `docs/tests/scenarios/phase0_scenarios.md` (inventário e decisões de limpeza)
  - [x] `docs/tests/scenarios/phase1_scenarios.md` (parsers/validação/utils)
  - [x] `docs/tests/scenarios/phase2_scenarios.md` (fluxos de integração e iCal)
- [ ] Atualizar documentações obrigatórias a cada mudança testada:
  - [x] `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md` (atualizados em 2025-08-09 após patch 0.5.2)
- [x] Processo de tracking
  - [x] Toda descoberta/melhoria gera itens no plano em formato checklist, e issues quando aplicável (via GH)
  - [x] Registrar no(s) arquivo(s) de cenários o status (ToDo/Doing/Done) e referência a PRs/Issues

### Progresso — Issue #72
- Branch: `chore/issue-72-docs-tests`
- PR (draft): #77
- Criados/Atualizados: overview; SCENARIOS_INDEX; scenarios de Fase 0, 1 e 2
- Matrizes de cenários adicionadas: Fase 0 e Fase 1 (ToDo/Doing/Done com refs a testes/PRs)
- Rastreabilidade sincronizada: `docs/issues/open/issue-72.{md,json}` e este plano
  - CI: criado `.github/workflows/tests.yml` (Ubuntu, Python 3.11, cache pip, relatórios e artefatos); documentação atualizada em `README.md`, `tests/README.md`, `CHANGELOG.md`, `RELEASES.md`
 - Status: Issue #72 concluída em 2025-08-13; PR #77 mergeada; Épico #58 finalizado.

## Encerramento do Épico #58 — Fase 1.1 (2025-08-13)

- PRs principais: #55, #57, #66, #71, #73, #77
- Issues vinculadas concluídas: #59, #60, #61, #62, #63, #64
- CI de testes ativo: `.github/workflows/tests.yml`
- Documentação sincronizada: `README.md`, `tests/README.md`, `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`
- Resultado: Épico concluído e fechado no GitHub em 2025-08-13

# Fase 0 — Limpeza do Repositório
Objetivo: Remover legados e padronizar a base de testes antes de iniciar as fases seguintes, seguindo a simplicidade descrita em `.windsurf/rules/tester.md`.

## Checklist — Fase 0 (ordem sequencial)
- [x] Inventário de pastas/arquivos de teste
  - [x] Mapear tudo fora de `tests/` (padrões: `test_*.py`, `*_test.py`, `tests*/`, `.pytest_cache`, `htmlcov`, `junit.xml`, `coverage.xml`, `.coverage*`)
  - [x] Identificar scripts temporários em `scripts/` (ex.: `tmp_*tester*.sh`, `tmp_*tests*.sh`)
- [x] Definir padrão canônico
  - [x] Manter apenas `tests/` como pasta oficial de testes
  - [x] Mover para `tests/` arquivos válidos encontrados fora do padrão; excluir duplicatas
- [x] Limpeza do repositório (artefatos gerados)
  - [x] Remover do índice do Git artefatos gerados (manter local), conforme `.gitignore`
  - [x] Garantir `.gitkeep` em pastas vazias necessárias (ex.: `tests/test_results/`)
- [x] Revisão das ferramentas e ambiente de teste (não executar testes ainda)
  - [x] Verificar Python/pip: `python3 --version`, `pip --version`
  - [x] Verificar instalação e versões: `pip show pytest pytest-cov` e `pytest --version` (somente versão)
  - [x] Conferir `requirements.txt`/`requirements-dev.txt` e incluir `pytest`, `pytest-cov` se ausentes
  - [x] Ajustar/confirmar `pytest.ini` básico (`testpaths = tests`, `addopts = --cov=src --cov-report=term-missing`)
  - [x] Validar PATH/ambiente: `which pytest` e conflitos de múltiplas versões
  - [x] Documentar alterações em `CHANGELOG.md` e `REQUIREMENTS.md` (SemVer)
- [x] Remover frameworks/arquivos obsoletos
  - [x] Excluir `nose.cfg`, `tox.ini` e configs antigas não utilizadas (N/A — não encontrados)
  - [x] Unificar configuração em único `pytest.ini` (sem `setup.cfg`/`pyproject.toml` para testes)
- [x] Normalização de nomes/estrutura
  - [x] Garantir padrão de arquivo `test_*.py`
  - [x] Remover `__init__.py` em `tests/` (a menos que necessário)
- [x] Limpeza de artefatos gerados (não versionados; exclusão local é opcional)
  - [x] (N/A) Exclusão local opcional; diretórios/arquivos já ignorados pelo git: `.pytest_cache/`, `htmlcov/`, `.coverage*`, `coverage.xml`, `junit.xml`, `test_results/`
  - [x] Revisar e atualizar `CHANGELOG.md`, `RELEASES.md`, `README.md` e `tests/README.md` para garantir documentação dos mocks essenciais, gate de cobertura temporário e referência à issue #48. (PR #55)
- [x] Scripts temporários e dispersos (N/A — sem scripts temporários; utilitários mantidos)
  - [x] Revisão realizada: manter `scripts/tests_phase0_*` e `scripts/create_patch_0_5_2_pr.sh`; nenhum `tmp_*` encontrado
- [x] CI antigo (N/A — apenas `release-drafter.yml` presente)
  - [x] Nenhum workflow antigo/duplicado encontrado; manteremos `tests.yml` quando criado na Fase 1
- [x] Validação pós-limpeza
  - [x] Executar `pytest -q` para confirmar descoberta apenas em `tests/`
  - [x] Documentar no `CHANGELOG.md` e atualizar `README.md`/`REQUIREMENTS.md` se aplicável
- [x] Documentação e rastreabilidade (Fase 0)
  - [x] Criar/atualizar `docs/tests/scenarios/phase0_scenarios.md` com inventário, decisões e itens derivados
  - [x] Adicionar itens derivados como checklist nesta seção do plano (`docs/TEST_AUTOMATION_PLAN.md`)

  Itens derivados (Fase 0):
  - [x] Mover `./test_issue_3_fixes.py` para `tests/` e padronizar nome (padrão `test_*.py`).
  - [x] Limpeza de artefatos versionados do índice do Git (manter arquivos locais; `.gitignore` já cobre):
    - Diretórios: `.pytest_cache/`, `tests/**/test_results/`, `test_results/`, `test_results_github/`.
    - Arquivos: `.coverage`, `.coverage.*`, `coverage.xml`, `junit.xml` (incluindo variantes sob `tests/**/test_results/`, `test_results/`).
    - Utilizar o script: `scripts/tests_phase0_cleanup.sh` (DRY_RUN por padrão; executar com `DRY_RUN=0` para aplicar).
  - [x] Preparar script de movimentação de testes fora de `tests/`: `scripts/tests_phase0_move_outside_tests.sh` (DRY_RUN por padrão).
  - [x] Criado `tests/conftest.py` ajustando `sys.path` (raiz e `src/`) para evitar `ModuleNotFoundError`.
  - [x] Tornado determinístico o teste de fim de semana em `tests/test_tomada_tempo.py` (data fixa 01/08/2025, TZ `America/Sao_Paulo`).
  - [x] Validação da suíte de testes: `37 passed` em 2025-08-09 (pós-merge Fase 0).
  - [x] SemVer (patch): bump para `0.5.2` registrado em `CHANGELOG.md` e `RELEASES.md`.
  - Relatórios e referências:
    - Relatório de inventário: `test_results/inventory/phase0_inventory_20250809-081647.md`.
    - Cenários Fase 0: `docs/tests/scenarios/phase0_scenarios.md`.

# Fase 1 — Testes Unitários
Objetivo: Cobrir funções críticas de parsing/transformação/validação com testes rápidos, determinísticos e independentes de rede/FS.

## Checklist — Fase 1 (ordem sequencial)
- [x] Configuração mínima do Pytest
  - [x] Criar `pytest.ini`
    - [x] Descoberta em `tests/`
    - [x] Cobertura de `src/` e `sources/`
    - [x] Relatórios: term-missing, XML (coverage.xml), HTML (htmlcov), JUnit (test_results/junit.xml)
    - [x] Fail gate inicial (ex.: `--cov-fail-under=70`), com roadmap para 80%
- [x] Organização de testes
  - [x] Introduzir marcadores `@pytest.mark.unit`
  - [x] Criar/ajustar `conftest.py` com fixtures reutilizáveis (HTML mínimo, fuso horário padrão, relógio congelado)
  - [x] Criar `tests/README.md` com convenções e estrutura-alvo
- [x] Mocks essenciais
  - [x] Definir padrões de patch (compatíveis com shims):
    - [x] `sources.tomada_tempo.requests.get`
    - [x] `sources.base_source.requests.Session`
  - [x] Simular cenários: sucesso, timeout, HTTPError, HTML malformado — ver `tests/unit/sources/base_source/test_make_request.py` e `tests/unit/sources/tomada_tempo/test_parse_calendar_page.py`
  - [x] Tempo e aleatoriedade: fixture TZ-aware (America/Sao_Paulo) e `random.seed(0)` com restauração
  - [x] Isolamento de filesystem: uso de `tmp_path`/`tmp_path_factory` em testes que tocam disco — ver `tests/unit/utils/test_payload_manager.py`
  - [x] Variáveis de ambiente: `monkeypatch.setenv`/`delenv` para configurar/limpar `os.environ` — ver `tests/unit/test_env_vars.py`
  - [x] Validação: Suíte estável: `45 passed`; cobertura total: 28.75% (2025-08-10)
- [x] Alvos prioritários (unit)
  - [x] Parsers de data/hora e timezone em `sources/tomada_tempo.py`
  - [x] Validadores de eventos em `sources/base_source.py`
  - [x] Processadores/validadores de eventos em `src/event_processor.py`
  - [x] Utilitário iCal `src/ical_generator.py` (generate_calendar/validate_calendar)
  - [x] Lógica de filtro de fim de semana em `src/silent_period.py` e resumo `SilentPeriodManager.log_filtering_summary`
  - [x] PR #56 mergeada; rastreabilidade: `docs/issues/closed/issue-49.md`
  - [x] Validação (prioritários): Suíte estável: `79 passed`; cobertura total: 37.00% (2025-08-10)
 
 Status (Fase 1 — issue #50): PR #57 pronta para revisão (ready for review); rastreabilidade sincronizada em `docs/issues/closed/issue-50.{md,json}`.
 - [x] Geração de cenários (unit) — parcial
  - [x] Criar diretório `tests/fixtures/` (se necessário)
  - [x] HTMLs mínimos para parsing (datas/horas, categorias, campos faltantes)
  - [x] Matrizes de casos para horários — parcial
    - [x] 24h (ex.: `08:00`) — coberto por `tomada_tempo_weekend_minimal.html`
    - [x] AM/PM — coberto por `tomada_tempo_weekend_edge_cases.html`
    - [x] Sem minutos — coberto por `tomada_tempo_weekend_no_minutes.html`
    - [x] Overnight — coberto por `tomada_tempo_weekend_overnight.html`
    - Nota: "Naive vs Aware (TZ `America/Sao_Paulo`)" movido para a Fase 1.1
  - [x] Cenários de categoria — parcial: fallback `Unknown` coberto; expansão de categorias ficará para a Fase 1.1.
    - Nota: assert mínimo de `Unknown` no teste paramétrico (edge cases).
  - [x] Casos iCal — movidos para a Fase 2 (integração): PRODID, DTSTART/DTEND com TZ, URL, CATEGORIES, RRULE com `recurrence`.
 - [x] Documentação e rastreabilidade (Fase 1)
  - [x] Criar/atualizar `docs/tests/scenarios/phase1_scenarios.md` (matriz de casos, mapeamentos, status e links para testes)
  - [x] Adicionar itens derivados como checklist nesta seção do plano
     - [x] Criar fixture de edge cases (AM/PM, separador com ponto, categoria desconhecida)
     - [x] Atualizar teste paramétrico para incluir fixture de edge cases e assert de `Unknown`
     - [x] Atualizar `CHANGELOG.md` e `RELEASES.md` com os novos fixtures/testes
     - [x] Criar fixture de sem minutos (8h/14 horas/21/às 10) e adicionar ao teste paramétrico
     - [x] Criar fixture de overnight (23:50→00:10) e adicionar ao teste paramétrico
  - [x] Abrir PR de rascunho do plano de mocks essenciais (#48) — PR #55; rastreabilidade: `docs/issues/open/issue-48.md`

6) Execução e relatórios (local)
- Instalação: `pip install -r requirements.txt && pip install pytest pytest-cov`
- Execução rápida (unit):
  - `pytest -m unit --cov=src --cov=sources --cov-report=term-missing:skip-covered \
     --cov-report=xml:coverage.xml --cov-report=html -q --junitxml=test_results/junit.xml`

7) Critérios de aceite (Fase 1)
- Cobertura global ≥ 70% (meta subir para 80%).
- Testes determinísticos (< 30s localmente em máquina média).
- Relatórios HTML/ XML gerados e versionados apenas como artefatos (não no repo).

---

## Fase 1.1 — Expansão para 80% (Unit)
Objetivo: elevar a cobertura unitária para ≥ 80%, ampliando a matriz de casos e cobrindo ramos não exercitados.

### Checklist — Fase 1.1
*Sincronismo automático: esta checklist espelha as issues #59–#64 no GitHub (corpo e docs/issues/open/issue-<n>.{md,json}).*
*Importação de bugs: será realizada em lote ao final da Fase 1.1; manter arquivos no importador em `.github/import_issues/open/` até lá.*
- [x] #59 — Cobertura de `sources/tomada_tempo.py` ≥ 55% (progresso: 63% em 2025-08-10; 101 passed; cobertura global 40.64%; PR #66 draft; bug de precedência ISO vs BR documentado)
  - [x] Escopo entregue: cobertura 63%, 101 passed, global 40.64% (2025-08-10)
  - [x] Subtarefas avançadas replanejadas para #60–#64 (detalhamento nas respectivas issues)
- [x] #60 — Cobertura de `sources/base_source.py` ≥ 60%
  - [x] Métricas (2025-08-11): `sources/base_source.py` 97% (meta ≥60% atingida); suíte 132 passed; cobertura global 38.57%
  - [x] Escopo coberto: erros HTTP 4xx/5xx com retries e logs; backoff exponencial/rate-limit com monkeypatch em `time.sleep` (sem sleeps reais); comportamento seguro quando `logger=None` via `getattr` para métodos customizados; verificações de logs e salvamento de payload; teste opcional da rotação de `User-Agent` na 10ª requisição (determinístico via `random.choice`)
  - [x] Documentação sincronizada: `tests/README.md` (execução, métricas e destaques), `CHANGELOG.md` (Não Lançado), `RELEASES.md` (Próximo), `docs/issues/open/issue-60.md` (progresso)
  - [x] Bug documentado para importação em lote: `.github/import_issues/open/026-basesource-logger-none-attributeerror.{md,json}` — remoção de fallback para `logging.getLogger(__name__)` quando `logger=None` e guarda com `getattr`
  - [x] Robustez/erros (complementares concluídos)
    - [x] HTML malformado e campos ausentes adicionais (variações realistas)
  - [x] Cobertura por ramos (concluída)
    - [x] Ramos adicionais cobertos: exceção em `filter_weekend_events`, limpeza de campos vazios em `normalize_event_data`, context manager (`__enter__/__exit__`), `__str__`/`__repr__`
 - [x] #61 — Cobertura de `src/event_processor.py` ≥ 60%
   - [x] Métricas (2025-08-11): `src/event_processor.py` 83% (meta ≥60% atingida)
   - [x] Escopo coberto: normalização (links/data/hora/categoria/local/país/sessão), deduplicação (threshold/tolerância/merge), pipeline (`process_events`), categorias (`_detect_categories`), weekend target (`_detect_target_weekend`), estatísticas e logs
   - [x] Documentação sincronizada: `tests/README.md`, `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`, `docs/issues/open/issue-61.md`, `docs/issues/open/issue-61.json`
- [x] #62 — Cobertura de `src/ical_generator.py` ≥ 60%
  - [x] Métricas (2025-08-11): `src/ical_generator.py` 76%; suíte 156 passed; cobertura global 51.92%
  - [x] Novos testes: `tests/unit/ical/test_ical_generator_extended.py`
  - [x] Nota: corrigido side-effect de monkeypatch global em `pytz.timezone` nos testes de processamento
- [x] #63 — Gate global ≥ 45% (`pytest.ini`)
  - [x] Métricas (2025-08-12): suíte **170 passed**; cobertura global **57.86%**; gate aplicado em `pytest.ini` (`--cov-fail-under=45`)
  - [x] Automação local
    - [x] Script/Makefile com alvos `test.unit`, `test.integration`, `coverage`, `report`
  - [x] Fechada via PR #71 (merged em 2025-08-12T00:56:05Z)
- [x] #64 — Documentação e Cenários (sincronismo) — concluída
   - [x] Objetivo final atingido: cobertura unitária ≥ 80% (global 83.35%), matriz ampliada e ramos críticos cobertos
  - [x] Incremento atual: `ConfigManager`
    - Novos testes: `tests/unit/config/test_config_manager_merge_and_nested_set.py`, `tests/unit/config/test_config_manager_validation_and_streaming.py`, `tests/unit/config/test_config_manager_save_errors.py`
    - Escopo: merge profundo com defaults; `get`/`set` aninhados; validação (timezone inválida, diretório inacessível, seções ausentes); `get_streaming_providers` por região; erros em `save_config` (mkdir/open)
    - Métricas: suíte **191 passed**; cobertura global **59.15%**; `src/config_manager.py` **83%**
  - [x] Incremento atual: `CategoryDetector`
    - Novos testes: `tests/unit/category/test_category_detector_normalize_more.py`, `tests/unit/category/test_category_detector_threshold_and_learning.py`, `tests/unit/category/test_category_detector_persistence.py`
    - Escopo: normalização avançada; thresholds/aprendizado; persistência integrada com logger/config stub
  - [x] Incremento atual: `TomadaTempo`
    - Novos testes: `tests/unit/sources/tomada_tempo/test_tomada_tempo_parsing.py`
    - Escopo: parsing determinístico cobrindo variações reais de HTML e formatos de horário
  - [x] Incremento atual: `PayloadManager` e `ICalGenerator`
    - Novos testes:
      - `tests/unit/utils/test_payload_manager_errors.py`
      - `tests/unit/ical/test_ical_generator_branches.py`
    - Ajustes:
      - Construtor de `ICalGenerator`: uso correto do parâmetro `config_manager` no teste
      - `PayloadManager.save_payload`: exceção encapsulada validada como `IOError`
    - Métricas (pós-incremento):
      - Suíte: **205 passed**; cobertura global: **61.52%**
      - `src/utils/payload_manager.py`: **90%**
      - `src/ical_generator.py`: **93%**
    - Próximos passos:
      - Executar suíte 3× para confirmar zero flakes
      - Sincronizar documentação correlata (`README.md`, `RELEASES.md`, `docs/issues/open/issue-64.{md,json}`)
      - Manter PR #73 como draft na branch `chore/issue-64-coverage-80`
  - [x] CHANGELOG/RELEASES atualizados
  - [x] PR (draft) aberta — PR #73: https://github.com/dmirrha/motorsport-calendar/pull/73
  - [x] Incremento atual: `Logger`
    - Testes: `tests/unit/logger/test_logger_basic.py` e `tests/unit/logger/test_logger_misc.py` cobrindo configuração (handlers/formatters/níveis), rotação, emissão de níveis, `save_payload` (json/html/text) com exceções, `set_console_level`, `get_logger`, resumo/finalização de execução e helpers de domínio (category detection, duplicados, weekend, iCal, eventos por fonte), com fallbacks de config.
    - Estratégia: sem I/O real (uso de `tmp_path`), monkeypatch para desabilitar `_cleanup_old_logs`/`_cleanup_rotated_logs`, handlers custom para captura de registros.
    - Métricas: módulo `src/logger.py` **83%**; suíte **295 passed**; cobertura global **83.35%**; estabilidade **3×** (<30s).
    - Versionamento: bump para `0.5.8`.
    - Documentação sincronizada: `CHANGELOG.md`, `RELEASES.md`, `docs/issues/open/issue-64.{md,json}`, `docs/TEST_AUTOMATION_PLAN.md`.

# Fase 1.2 — Fixtures “golden” para ICS (Snapshots)
Objetivo: introduzir snapshots estáveis para validar a saída do `src/ical_generator.py`, garantindo regressão determinística.

## Entregáveis
- Diretório `tests/fixtures/ical/` com arquivos `.ics` canônicos (e/ou JSON normalizado auxiliar).
- Utilitários em `tests/utils/ical_snapshots.py` para normalizar e comparar snapshots.
- Casos em `tests/unit/ical/test_ical_generator_snapshots.py` cobrindo cenários básicos, com alarmes e com timezone.

## Estrutura sugerida
- `tests/fixtures/ical/`
  - `basic_event.ics`
  - `event_with_alarms.ics`
  - `event_with_timezone.ics`
- `tests/utils/ical_snapshots.py`
  - `normalize_ics(text: str) -> str`
  - `strip_volatile_props(text: str, props: list[str]) -> str`
  - `compare_snapshot(actual: str, golden_path: str) -> None`

## Normalização e determinismo
- Remover/normalizar propriedades voláteis: `UID`, `DTSTAMP`, `CREATED`, `LAST-MODIFIED`, `SEQUENCE`, `PRODID` (se dinâmico).
- Fixar TZ e tempo (congelar relógio com fixture; evitar monkeypatch global persistente).
- Normalizar terminadores de linha (CRLF/LF), espaços e ordem relevante quando aplicável.

## Tarefas
- Criar fixtures em `tests/fixtures/ical/` (cenários: simples, com alarmes, com TZ).
- Implementar utilitários de normalização/compare em `tests/utils/ical_snapshots.py`.
- Escrever `tests/unit/ical/test_ical_generator_snapshots.py` exercitando geração e comparação.
- Atualizar documentação: `tests/README.md`, `docs/TEST_AUTOMATION_PLAN.md`, `CHANGELOG.md`, `RELEASES.md`.
- Rastreabilidade: criar issue e PR dedicados (draft com PARE), checklists sincronizados (issue/PR/docs).

## Critérios de aceite
- Comparação por snapshot estável aprovada nos cenários definidos.
- Testes determinísticos (sem flakiness por TZ/tempo/SO).
  - [ ] Conjuntos para validar deduplicação, ordenação e consistência de TZ
- [ ] Validações principais
  - [ ] Contagem de eventos processados
  - [ ] VEVENT: SUMMARY, DTSTART/DTEND, UID, URL, CATEGORIES, RRULE (quando aplicável)
  - [ ] Consistência de timezone (naive → localized conforme config)
  - [ ] Criar/atualizar `docs/tests/scenarios/phase2_scenarios.md` (fluxos, casos, status e links)
  - [x] Governança Fase 2: épico #78 e sub-issues #79–#86 criados
  - [x] Link do épico: https://github.com/dmirrha/motorsport-calendar/issues/78
  - [x] Sincronismo de documentos: `README.md`, `docs/TEST_AUTOMATION_PLAN.md`, `CHANGELOG.md`, `RELEASES.md`
  - [x] PR de governança: #87 (https://github.com/dmirrha/motorsport-calendar/pull/87)
  - [x] Adicionar itens derivados como checklist nesta seção do plano
    - [x] `tests/README.md`: comandos `pytest -m integration` e referências a cenários Fase 2 e PR #87
    - [x] `docs/tests/scenarios/phase2_scenarios.md`: referências ao épico #78 e PR #87
    - [x] `docs/tests/overview.md`: referência à execução de integração e ao PR #87
  - [ ] Automação CI (final da Fase 2)
   - [ ] GitHub Actions: workflow para unit/integration com `pytest` + `pytest-cov`
   - [ ] Upload de artefatos (HTML/ XML) e envio ao Codecov
   - [ ] Codecov: upload de `coverage.xml`, status check e badge no `README.md`
   - [ ] Gatilhos em PRs e pushes, gate por status de cobertura

### Progresso — Issue #80 (edge cases ICS)

- Fixtures de integração:
  - `tests/fixtures/integration/scenario_optionals_missing.json`
  - `tests/fixtures/integration/scenario_overnight.json`
  - `tests/fixtures/integration/scenario_timezones.json`
- Testes de integração:
  - `tests/integration/test_phase2_optionals.py`
  - `tests/integration/test_phase2_overnight.py`
  - `tests/integration/test_phase2_timezones.py`
- Snapshots canônicos:
  - `tests/snapshots/phase2/phase2_optionals.ics`
  - `tests/snapshots/phase2/phase2_overnight.ics`
  - `tests/snapshots/phase2/phase2_timezones.ics`
- Normalização via `tests/utils/ical_snapshots.py` (UID fixo, remoção de `DTSTAMP/CREATED/LAST-MODIFIED/SEQUENCE/PRODID`, quebras `\n`).
- Estabilidade local: cada teste 3× sem flakes (<30s por execução; `-o addopts=""` quando necessário).
- Documentação sincronizada: `CHANGELOG.md`, `RELEASES.md`, `tests/README.md`, este plano.
- Rastreabilidade: `docs/issues/open/issue-80.{md,json}` atualizados.
- Versionamento: bump para `0.5.14` em `src/__init__.py`.
- Próximos passos: criar branch remota `tests/issue-80-edge-cases`, abrir PR referenciando a Issue #80, atualizar checklist na issue com links/versão.

## Execução Local — Guia Rápido
- Instalação:
```
pip install -r requirements.txt
pip install pytest pytest-cov
```
- Unit:
```
pytest -m unit --cov=src --cov=sources --cov-report=term-missing:skip-covered \
  --cov-report=xml:coverage.xml --cov-report=html \
  --junitxml=test_results/junit.xml
```
- Integração:
```
pytest -m integration --cov=src --cov=sources --cov-append \
  --cov-report=term-missing:skip-covered --cov-report=xml:coverage.xml \
  --cov-report=html --junitxml=test_results/junit.xml
```

## GitHub Actions — Workflow Sugerido (`.github/workflows/tests.yml`)
```yaml
name: Tests
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Pytest (unit)
        run: |
          pytest -m unit --cov=src --cov=sources \
            --cov-report=term-missing:skip-covered \
            --cov-report=xml:coverage.xml --cov-report=html \
            --junitxml=test_results/junit.xml
      - name: Pytest (integration)
        run: |
          pytest -m integration --cov=src --cov=sources --cov-append \
            --cov-report=term-missing:skip-covered --cov-report=xml:coverage.xml \
            --cov-report=html --junitxml=test_results/junit.xml || true
      - name: Upload coverage HTML
        uses: actions/upload-artifact@v4
        with:
          name: htmlcov
          path: htmlcov/
          if-no-files-found: ignore
      - name: Upload JUnit report
        uses: actions/upload-artifact@v4
        with:
          name: junit
          path: test_results/junit.xml
          if-no-files-found: ignore
      - name: E2E Happy Path
        run: |
          pytest -q -c /dev/null tests/integration/test_phase2_e2e_happy.py -k happy \
            --cov=src --cov=sources \
            --cov-report=term-missing:skip-covered \
            --cov-report=xml:coverage_e2e.xml \
            --cov-report=html:htmlcov-e2e \
            --junitxml=test_results_e2e/junit.xml
      - name: Upload E2E coverage HTML
        uses: actions/upload-artifact@v4
        with:
          name: htmlcov-e2e
          path: htmlcov-e2e/
          if-no-files-found: ignore
      - name: Upload E2E JUnit report
        uses: actions/upload-artifact@v4
        with:
          name: junit-e2e
          path: test_results_e2e/junit.xml
          if-no-files-found: ignore
```
Notas:
- `|| true` no bloco de integração é opcional se a fase 2 ainda não estiver completa; remova quando estabilizar.
- Para gates de cobertura no CI, adicione `--cov-fail-under=<meta>`.

## Convenções e Boas Práticas
- Nomes de testes descritivos: `test_<comportamento>_<cenário>_<resultado>`.
- Um comportamento por teste quando possível.
- Fixtures pequenas e reutilizáveis; evitar hierarquias complexas.
- Mocks só quando necessário para remover efeitos colaterais (rede/FS/tempo).

## Roadmap de Evolução
1. Subir `--cov-fail-under` de 70% → 80% após estabilização da Fase 2.
2. Paralelizar testes com `pytest -n auto` (quando estável e sem condições de corrida).
3. Opcional: adicionar `pytest-rerunfailures` para flakies pontuais.

 ## Backlog Prioritário — Issue #64 (trabalho 1 a 1)
 Seguindo `.windsurf/rules/tester.md` e a diretriz qualidade-first, vamos atacar módulos que hoje estão abaixo da meta de 80% de cobertura, priorizando parsers/validadores/processadores. Marque cada item ao concluir.
 
 - [x] P1 — `sources/tomada_tempo.py` (Concluído: cobertura 90% e 3× estável <30s; docs/PR sincronizados — refs #64, PR #73)
   - Foco: `_extract_time`, `_extract_date`, `_extract_event_from_element`, `_extract_streaming_links`, `_extract_official_url`, `filter_weekend_events` (herdado).
   - Casos: ISO vs BR (precedência), sem data (usar contexto), AM/PM (ignorado), overnight (sem ajuste na hora), separadores variados, HTML malformado.
   - Caminho: `sources/tomada_tempo.py` | Tests: `tests/unit/sources/tomada_tempo/`

 - [x] P2 — `src/category_detector.py` (Concluído: cobertura ~96% e 3× estável <30s; docs/PR sincronizados — refs #64, PR #73)
  - Foco: fallback "Unknown", conflitos de regras (prioridade determinística), métricas/estatísticas (se expostas), persistência save/load (mock de FS).
  - Caminho: `src/category_detector.py` | Tests sugeridos: `tests/unit/category/`

- [x] P3 — `src/utils/error_codes.py` (Concluído: módulo >90% e 3× estável <30s; docs/PR sincronizados — refs #64, PR #73)
  - Foco: mapeamentos específicos, mensagens de fallback para códigos desconhecidos, tipos inválidos.
  - Caminho: `src/utils/error_codes.py` | Tests: `tests/unit/utils/test_error_codes.py`
  - Métricas: suíte **267 passed**; cobertura global **68.04%**; estabilidade **3×** (<30s).

- [x] P4 — `src/data_collector.py` (Concluído: módulo ~67% e 3× estável <30s; docs/PR sincronizados — versão 0.5.5; refs #64, PR #73)
  - Foco mínimo de valor: fluxos críticos isolados com mocks (sem rede), erros comuns (timeout/404), validação de dados obrigatórios.
  - Caminho: `src/data_collector.py` | Tests: `tests/unit/data_collector/`

- [x] P5 — `src/ui_manager.py` (Concluído: módulo 100% e 3× estável <30s; docs/PR sincronizados — versão 0.5.6; refs #64, PR #73)
  - Foco: comportamento básico sem I/O real, ramos de mensagens e estados simples.
  - Caminho: `src/ui_manager.py` — 100% (3× estável)
  - Tests: `tests/unit/ui/`

- [x] P6 — `src/logger.py` (Concluído: módulo 83% e 3× estável <30s; docs/PR sincronizados — versão 0.5.8; refs #64, PR #73)
  - Foco: configuração de handlers/formatters mais usados, ramos de nível de log.
  - Caminho: `src/logger.py` | Tests: `tests/unit/logger/`

Notas rápidas:
- Critérios de qualidade: 3× sem flakes (<30s), documentação sincronizada (CHANGELOG, RELEASES, TEST_AUTOMATION_PLAN, docs/issues/open/issue-64.{md,json}).
- Após cada incremento testado: atualizar PR draft #73 (branch `chore/issue-64-coverage-80`) referenciando a Issue #64.

## Referências
- Guia de simplicidade: `.windsurf/rules/tester.md`.
- Código relevante: `sources/`, `src/motorsport_calendar/`, `tests/`.
- Padrões de patch (shims já mapeados): `sources.tomada_tempo.requests.get`, `sources.base_source.requests.Session`.
