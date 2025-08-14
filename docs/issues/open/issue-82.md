# Issue #82 — Fase 2 — E2E Caminho Feliz com Snapshots ICS

Vinculado ao épico: #78

Referências:
- Epic: #78 — Épico Fase 2
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/82
- Plano: `docs/TEST_AUTOMATION_PLAN.md`

## Descrição
Implementar testes E2E do fluxo completo com comparação de snapshots `.ics`.

## Tarefas
- [x] Teste E2E: coleta (mock) → processamento → geração de `.ics`
- [x] Função de normalização de ICS (remover/estabilizar campos voláteis)
- [x] Snapshot test: comparar saída atual com `tests/snapshots/phase2/*.ics`
- [x] Registrar tempo de execução em log de teste

## Critérios de Aceite
- [x] 3× local sem flakes (<30s)
- [x] Snapshots estáveis e revisados
- [ ] Cobertura do caminho feliz reportada no CI

## Plano de Resolução (PARE)
1) Arquitetura do fluxo E2E (caminho feliz):
   - Coleta: `DataCollector.collect_events()` com rede mockada via `patch_requests_session`/`patch_requests_get` de `tests/conftest.py`.
   - Processamento: `EventProcessor.process_events()` para normalizar/filtrar eventos para o fim de semana alvo.
   - Geração ICS: `ICalGenerator.generate_calendar()` produz arquivo `.ics` determinístico (TZ e tempo congelados via `freeze_datetime`).
2) Teste E2E:
   - Arquivo: `tests/integration/test_phase2_e2e_happy.py`.
   - Snapshot: `tests/snapshots/phase2/phase2_e2e_happy.ics` usando `compare_or_write_snapshot()`.
   - Medição de tempo: registrar duração com `time.perf_counter()` no log do teste.
3) Mocks e determinismo:
   - Tempo: usar `freeze_datetime` para fixar `datetime.now()/today()` nos módulos chave.
   - Rede: usar `_DummySession`/`_DummyResponse` para retornar HTML/JSON mínimos da fonte principal (`sources/tomada_tempo`).
4) Critérios de aceite e estabilidade:
   - Rodar local 3× sem flakes (<30s) e validar snapshots.
   - Habilitar cobertura no CI para o caminho feliz.

## Resultados (execução local)
- Comando (sem cobertura/gate, ignorando pytest.ini):
  - `pytest -q -c /dev/null tests/integration/test_phase2_e2e_happy.py -k happy`
- Execuções:
  - Run 1: 1 passed in 1.95s
  - Run 2: 1 passed in 2.02s
  - Run 3: 1 passed in 2.00s
- Média: ~1.99s por execução; Estabilidade: 3/3 passes (sem flakes; <30s).
- Observações:
  - Aviso de marker `integration` desconhecido ocorre apenas porque `-c /dev/null` ignora o `pytest.ini`; no fluxo normal com `pytest.ini` o marker está registrado.
  - Aviso de cache do Pytest não impacta o resultado; execuções determinísticas com fixtures/mocks.

## Progresso
- [x] Teste E2E implementado
- [x] Normalização e snapshots validados 3×
- [ ] Cobertura refletida no CI
