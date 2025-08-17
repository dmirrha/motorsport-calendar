# Fase 2 — Cenários de Integração

Objetivo: mapear cenários integrados cobrindo fluxo coleta → processamento → iCal, sem dependência externa real quando possível.

## Escopo inicial
- Fluxo mínimo: coleta (mock/fake) → `EventProcessor` → `ICalGenerator`/`utils.generate_ical` → validação `.ics`.
- Mocks/fakes: finais de semana, TZ de configuração, eventos sem data explícita (programação), overnight.
- Dados: respostas estáticas com HTML mínimo e JSONs sintéticos.

## Cenários (status)
- [x] Integração básica com eventos simples (SUMMARY/DTSTART/DTEND/UID/URL/CATEGORIES)
- [x] Eventos cruzando meia-noite e múltiplos fusos
- [ ] Casos com e sem `url`, `category`, `recurrence`
- [x] Deduplicação, ordenação e consistência de TZ
- [x] Snapshot `.ics` estável (ver Fase 1.2)

### Fase 2 — Deduplicação e Ordenação (Issue #84)
- Teste: `tests/integration/test_phase2_dedupe_order_consistency.py`
- Snapshot: `tests/snapshots/phase2/phase2_dedupe_order_consistency.ics`
- Regra de ordenação determinística no ICS: VEVENTs ordenados por `datetime` convertido para UTC (com fallback para datetime naive) e, em seguida, por `display_name`/`name` para desempate (implementado em `src/ical_generator.py::ICalGenerator.generate_calendar`).
- Normalização de snapshots: via `tests/utils/ical_snapshots.py` (UID fixo; remoção de `DTSTAMP`, `CREATED`, `LAST-MODIFIED`, `SEQUENCE`, `PRODID`; quebras `\n`).
- Estabilidade: executado 3× localmente (com `-c /dev/null` para ignorar gates) sem flakes e <30s.

### E2E — Caminho Feliz (Issue #82)
- Teste: `tests/integration/test_phase2_e2e_happy.py`
- Snapshot: `tests/snapshots/phase2/phase2_e2e_happy.ics` (normalizado via `tests/utils/ical_snapshots.py`)
- Execuções locais (sem cobertura/gate; ignorando `pytest.ini` com `-c /dev/null`):
  - Run 1: 1 passed in 1.95s
  - Run 2: 1 passed in 2.02s
  - Run 3: 1 passed in 2.00s
- Média: ~1.99s; Estabilidade: 3/3 passes (<30s). Sem flakes.
- Observações: o aviso de marker `integration` só aparece ao ignorar o `pytest.ini`; no fluxo normal, os markers estão registrados.
 - CI: o job `e2e_happy` no GitHub Actions executa este teste com cobertura e publica artefatos dedicados (`coverage_e2e.xml`, `htmlcov-e2e/`, `test_results_e2e/junit.xml`).

### Fase 2 — Edge Cases (Issue #80)
- Fixtures:
  - `tests/fixtures/integration/scenario_overnight.json`
  - `tests/fixtures/integration/scenario_timezones.json`
  - `tests/fixtures/integration/scenario_optionals_missing.json`
- Testes:
  - `tests/integration/test_phase2_overnight.py` → snapshot `tests/snapshots/phase2/phase2_overnight.ics`
  - `tests/integration/test_phase2_timezones.py` → snapshot `tests/snapshots/phase2/phase2_timezones.ics`
  - `tests/integration/test_phase2_optionals.py` → snapshot `tests/snapshots/phase2/phase2_optionals.ics`
- Execuções locais (ignorando gate de cobertura com `-c /dev/null`):
  - Overnight: 3/3 passes
  - Timezones: 3/3 passes
  - Opcionais: 3/3 passes
- Notas:
  - Para eventos com TZID, o parser `icalendar` pode retornar `datetime` ingênuo ao decodificar; validamos presença de `TZID` e componentes locais de hora/minuto.
  - Para UTC, o ICS pode serializar com sufixo `Z` sem `TZID`; validamos horário local e duração.

### Fase 2 — PayloadManager
- Teste: `tests/integration/test_phase2_payload_manager.py`
- Snapshot: não aplicável (validação por conteúdo/arquivos gerados).
- Escopo: serialização (JSON/HTML/binário), compressão `gzip`, limpeza por idade/quantidade (retenção) e estatísticas agregadas por fonte.
- Estabilidade: execução local estável, sem flakes.
- Cobertura: suíte consolidada ~**91.75%** (Codecov por job/flag).

## Referências
- Plano: `docs/TEST_AUTOMATION_PLAN.md` (seção Fase 2)
- Overview: `docs/tests/overview.md`
- Índice: `docs/tests/scenarios/SCENARIOS_INDEX.md`
- Issue: #72
- Issue: #83 — Documentação e Rastreabilidade

- Épico: #78 — Testes Integrados e Validação de ICS
- PR de governança: #87 (https://github.com/dmirrha/motorsport-calendar/pull/87)
