# Issue #78 — Épico: Fase 2 — Testes Integrados e Validação de ICS

Referências:
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/78
- Plano: `docs/TEST_AUTOMATION_PLAN.md` (Seção Fase 2 — Testes Integrados)
- Regras: `.windsurf/rules/tester.md`
- Sub-issues: #79, #80, #81, #82, #83, #84, #85, #86

## Objetivo
Cobrir o fluxo ponta a ponta (coleta → processamento → geração/validação de iCal) com testes integrados simples, determinísticos e rastreáveis, com mocks/fakes práticos e reaproveitamento de fixtures.

## Escopo
- Estrutura de testes de integração (`tests/integration/`) e marker `integration`
- Fixtures e cenários realistas (HTML/JSON/ICS) com snapshots de ICS
- Testes E2E do caminho feliz com comparação de snapshots
- Casos de borda: overnight, múltiplos fusos, campos opcionais
- Validações de deduplicação, ordenação e consistência de timezone
- Mocks/fakes de coleta e controle de tempo
- Integração CI (job dedicado, artefatos, cobertura visível)
- Documentação e rastreabilidade atualizadas

## Critérios de Conclusão
- Suíte `integration` estável (3× sem flakes, <30s local)
- Snapshots ICS determinísticos (normalização de campos voláteis)
- Job CI para integração com upload de artefatos (junit/coverage/html)
- Documentação sincronizada (CHANGELOG, RELEASES, TEST_AUTOMATION_PLAN, tests/README.md, docs/tests/scenarios)

## Checklist de Sub-issues (sequência sugerida)
- [ ] #85 — Infra de Testes de Integração e Markers
- [ ] #79 — Mocks/Fakes de Coleta e Controle de Tempo
- [ ] #86 — Fixtures e Cenários Integrados (HTML/JSON/ICS)
- [ ] #82 — E2E Caminho Feliz com Snapshots ICS
- [ ] #80 — Edge Cases: Overnight, Fusos Múltiplos e Campos Opcionais
- [ ] #84 — Deduplicação, Ordenação e Consistência
- [ ] #81 — CI: Job de Integração, Cobertura e Artefatos
- [ ] #83 — Documentação e Rastreabilidade

## Progresso
- [x] Sub-issues vinculadas ao épico no GitHub
- [x] Escopo e critérios definidos no corpo do épico
- [ ] Documentação de rastreabilidade (issue-78..86) criada
