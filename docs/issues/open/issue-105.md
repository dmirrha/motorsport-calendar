# Issue #105 — Aumentar a cobertura de testes integrados para >80%

Referências:
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/105
- Workflow: `.github/workflows/tests.yml`
- Configuração Codecov: `codecov.yml`
- Plano de testes: `docs/TEST_AUTOMATION_PLAN.md`
- Regras do tester: `.windsurf/rules/tester.md`

## Descrição
Aumentar a cobertura de testes integrados para >80%, de forma equalizada entre os módulos/componentes.

## Detalhes da Issue (GitHub)
- Título: Aumentar a cobertura de testes integrados para >80%
- URL: https://github.com/dmirrha/motorsport-calendar/issues/105
- Criada em: 2025-08-14T19:39:14Z
- Atualizada em: 2025-08-14T22:50:54Z

### Corpo da Issue
```
## 🚀 Descrição da Feature
Aumentar a cobertura de testes integrados para >80%

## 📌 Objetivo
Aumentar a cobertura de testes integrados para >80%, de forma equalizada entre todos os módulos

## 💡 Solução Proposta
Analisar a cobertura atual dos testes integrados por módulos ou componentes e listar a ordem de prioridade para criar novos cenários e aumentar a cobertura.

1. Execute os testes E2E e Integrados e grave o percentual de cobertura de cada módulo e global;
2. Monte um plano para priorizar o aumento da cobertura de testes, focado na qualidade dos testes;
3. Peça aprovação do plano;
4. Execute o plano;

## 📊 Impacto Esperado
Testes Integrados com cobertura global acima de 80%
```

## Contexto atual
- Uploads de cobertura por flags (`unit`, `integration`, `e2e`) via `codecov/codecov-action@v4` com OIDC e `disable_search: true`.
- Test Analytics habilitado com `codecov/test-results-action@v1` (JUnit por job) com `use_oidc: true`.
- `codecov.yml` com `component_management` mapeando `src/` e `sources/` para visualizar cobertura por componentes.
- Slug do dashboard Codecov: `/github`.
 - CI publica cobertura no console e no resumo do job: `--cov-report=term:skip-covered` e passo de extração do `line-rate` dos XMLs (unit/e2e/integration) que imprime no log, escreve no `$GITHUB_STEP_SUMMARY` e expõe `steps.coverage_*/outputs.percent`.

## Dados coletados (baseline)
- Cobertura integrada (global): 91,27% (Codecov, commit `2096dd8` na branch `chore/issue-105`).
- Cobertura por componente: disponível no Codecov Components (não consolidado neste documento).
- Módulos mais críticos (baixa cobertura): a coletar.
- Uploads confirmados no Codecov (coverage + test analytics) para `unit`, `integration` e `e2e` via OIDC/flags corretas.

