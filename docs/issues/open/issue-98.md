# Issue #98 — Integrar Codecov (Fase 1)

Vinculado ao épico: —

Referências:
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/98
- Workflow: `.github/workflows/tests.yml`
- Plano: `docs/TEST_AUTOMATION_PLAN.md`

## Descrição
Integrar Codecov no pipeline de CI com uploads informativos (unit/integration) e badge no README. Gates/status obrigatórios serão avaliados em fases posteriores para evitar instabilidade inicial.

## Tarefas (Fase 1 — agora)
- [x] Adicionar upload via `codecov/codecov-action@v4` no job unit (files: `coverage.xml`, flag: `unit`).
- [x] Adicionar upload via `codecov/codecov-action@v4` no job integration (files: `coverage_integration.xml`, flag: `integration`).
- [x] Adicionar badge do Codecov no `README.md` (branch `main`).
- [x] Documentar em `tests/README.md` como acessar relatórios no Codecov.
- [x] Atualizar `docs/TEST_AUTOMATION_PLAN.md` (Codecov: uploads concluídos; status/gate pendentes).
- [ ] Commitar alterações, abrir PR e solicitar revisão.

## Fora de escopo (Fase 2+)
- [ ] Ativar status/gates no Codecov (project/patch) com limiares graduais.
- [ ] Avaliar `.coveragerc` e exclusões de cobertura (se necessário).
- [ ] Badges por flag (unit/integration) opcionais.

## Critérios de Aceite
- [x] Uploads visíveis no Codecov para os dois jobs (`unit` e `integration`).
- [x] Badge exibido no `README.md`.
- [x] Nenhum gate bloqueando PRs nesta fase (upload não quebra o CI em caso de erro).

## Progresso
- [x] Workflow atualizado com passos de upload no Codecov para `tests` e `integration` (`fail_ci_if_error: false`).
- [x] Badge Codecov adicionado no `README.md`.
- [x] `tests/README.md` atualizado com badge e link para o Codecov.
- [x] `docs/TEST_AUTOMATION_PLAN.md` atualizado (uploads concluídos; gates/status pendentes).
- [ ] Abrir PR na branch `tests/issue-98-codecov-phase1` referenciando esta issue.
