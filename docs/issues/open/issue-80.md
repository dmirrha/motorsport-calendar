# Issue #80 — Fase 2 — Edge Cases: Overnight, Fusos Múltiplos e Campos Opcionais

Vinculado ao épico: #78

Referências:
- Epic: #78 — Épico Fase 2
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/80
- Plano: `docs/TEST_AUTOMATION_PLAN.md`

## Descrição
Cobrir casos de borda críticos relacionados a tempo e campos opcionais.

## Tarefas
- [ ] Overnight: evento cruzando dia (DTSTART/DTEND corretos)
- [ ] Fusos: validar TZs diferentes e conversões
- [ ] Opcionais: ausência de location/description/links sem quebrar ICS
- [ ] Asserções específicas por campo (UID, SUMMARY, DTSTART, DTEND, TZID)

## Critérios de Aceite
- [ ] Cenários reproduzíveis em `tests/fixtures/integration/`
- [ ] Validações por campo passam 3× local
- [ ] Documentação dos casos em `docs/tests/scenarios/phase2_scenarios.md`

## Progresso
- [ ] Cenários criados em fixtures
- [ ] Validações 3× local sem flakes
- [ ] Documentação sincronizada
