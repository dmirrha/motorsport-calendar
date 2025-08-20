# Issue #129: P0: Resolver xfails pendentes — ordenação ICS e deduplicação TomadaTempo


**URL:** https://github.com/dmirrha/motorsport-calendar/issues/129

**Criada em:** 2025-08-20T08:13:40Z | **Atualizada em:** 2025-08-20T08:13:40Z

**Labels:**
- enhancement
- testing
- needs-triage
- priority: P0

## Descrição

# P0: Resolver xfails pendentes — ordenação ICS e deduplicação TomadaTempo

## Contexto
A auditoria de testes identificou xfails pendentes que precisam ser endereçados:
- Ordenação determinística de eventos ICS.
- Ajustes na deduplicação da fonte `TomadaTempo`.

Relatório completo: `docs/tests/audit/TEST_AUDIT_2025-08-19.md`.
Entradas de documentação: `CHANGELOG.md` ([Unreleased]) e `RELEASES.md` (Não Lançado).

## Objetivo
Remover os `xfail` existentes ao corrigir:
1) Ordenação determinística de eventos gerados/normalizados a partir de ICS.
2) Heurística de deduplicação em `TomadaTempo` para evitar falsos positivos/negativos.

## Escopo
- Ajustar lógica de ordenação de eventos ICS garantindo estabilidade e comparabilidade.
- Revisar e corrigir a deduplicação em `TomadaTempo`.
- Converter testes `xfail` em testes de sucesso.
- Garantir que a suíte permaneça verde e estável em CI.

## Critérios de Aceite
- Não há `xfail` remanescente nos casos identificados.
- Testes de integração relacionados passam de forma determinística (3x runs).
- Cobertura não diminui e não há regressão em entidades/duplicatas.
- Documentação atualizada (CHANGELOG/RELEASES/docs/tests/overview.md).

## Tarefas
- [ ] Mapear testes `xfail` de ICS e TomadaTempo.
- [ ] Implementar ordenação determinística p/ eventos ICS.
- [ ] Corrigir heurística de deduplicação em `TomadaTempo`.
- [ ] Atualizar/reativar asserts dos testes removendo `xfail`.
- [ ] Rodar suíte 3x em CI para validar estabilidade.
- [ ] Atualizar documentação relacionada.

## Riscos e Mitigações
- Risco de regressão em parsing ICS ou heurísticas de dedup: adicionar testes adicionais e rodadas repetidas.
- Performance: validar impacto em tempo/complexidade.

## Referências
- `tests/integration/` (TomadaTempo): `test_it2_tomada_tempo_*`
- `docs/tests/audit/TEST_AUDIT_2025-08-19.md`


## Evidências e Logs
- Relatório: 
- Testes afetados:
  -  (xfail final)
  -  (deduplicação)

## Plano de Resolução
- [ ] Mapear pontos de ordenação ICS
- [ ] Implementar ordenação determinística
- [ ] Corrigir heurística de deduplicação (TomadaTempo)
- [ ] Remover xfails e restaurar asserts
- [ ] Executar CI 3x para validar estabilidade
- [ ] Atualizar documentação (CHANGELOG/RELEASES/docs)

## Decisões e Riscos
- Risco de regressão em parsing ICS/dedup: mitigar com testes adicionais e runs repetidas.
- Performance: avaliar impacto nas funções de normalização/ordenamento.

## Aprovação
- Aguarda confirmação para iniciar implementação.