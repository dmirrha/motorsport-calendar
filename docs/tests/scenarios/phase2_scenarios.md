# Fase 2 — Cenários de Integração

Objetivo: mapear cenários integrados cobrindo fluxo coleta → processamento → iCal, sem dependência externa real quando possível.

## Escopo inicial
- Fluxo mínimo: coleta (mock/fake) → `EventProcessor` → `ICalGenerator`/`utils.generate_ical` → validação `.ics`.
- Mocks/fakes: finais de semana, TZ de configuração, eventos sem data explícita (programação), overnight.
- Dados: respostas estáticas com HTML mínimo e JSONs sintéticos.

## Cenários (status)
- [ ] Integração básica com eventos simples (SUMMARY/DTSTART/DTEND/UID/URL/CATEGORIES)
- [ ] Eventos cruzando meia-noite e múltiplos fusos
- [ ] Casos com e sem `url`, `category`, `recurrence`
- [ ] Deduplicação, ordenação e consistência de TZ
- [ ] Snapshot `.ics` estável (ver Fase 1.2)

## Referências
- Plano: `docs/TEST_AUTOMATION_PLAN.md` (seção Fase 2)
- Overview: `docs/tests/overview.md`
- Índice: `docs/tests/scenarios/SCENARIOS_INDEX.md`
- Issue: #72

- Épico: #78 — Testes Integrados e Validação de ICS
- PR de governança: #87 (https://github.com/dmirrha/motorsport-calendar/pull/87)
