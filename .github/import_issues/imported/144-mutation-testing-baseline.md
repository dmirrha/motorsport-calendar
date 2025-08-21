# P1: Mutation testing baseline (mutmut) em módulos críticos (event_processor, ical_generator, base_source)

## Contexto
A auditoria (P1) identificou risco de cobertura otimista. Baseline de mutation testing ajuda a medir eficácia dos testes.

## Objetivo
Configurar `mutmut` para medir mutantes sobreviventes nos módulos críticos:
- `src/event_processor.py`
- `src/ical_generator.py`
- `sources/base_source.py`

## Escopo
- Incluir `mutmut` em `requirements-dev.txt`.
- Adicionar alvo make/script simples: `make mutmut-baseline` (ou comando no README).
- Parâmetros sugeridos iniciais:
  - `mutmut run --paths-to-mutate src/event_processor.py,src/ical_generator.py,sources/base_source.py --backup`.
  - Ignorar testes lentos; manter orçamento de tempo curto.
- CI: opcional (noturno) apenas para relatório informativo, sem bloquear PRs.

## Critérios de Aceite
- Execução local produz relatório de mutantes com pelo menos 1 módulo coberto.
- Documentação: `tests/README.md` e `docs/tests/overview.md` com instruções e interpretação do relatório.
- Não aumenta tempo total de CI em PRs (se integrado, rodar apenas no noturno, informativo).

## Tarefas
- [ ] Adicionar `mutmut` ao `requirements-dev.txt`.
- [ ] Script/Make alvo para baseline local.
- [ ] (Opcional) Job noturno informativo.
- [ ] Atualizar documentação e notas (CHANGELOG/RELEASES).

## Referências
- Auditoria: `docs/tests/audit/TEST_AUDIT_2025-08-19.md` (linhas 76–78).
