# Issue #84 — Fase 2 — Deduplicação, Ordenação e Consistência

Vinculado ao épico: #78

Referências:
- Epic: #78 — Épico Fase 2
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/84
- Plano: `docs/TEST_AUTOMATION_PLAN.md`

## Descrição
Validar regras de deduplicação, ordenação e consistência de timezone/dados.

## Tarefas
- [x] Testar dedupe por chave de negócio (ex.: data + título + local)
- [x] Ordenação cronológica consistente
- [x] Consistência de timezone entre eventos
- [x] Verificações de contagem e campos obrigatórios

## Critérios de Aceite
- [x] Regras passam 3× local
- [ ] Cobertura acrescentada nos relatórios do CI
- [x] Casos documentados em `phase2_scenarios.md`

## Progresso
- [x] Casos implementados
- [x] 3× local sem flakes
- [x] Documentação sincronizada

## Branch
`tests/issue-84-dedupe-order-consistency`

## PARE (checkpoint)
Antes de implementar os testes, confirmar este plano e artefatos abaixo. Após confirmação, prosseguir com implementação e execução 3×.

## Plano de Resolução
- Coletar eventos simulados e/ou via `DataCollector` (mockado) e processar com `EventProcessor.process_events()`.
- Validar deduplicação via `_deduplicate_events()` e critérios de similaridade:
  - Nome: fuzzy (fuzz.ratio) ≥ `similarity_threshold` (padrão 85).
  - Datetime: diferença ≤ `time_tolerance_minutes` (padrão 30 min).
  - Categoria: fuzzy ≥ `category_similarity_threshold` (padrão 90).
  - Local: fuzzy ≥ `location_similarity_threshold` (padrão 80).
  - Seleção do “melhor” evento por prioridade de fonte/links (`_select_best_event`).
- Ordenação cronológica: verificar eventos finais e ICS por `DTSTART` em ordem crescente; caso divergente, registrar follow-up.
- Timezone: garantir normalização e TZID conforme `config_manager.get_timezone()` e geração no `ICalGenerator`.
- Sanidade: contagem mínima, campos obrigatórios (`name`, `datetime`, `detected_category`).

## Cenários de Teste Alvo (docs/tests/scenarios/phase2_scenarios.md)
- Deduplicação por chave de negócio aproximada (nome/data/hora/local/categoria) com pequenas variações.
- Ordenação cronológica consistente de múltiplos eventos no mesmo dia.
- Consistência de timezone entre BR (America/Sao_Paulo) e UTC/UK.
- Sanidade de contagens e campos obrigatórios.

## Artefatos de Teste
- Teste: `tests/integration/test_phase2_dedupe_order_consistency.py`
- Fixture: `tests/fixtures/integration/scenario_dedupe_order.json`
- Snapshot ICS: `tests/snapshots/phase2/phase2_dedupe_order_consistency.ics`
- Utilitário de normalização de snapshot: `tests/utils/ical_snapshots.py`

## Execução e Estabilidade
- Executar a suíte 3× localmente, < 30s, zero flakes.
- Atualizar `CHANGELOG.md`, `RELEASES.md`, `tests/README.md`, `docs/TEST_AUTOMATION_PLAN.md` e rastreabilidade (`.md|.json`).
- PR deve referenciar: “Closes #84”. Release Drafter acumulará notas.
