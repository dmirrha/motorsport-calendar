# Fase 2 — CI: Job de Integração, Cobertura e Artefatos
Vinculado ao épico: #78

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

## Referências
- `.github/workflows/tests.yml`
- `docs/TEST_AUTOMATION_PLAN.md` (Fase 2)