## Plano de resolução (proposto)
1) Executar baseline dos testes Integrados e E2E na branch de trabalho e registrar percentuais global e por componente (usar Codecov Components/flags).
2) Priorizar módulos críticos (parsers, processadores, validadores) conforme as regras do tester (`.windsurf/rules/tester.md`).
3) Implementar cenários integrados mínimos e efetivos (mocks simples quando necessário).
4) Rodar CI, validar evolução de cobertura e ajustar até atingir >80% global para Integrados.
5) Atualizar documentação (README/tests/RELEASES/CHANGELOG) e preparar PR mencionando a issue (#105).

## Plano de priorização (proposta para aprovação)
- Componentes por prioridade:
  1. data-collection (coleta/parsers)
  2. core-processing (transformações/validações)
  3. calendar-generation (geração de artefatos)
  4. configuration (carregamento/flags)
  5. utils (datas/URLs/helpers)
  6. logging (erros/observabilidade)

- Cenários integrados iniciais por componente:
  - data-collection:
    - Parse e normalização com fixtures HTML/JSON; cobertura de HTTP 200/404/429/timeout (retries/backoff).
    - Saída no formato intermediário esperado (schema validado).
  - core-processing:
    - Transformação em objetos de corrida; deduplicação; normalização de fuso horário.
    - Caminho de erro para entradas malformadas (falha isolada, pipeline continua).
  - calendar-generation:
    - Geração de calendário/artefatos (ICS/CSV/JSON quando aplicável) a partir de objetos válidos.
    - Asserções de conteúdo/contagem de eventos e integridade de arquivos.
  - configuration:
    - Carregamento de config/.env; comportamento com flags; erro quando inválido.
  - utils:
    - Parsing de datas (locale/tz) e construtores de URL estáveis.
  - logging:
    - Emissão de logs de erro/aviso quando parser falha; resumo agregado sem dados sensíveis.

- Fluxos E2E:
  - Happy path: fixture mínima -> pipeline completo -> artefatos gerados e válidos; flag e2e enviada ao Codecov.
  - Falhas não letais: erros de rede (retries) e registros malformados são ignorados com warnings; execução termina com sucesso.

- Definição de pronto (DoD) por cenário:
  - Teste integrado reproduz o fluxo ponta-a-ponta do componente.
  - Asserções funcionais + verificação de logs relevantes.
  - Mocks controlados para I/O externo (`requests`/tempo), testes determinísticos.
  - Cobertura refletida em Codecov (flags + components) e CI verde.

- Iterações/metas:
  - Iteração 1: data-collection + core-processing (mínimos viáveis).
  - Iteração 2: calendar-generation + configuration.
  - Iteração 3: utils + logging e hardenings.

### Fase 0 — Alvos prioritários (proposta)
- 1) HTTP/Resiliência de coleta — `src/data_collector.py` e `sources/base_source.py`
  - Erros comuns: timeout, 404, 429, conteúdo vazio/malformed; retries/backoff simples; headers/UA básicos.
  - Testes-alvo: `tests/integration/test_phase2_data_collector_resilience.py` e `tests/integration/test_phase2_sources_parsing_errors.py`.
- 2) Parser de fonte principal — `sources/tomada_tempo.py`
  - Parsing HTML/JSON instável; campos ausentes; normalização para payload intermediário.
  - Teste-alvo: `tests/integration/test_phase2_sources_parsing_errors.py`.
- 3) Processamento/Dedup/Ordenação/TZ — `src/event_processor.py`
  - Deduplicação estável; ordenação determinística; bordas TZ/DST.
  - Teste-alvo: `tests/integration/test_phase2_processor_dedupe_order_tz.py`.
- 4) Geração ICS e casos de borda — `src/ical_generator.py`
  - DTSTART/DTEND; TZIDs; propriedades opcionais; encoding seguro.
  - Teste-alvo: `tests/integration/test_phase2_ical_options_and_edges.py`.
- 5) Períodos silenciosos e filtros — `src/silent_period.py`
  - Aplicação correta de filtros/silent windows no pipeline final.
  - Teste-alvo: `tests/integration/test_phase2_silent_periods_filters.py`.
- 6) Configuração/variantes — `src/config_manager.py` e `src/utils/config_validator.py`
  - Carregamento de env/flags; comportamento por variante; erros claros quando inválido.
  - Teste-alvo: `tests/integration/test_phase2_config_variants_streaming.py`.
- 7) E2E robustez — fluxo ponta-a-ponta
  - Mistura de 404/timeout/malformed → ICS válido (subset) com warnings.
  - Teste-alvo: `tests/integration/test_phase2_e2e_resilience.py`.
- 8) E2E dedupe entre fontes e bordas TZ/DST
  - Consistência de ordenação e dedupe cross-source; bordas de fuso/DST.
  - Testes-alvo: `tests/integration/test_phase2_e2e_dedupe_cross_source.py`, `tests/integration/test_phase2_e2e_tz_dst_boundary.py`.

## Critérios de aceite
- Cobertura de testes integrados global ≥ 80%.
- Cobertura dos módulos prioritários aumentada de forma balanceada.
- CI passando e uploads/analytics no Codecov corretos (flags + components).
- Documentação atualizada.

## Riscos/Observações
- Evitar over-engineering de testes; foco no essencial (parsers/transformações/tratamento de erros comuns).
- Usar mocks básicos (`requests`, timeouts) quando necessário.

## Confirmação
Autorize a execução do baseline de cobertura e a implementação incremental dos testes conforme este plano.

