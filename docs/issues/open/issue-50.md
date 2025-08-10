# Issue #50 — Fase 1: Geração de cenários (unit)

Referências:
- Epic: #45 — Automação de testes
- Milestone: #2 — Automação de testes - Fase 1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/50

## Objetivo
Criar fixtures/cenários reutilizáveis para testes unitários, com dados minimamente realistas, cobrindo parsers, validadores e utilitários, e documentar os cenários para reuso em fases seguintes.

## Plano de Execução (Checklist)
- [x] Criar diretório `tests/fixtures/` (se necessário)
- [x] HTMLs mínimos para parsing (datas/horas, categorias, campos faltantes)
 - [x] Matrizes de casos para horários
   - [x] 24h (ex.: `08:00`) — coberto por `tomada_tempo_weekend_minimal.html`
   - [x] AM/PM — coberto por `tomada_tempo_weekend_edge_cases.html`
   - [x] Sem minutos — coberto por `tomada_tempo_weekend_no_minutes.html`
   - [x] Overnight — coberto por `tomada_tempo_weekend_overnight.html`
   - [ ] Naive vs Aware (TZ `America/Sao_Paulo`)
- [ ] Cenários de categoria: conhecidas vs fallback `Unknown`
- [ ] Casos iCal: PRODID, DTSTART/DTEND com TZ, URL, CATEGORIES, RRULE com `recurrence`

### Documentação e rastreabilidade (Fase 1)
- [x] Criar/atualizar `docs/tests/scenarios/phase1_scenarios.md` (matriz de casos, mapeamentos, status e links para testes)
 - [x] Adicionar itens derivados como checklist nesta seção do plano (`docs/TEST_AUTOMATION_PLAN.md`)

## PARE — Autorização
- Implementação requer confirmação. A PR será aberta como draft com este gate indicado apenas no corpo/labels/estado (título limpo e objetivo).

## Progresso
- [x] Branch criada: `chore/tests-scenarios-unit-50-20250810`
- [x] Checklists sincronizadas com `docs/TEST_AUTOMATION_PLAN.md` (seção “Geração de cenários (unit)”).
 - [x] PR (draft) aberta: #57 — https://github.com/dmirrha/motorsport-calendar/pull/57
 - [x] Fixture de edge cases criado: `tests/fixtures/html/tomada_tempo_weekend_edge_cases.html` (AM/PM, ponto como separador, categoria `Unknown`)
 - [x] Teste paramétrico atualizado com assert mínimo de `Unknown` para o fixture de edge cases: `tests/unit/sources/tomada_tempo/test_parse_calendar_page_fixtures.py`
 - [x] Documentação atualizada: `docs/tests/scenarios/phase1_scenarios.md` e `CHANGELOG.md` (Não Lançado)
 - [x] Fixture "sem minutos" criado: `tests/fixtures/html/tomada_tempo_weekend_no_minutes.html` ("8h", "14 horas", "21", "às 10")
 - [x] Fixture "overnight" criado: `tests/fixtures/html/tomada_tempo_weekend_overnight.html` (23:50 → 00:10 com datas distintas)
 - [x] Teste paramétrico atualizado para incluir `no_minutes` e `overnight`: `tests/unit/sources/tomada_tempo/test_parse_calendar_page_fixtures.py`

## Notas
- Reutilizar mocks essenciais: rede (requests/Session), tempo/TZ, `tmp_path`, `os.environ`.
- Manter documentação e rastreabilidade: atualizar CHANGELOG/RELEASES/README/tests/README conforme necessário a cada marco.
