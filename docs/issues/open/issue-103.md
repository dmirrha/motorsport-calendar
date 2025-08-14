# Issue #103 — Codecov Hardening (OIDC, disable_search, codecov.yml, docs)

Vinculado ao épico: —

Referências:
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/103
- Workflow: `.github/workflows/tests.yml`
- Plano: `docs/TEST_AUTOMATION_PLAN.md`

## Descrição
Endurecer a integração do Codecov sem alterar gates/checagens obrigatórias (fase informativa). Objetivo é tornar o upload mais seguro e previsível, e centralizar configuração mínima no `codecov.yml`.

## Escopo
- Ativar autenticação OIDC no `codecov/codecov-action@v4` (`use_oidc: true`).
- Desabilitar varredura automática de arquivos (`disable_search: true`) para enviar apenas o arquivo indicado em `files`.
- Adicionar `codecov.yml` mínimo com statuses informativos (project/patch) e `comment: false`.
- Atualizar documentação: `tests/README.md` e `docs/TEST_AUTOMATION_PLAN.md` (fluxo, flags, link do painel).

## Tarefas
- [x] Atualizar `.github/workflows/tests.yml` com `use_oidc: true` e `disable_search: true` nos passos de upload (jobs `tests`, `integration` e `e2e_happy`).
- [x] Adicionar `codecov.yml` mínimo na raiz (statuses informativos, comment desativado; flags documentadas).
- [x] Atualizar `tests/README.md` (acesso aos relatórios, flags `unit`/`integration`/`e2e`, nota sobre OIDC e `disable_search`).
- [x] Atualizar `docs/TEST_AUTOMATION_PLAN.md` (seção Codecov: hardening aplicado, gates ainda pendentes).
- [ ] Validar novo run do CI com uploads bem-sucedidos (flags preservadas).
- [ ] Abrir PR referenciando "Closes #103" e sincronizar checklist.

## Fora de Escopo (futuro)
- Ativar status/gates obrigatórios no Codecov (project/patch) com limiares graduais.
- Ajustes finos de cobertura (`.coveragerc`) e exclusões.
- Badges por flag (unit/integration) opcionais.

## Critérios de Aceite
- [ ] Uploads continuam funcionando com `flags: unit` (tests) e `flags: integration` (integration).
- [ ] Avisos de busca automática ausentes (apenas o arquivo especificado é enviado).
- [ ] `codecov.yml` presente e carregado; comentários do bot desativados.
- [ ] Documentação atualizada conforme escopo.

## Progresso
- [x] Issue aberta no GitHub (#103) com escopo e critérios.
- [x] Branch criada: `tests/issue-103-codecov-hardening`.
- [x] Arquivos de workflow e docs atualizados.
- [ ] PR aberto e checklist sincronizado.

## Confirmação
Solicito confirmação para aplicar o patch no workflow, criar `codecov.yml` e atualizar a documentação conforme tarefas acima (seguindo `.windsurf/rules/tester.md`).
