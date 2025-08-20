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