## Plano detalhado (Integration/E2E) — simples e focado em qualidade
Seguindo `/.windsurf/rules/tester.md`: pytest puro, mocks simples, determinismo (<30s), foco em parsers/validadores/processadores, snapshots ICS normalizados.

### Fase 0 — Descoberta guiada por gaps
- Executar cobertura por flag localmente para identificar misses relevantes (parsers/processadores/validadores):
  - Integration: `pytest -q -c /dev/null tests/integration --cov=src --cov=sources --cov-report=xml:coverage_integration.xml`
  - E2E: `pytest -q -c /dev/null tests/integration/test_phase2_e2e_happy.py --cov=src --cov=sources --cov-report=xml:coverage_e2e.xml`
- Priorizar alvos com maior impacto: `sources/tomada_tempo.py`, `src/event_processor.py`, `src/data_collector.py`, `src/ical_generator.py`, `src/config_manager.py`, `src/silent_period.py`.

### Fase 1 — Integration (parsers e coleta resiliente)
- `test_phase2_sources_parsing_errors.py`: 200/404/timeout/HTML malformado, normalização e descarte seguro.
- `test_phase2_data_collector_resilience.py`: lote com sucesso+falhas, agregação parcial, warnings sem crash.
- `test_phase2_config_variants_streaming.py`: variantes de config que afetam fluxo e payload intermediário.

### Fase 2 — Integration (processamento, dedupe/ordem/TZ e ICS)
- `test_phase2_processor_dedupe_order_tz.py`: duplicatas cross-fontes, tolerâncias de horário, ordenação por DTSTART, TZ conforme config.
- `test_phase2_ical_options_and_edges.py`: toggles de campos, overnight, opcionais ausentes; snapshot ICS normalizado + asserts de campos.
- `test_phase2_silent_periods_filters.py`: períodos silenciosos e filtros refletidos no ICS final.

### Fase 3 — E2E (robustez além do happy path)
- `test_phase2_e2e_resilience.py`: mistura de 404/timeout/malformed → ICS válido com subset e warnings.
- `test_phase2_e2e_dedupe_cross_source.py`: dedupe entre fontes e ordenação estável.
- `test_phase2_e2e_tz_dst_boundary.py`: bordas de TZ/DST, DTSTART/DTEND corretos.
- `test_phase2_e2e_invalid_config.py`: config inválida/ausente → erro claro/fail-fast controlado.

### Fase 4 — Polimento e estabilidade
- Rodar 3× local (<30s), ajustar mocks/fixtures para zero flakes.
- Asserts mínimos de logs/warnings quando agregam valor.
- Validar flags/components no Codecov (slug `/github`).
- Atualizar documentação: `CHANGELOG.md`, `RELEASES.md`, `tests/README.md`, `docs/TEST_AUTOMATION_PLAN.md`.

## Checklist de execução (sincronizado com GitHub)
- [x] Baseline: disparar workflow "Tests" (workflow_dispatch) na branch `chore/issue-105` e registrar percentuais Integration/E2E (Codecov flags + Components) — global 91,27% (Codecov, commit `2096dd8`).
- [ ] Fase 0: analisar misses por arquivo/trecho e selecionar 6–8 alvos de maior valor
- [ ] Fase 1: adicionar testes de parsers/HTTP/collector/config (integration)
  - [ ] `test_phase2_sources_parsing_errors.py`
  - [ ] `test_phase2_data_collector_resilience.py`
  - [ ] `test_phase2_config_variants_streaming.py`
- [ ] Fase 2: adicionar testes de processamento/ICS/silent (integration)
  - [ ] `test_phase2_processor_dedupe_order_tz.py`
  - [ ] `test_phase2_ical_options_and_edges.py`
  - [ ] `test_phase2_silent_periods_filters.py`
- [ ] Fase 3: adicionar E2E de robustez (além do happy path)
  - [ ] `test_phase2_e2e_resilience.py`
  - [ ] `test_phase2_e2e_dedupe_cross_source.py`
  - [ ] `test_phase2_e2e_tz_dst_boundary.py`
  - [ ] `test_phase2_e2e_invalid_config.py`
- [ ] Fase 4: estabilidade (3× sem flakes, <30s) e documentação sincronizada
- [ ] Meta: Integration ≥70–80% e E2E ≥70–80%, CI verde e Codecov refletindo evolução
