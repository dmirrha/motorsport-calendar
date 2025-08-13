# Issue #81 — Fase 2 — CI: Job de Integração, Cobertura e Artefatos

Vinculado ao épico: #78

Referências:
- Epic: #78 — Épico Fase 2
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/81
- Workflow: `.github/workflows/tests.yml`
- Plano: `docs/TEST_AUTOMATION_PLAN.md`

## Descrição
Integrar a suíte `integration` ao CI com job dedicado, cobertura e artefatos.

## Tarefas
- [ ] Job GitHub Actions executando `pytest -m integration`
- [ ] Upload de artefatos: junit.xml, coverage.xml, htmlcov-integration/
- [ ] Matriz/estratégia consistente com job unitário existente
- [ ] Badge/documentação em `tests/README.md`

## Critérios de Aceite
- [ ] Job executa em PRs e main
- [ ] Artefatos visíveis no run
- [ ] Gate de cobertura informado (não precisa falhar inicialmente)

## Progresso
- [ ] Job criado e executando no CI
- [ ] Artefatos publicados
- [ ] Documentação sincronizada
