# Issue #59 — Fase 1.1: Cobertura de sources/tomada_tempo.py ≥55% (paramétricos e edge)

Referências:
- Epic: #58 — Fase 1.1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/59

## Objetivo
Elevar cobertura de `sources/tomada_tempo.py` para ≥55% com testes paramétricos e cenários de borda.

## Plano de Execução
1. Ampliar testes paramétricos com novos fixtures (timezone limítrofe, horários duplicados, sessões canceladas/adiadas)
2. Exercitar ramificações de parsing (sem minutos, overnight, campos ausentes/inválidos)
3. Garantir mocks de rede (requests) e TZ fixa (America/Sao_Paulo)
4. Validar determinismo (<30s local) e registrar tempo
5. Atualizar `docs/tests/scenarios/phase1_scenarios.md` e `SCENARIOS_INDEX.md`
6. Documentar no `tests/README.md` os novos casos
7. Atualizar `docs/TEST_AUTOMATION_PLAN.md` e CHANGELOG/RELEASES

## PARE — Autorização
- PR inicia em draft até validação deste plano.

## Progresso
- [x] Branch criada
- [x] PR (draft) aberta
- [ ] Testes implementados e passando
- [ ] Documentação sincronizada

## Notas
- Usar fixtures existentes em `tests/fixtures/html/` e adicionar novas conforme necessário.
