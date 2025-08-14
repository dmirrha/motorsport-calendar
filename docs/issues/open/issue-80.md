# Issue #80 — Fase 2 — Edge Cases: Overnight, Fusos Múltiplos e Campos Opcionais

Vinculado ao épico: #78

Referências:
- Epic: #78 — Épico Fase 2
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/80
- Plano: `docs/TEST_AUTOMATION_PLAN.md`

## Descrição
Cobrir casos de borda críticos relacionados a tempo e campos opcionais.

## Tarefas
- [x] Overnight: evento cruzando dia (DTSTART/DTEND corretos)
- [x] Fusos: validar TZs diferentes e conversões
- [x] Opcionais: ausência de location/description/links sem quebrar ICS
- [x] Asserções específicas por campo (UID, SUMMARY, DTSTART, DTEND, TZID)

## Critérios de Aceite
- [x] Cenários reproduzíveis em `tests/fixtures/integration/`
- [x] Validações por campo passam 3× local
- [x] Documentação dos casos em `docs/tests/scenarios/phase2_scenarios.md`

## Progresso
- [x] Cenários criados em fixtures
  - `tests/fixtures/integration/scenario_overnight.json`
  - `tests/fixtures/integration/scenario_timezones.json`
  - `tests/fixtures/integration/scenario_optionals_missing.json`
- [x] Validações 3× local sem flakes (ignorando gate de cobertura com `-c /dev/null`)
  - Testes: 
    - `tests/integration/test_phase2_overnight.py` → snapshot `tests/snapshots/phase2/phase2_overnight.ics`
    - `tests/integration/test_phase2_timezones.py` → snapshot `tests/snapshots/phase2/phase2_timezones.ics`
    - `tests/integration/test_phase2_optionals.py` → snapshot `tests/snapshots/phase2/phase2_optionals.ics`
- [x] Documentação sincronizada (este arquivo e `docs/tests/scenarios/phase2_scenarios.md`)
