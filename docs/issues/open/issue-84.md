# Issue #84 — Fase 2 — Deduplicação, Ordenação e Consistência

Vinculado ao épico: #78

Referências:
- Epic: #78 — Épico Fase 2
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/84
- Plano: `docs/TEST_AUTOMATION_PLAN.md`

## Descrição
Validar regras de deduplicação, ordenação e consistência de timezone/dados.

## Tarefas
- [ ] Testar dedupe por chave de negócio (ex.: data + título + local)
- [ ] Ordenação cronológica consistente
- [ ] Consistência de timezone entre eventos
- [ ] Verificações de contagem e campos obrigatórios

## Critérios de Aceite
- [ ] Regras passam 3× local
- [ ] Cobertura acrescentada nos relatórios do CI
- [ ] Casos documentados em `phase2_scenarios.md`

## Progresso
- [ ] Casos implementados
- [ ] 3× local sem flakes
- [ ] Documentação sincronizada
