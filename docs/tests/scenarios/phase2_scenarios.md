# Fase 2 — Cenários de Integração

Objetivo: mapear cenários integrados cobrindo fluxo coleta → processamento → iCal, sem dependência externa real quando possível.

## Escopo inicial
- Fluxo mínimo: coleta (mock/fake) → `EventProcessor` → `ICalGenerator`/`utils.generate_ical` → validação `.ics`.
- Mocks/fakes: finais de semana, TZ de configuração, eventos sem data explícita (programação), overnight.
- Dados: respostas estáticas com HTML mínimo e JSONs sintéticos.

## Cenários (status)
- [x] Integração básica com eventos simples (SUMMARY/DTSTART/DTEND/UID/URL/CATEGORIES)
- [ ] Eventos cruzando meia-noite e múltiplos fusos
- [ ] Casos com e sem `url`, `category`, `recurrence`
- [ ] Deduplicação, ordenação e consistência de TZ
- [x] Snapshot `.ics` estável (ver Fase 1.2)

### E2E — Caminho Feliz (Issue #82)
- Teste: `tests/integration/test_phase2_e2e_happy.py`
- Snapshot: `tests/snapshots/phase2/phase2_e2e_happy.ics` (normalizado via `tests/utils/ical_snapshots.py`)
- Execuções locais (sem cobertura/gate; ignorando `pytest.ini` com `-c /dev/null`):
  - Run 1: 1 passed in 1.95s
  - Run 2: 1 passed in 2.02s
  - Run 3: 1 passed in 2.00s
- Média: ~1.99s; Estabilidade: 3/3 passes (<30s). Sem flakes.
- Observações: o aviso de marker `integration` só aparece ao ignorar o `pytest.ini`; no fluxo normal, os markers estão registrados.

## Referências
- Plano: `docs/TEST_AUTOMATION_PLAN.md` (seção Fase 2)
- Overview: `docs/tests/overview.md`
- Índice: `docs/tests/scenarios/SCENARIOS_INDEX.md`
- Issue: #72

- Épico: #78 — Testes Integrados e Validação de ICS
- PR de governança: #87 (https://github.com/dmirrha/motorsport-calendar/pull/87)

