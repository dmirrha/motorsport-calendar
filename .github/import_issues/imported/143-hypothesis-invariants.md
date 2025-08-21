# P1: Property-based testing (hypothesis) para invariantes de parsing/dedupe/ordenação ICS

## Contexto
Conforme `docs/tests/audit/TEST_AUDIT_2025-08-19.md` (P1), precisamos introduzir property-based testing para reforçar invariantes em parsers de datas/horas/TZ, deduplicação e ordenação estável no ICS. Isso aumenta confiança sem acoplar a casos específicos.

## Objetivo
Adicionar testes com Hypothesis cobrindo invariantes principais:
- Parsing de datas/horas/timezones: round-trips e equivalências.
- Dedupe: idempotência, comutatividade parcial, estabilidade de escolha por prioridade.
- Ordenação ICS: ordem estável sob empates.

## Escopo
- Incluir `hypothesis` em `requirements-dev.txt`.
- Criar bateria mínima de propriedades em `tests/unit/` (ou `tests/property/` se preferir):
  - `test_prop_datetime_parsing_roundtrip.py`
  - `test_prop_dedupe_invariants.py`
  - `test_prop_ical_ordering_stability.py`
- Targets e referências:
  - `src/event_processor.py`
  - `src/ical_generator.py`
  - `sources/base_source.py`

## Critérios de Aceite
- Propriedades executam localmente 3× sem flakes (<30s no total).
- Cobrem os invariantes listados com exemplos mínimos de shrinking.
- Documentação: `tests/README.md` e `docs/tests/overview.md` atualizados com seção “Property-based testing (Hypothesis)”.

## Tarefas
- [ ] Adicionar `hypothesis` ao `requirements-dev.txt`.
- [ ] Implementar propriedades de parsing de datas/TZ.
- [ ] Implementar propriedades de dedupe (idempotência/estabilidade).
- [ ] Implementar propriedades de ordenação estável no ICS.
- [ ] Atualizar documentação (README de testes/overview) e notas (CHANGELOG/RELEASES).

## Referências
- Auditoria: `docs/tests/audit/TEST_AUDIT_2025-08-19.md` (linhas 72–75). 
- Módulos: `src/event_processor.py`, `src/ical_generator.py`, `sources/base_source.py`.
