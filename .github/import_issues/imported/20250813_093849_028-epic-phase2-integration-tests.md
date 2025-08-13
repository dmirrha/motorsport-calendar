# Épico: Fase 2 — Testes Integrados e Validação de ICS

Referências:
- Plano: `docs/TEST_AUTOMATION_PLAN.md` (Seção Fase 2 — Testes Integrados)
- Regras: `.windsurf/rules/tester.md`

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

## Histórias Vinculadas
- Infra e markers de integração
- Fixtures e cenários integrados
- E2E caminho feliz + snapshots
- Edge cases (overnight, TZ, opcionais)
- Deduplicação e ordenação
- Mocks/fakes (rede/tempo)
- CI (workflow, artefatos, cobertura)
- Documentação e rastreabilidade

## Notas
- Mantenha simplicidade: mocks básicos e fixtures pequenas.
- Priorize legibilidade e manutenção.
