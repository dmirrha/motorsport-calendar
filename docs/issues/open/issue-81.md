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
- [x] Job GitHub Actions executando `pytest -m integration`
- [x] Upload de artefatos: junit.xml, coverage.xml, htmlcov-integration/
- [x] Matriz/estratégia consistente com job unitário existente
- [x] Badge/documentação em `tests/README.md`

## Critérios de Aceite
- [ ] Job executa em PRs e main
- [ ] Artefatos visíveis no run
- [ ] Gate de cobertura informado (não precisa falhar inicialmente)

## Progresso
- [x] Job criado no workflow `tests.yml` (job `integration`)
- [ ] Execução validada no CI (aguardando run da branch/PR)
- [x] Artefatos configurados: `test_results_integration/junit.xml`, `coverage_integration.xml`, `htmlcov-integration/`
- [x] Documentação sincronizada em `tests/README.md`
