# Fase 2 — Deduplicação, Ordenação e Consistência
Vinculado ao épico: #78

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

## Referências
- `docs/TEST_AUTOMATION_PLAN.md` (Fase 2)
