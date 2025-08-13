# Issue #72 — Fases 0/1/1.1/1.2: Documentação de Testes (overview, cenários e tracking)

Referências:
- Epic: #58 — Fase 1.1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/72
- Relacionadas: #61, #62, #63, #64

## Objetivo
Consolidar e manter atualizadas as documentações de testes referentes às fases 0, 1, 1.1 e 1.2, incluindo visão geral, cenários por fase e processo de tracking.

## Checklist — Documentação Padrão
- [x] Criar/atualizar visão geral de testes em `docs/tests/overview.md` (estratégia, escopo, como rodar local/CI, estrutura de pastas)
- [x] Criar índice de cenários em `docs/tests/scenarios/SCENARIOS_INDEX.md` (links para cenários por fase)
- [ ] Criar/atualizar mapeamento de cenários por fase:
  - [x] `docs/tests/scenarios/phase0_scenarios.md` (inventário e decisões de limpeza)
  - [x] `docs/tests/scenarios/phase1_scenarios.md` (parsers/validação/utils)
  - [x] `docs/tests/scenarios/phase2_scenarios.md` (fluxos de integração e iCal)
- [ ] Atualizar documentações obrigatórias a cada mudança testada:
  - [x] `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md` (atualizados em 2025-08-09 após patch 0.5.2)
- [ ] Processo de tracking
  - [x] Toda descoberta/melhoria gera itens no plano em formato checklist, e issues quando aplicável (via GH)
  - [x] Registrar no(s) arquivo(s) de cenários o status (ToDo/Doing/Done) e referência a PRs/Issues

## PARE — Autorização
- PR inicia em draft até validação deste plano.

## Progresso
- [x] Branch criada (`chore/issue-72-docs-tests`)
- [x] PR (draft) aberta — PR #77: https://github.com/dmirrha/motorsport-calendar/pull/77
- [x] Documentações criadas/atualizadas conforme checklist
- [ ] Rastreabilidade sincronizada (issues/PRs, docs locais, CHANGELOG/RELEASES, TEST_AUTOMATION_PLAN)

## Plano de Resolução
- Criar estrutura `docs/tests/` e arquivos:
  - `docs/tests/overview.md`
  - `docs/tests/scenarios/SCENARIOS_INDEX.md`
  - `docs/tests/scenarios/phase0_scenarios.md`
  - `docs/tests/scenarios/phase1_scenarios.md`
  - `docs/tests/scenarios/phase2_scenarios.md`
- Conteúdo mínimo e simples, seguindo `.windsurf/rules/tester.md`:
  - Overview: estratégia, escopo, como rodar local/CI, estrutura de pastas
  - SCENARIOS_INDEX: links para cenários por fase
  - PhaseX: lista de cenários por módulo, status (ToDo/Doing/Done) e refs de PR/Issues
- Atualizar `docs/TEST_AUTOMATION_PLAN.md` com progresso da `#72`
- Abrir PR em draft referenciando `#72`
- PARE para confirmação antes de alterar documentação

## Critérios de Aceite
- Documentação padrão criada/atualizada conforme checklist acima.
- Rastreabilidade sincronizada (issues/PRs, docs locais, CHANGELOG/RELEASES, TEST_AUTOMATION_PLAN).
