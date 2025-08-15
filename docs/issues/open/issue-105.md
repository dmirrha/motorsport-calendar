# Issue #105 — Aumentar a cobertura de testes integrados para >80%

Referências:
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/105
- Workflow: `.github/workflows/tests.yml`
- Configuração Codecov: `codecov.yml`
- Plano de testes: `docs/TEST_AUTOMATION_PLAN.md`
- Regras do tester: `.windsurf/rules/tester.md`

## Descrição
Aumentar a cobertura de testes integrados para >80%, de forma equalizada entre os módulos/componentes.

## Detalhes da Issue (GitHub)
- Título: Aumentar a cobertura de testes integrados para >80%
- URL: https://github.com/dmirrha/motorsport-calendar/issues/105
- Criada em: 2025-08-14T19:39:14Z
- Atualizada em: 2025-08-14T22:50:54Z

### Corpo da Issue
```
## 🚀 Descrição da Feature
Aumentar a cobertura de testes integrados para >80%

## 📌 Objetivo
Aumentar a cobertura de testes integrados para >80%, de forma equalizada entre todos os módulos

## 💡 Solução Proposta
Analisar a cobertura atual dos testes integrados por módulos ou componentes e listar a ordem de prioridade para criar novos cenários e aumentar a cobertura.

1. Execute os testes E2E e Integrados e grave o percentual de cobertura de cada módulo e global;
2. Monte um plano para priorizar o aumento da cobertura de testes, focado na qualidade dos testes;
3. Peça aprovação do plano;
4. Execute o plano;

## 📊 Impacto Esperado
Testes Integrados com cobertura global acima de 80%
```

## Contexto atual
- Uploads de cobertura por flags (`unit`, `integration`, `e2e`) via `codecov/codecov-action@v4` com OIDC e `disable_search: true`.
- Test Analytics habilitado com `codecov/test-results-action@v1` (JUnit por job) com `use_oidc: true`.
- `codecov.yml` com `component_management` mapeando `src/` e `sources/` para visualizar cobertura por componentes.
- Slug do dashboard Codecov: `/github`.

## Dados coletados (baseline)
- Cobertura integrada (global): a coletar
- Cobertura por componente: a coletar (usar Components no Codecov)
- Módulos mais críticos (baixa cobertura): a coletar

## Plano de resolução (proposto)
1) Executar baseline dos testes Integrados e E2E na branch de trabalho e registrar percentuais global e por componente (usar Codecov Components/flags).
2) Priorizar módulos críticos (parsers, processadores, validadores) conforme as regras do tester (`.windsurf/rules/tester.md`).
3) Implementar cenários integrados mínimos e efetivos (mocks simples quando necessário).
4) Rodar CI, validar evolução de cobertura e ajustar até atingir >80% global para Integrados.
5) Atualizar documentação (README/tests/RELEASES/CHANGELOG) e preparar PR mencionando a issue (#105).

## Critérios de aceite
- Cobertura de testes integrados global ≥ 80%.
- Cobertura dos módulos prioritários aumentada de forma balanceada.
- CI passando e uploads/analytics no Codecov corretos (flags + components).
- Documentação atualizada.

## Riscos/Observações
- Evitar over-engineering de testes; foco no essencial (parsers/transformações/tratamento de erros comuns).
- Usar mocks básicos (`requests`, timeouts) quando necessário.

## Confirmação
Autorize a execução do baseline de cobertura e a implementação incremental dos testes conforme este plano.
