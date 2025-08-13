# Fase 2 — E2E Caminho Feliz com Snapshots ICS
Vinculado ao épico: #78

## Descrição
Implementar testes E2E do fluxo completo com comparação de snapshots `.ics`.

## Tarefas
- [ ] Teste E2E: coleta (mock) → processamento → geração de `.ics`
- [ ] Função de normalização de ICS (remover/estabilizar campos voláteis)
- [ ] Snapshot test: comparar saída atual com `tests/snapshots/phase2/*.ics`
- [ ] Registrar tempo de execução em log de teste

## Critérios de Aceite
- [ ] 3× local sem flakes (<30s)
- [ ] Snapshots estáveis e revisados
- [ ] Cobertura do caminho feliz reportada no CI

## Referências
- `docs/TEST_AUTOMATION_PLAN.md` (Fase 2)
