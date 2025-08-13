# Issue #82 — Fase 2 — E2E Caminho Feliz com Snapshots ICS

Vinculado ao épico: #78

Referências:
- Epic: #78 — Épico Fase 2
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/82
- Plano: `docs/TEST_AUTOMATION_PLAN.md`

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

## Progresso
- [ ] Teste E2E implementado
- [ ] Normalização e snapshots validados 3×
- [ ] Cobertura refletida no CI
