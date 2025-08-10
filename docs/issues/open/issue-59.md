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
- [x] Testes implementados e passando
- [x] Documentação sincronizada

## Métricas
- Cobertura global (unit): 40.64% (gate 25% atendido)
- Cobertura do arquivo `sources/tomada_tempo.py`: 63%
- Execução (unit): 101 passed, ~8.19s

## Escopo entregue e replanejamento
- Escopo concluído em #59: cobertura 63% em `sources/tomada_tempo.py`, 101 passed, cobertura global 40.64% (2025-08-10).
- Subtarefas avançadas replanejadas para #60–#64: matrizes de horários avançadas, categorias/locais ampliados, robustez/erros e ambiguidades documentadas serão tratadas nas issues subsequentes.
- Bug de precedência ISO vs BR em `_extract_date()` documentado para importação em lote ao final da Fase 1.1: `.github/import_issues/open/025-tomadatemposource-extract-date-parsing-precedence.{json,md}`.

## Notas
- Usar fixtures existentes em `tests/fixtures/html/` e adicionar novas conforme necessário.
- Bug de follow-up documentado: precedência ISO vs BR em `_extract_date()` — arquivos criados no importador: `.github/import_issues/open/025-tomadatemposource-extract-date-parsing-precedence.{json,md}`; importação para o GitHub pendente.
