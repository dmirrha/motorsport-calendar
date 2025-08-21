# Issue 143 — P1: Property-based testing (hypothesis) para invariantes de parsing/dedupe/ordenação ICS

- ID: 3341578489
- Número: 143
- Estado: open
- URL: https://github.com/dmirrha/motorsport-calendar/issues/143
- Criado em: 2025-08-21T12:35:39Z
- Atualizado em: 2025-08-21T12:35:39Z
- Labels: enhancement, testing, needs-triage, priority: P1

## Contexto
A auditoria (P1) recomenda introduzir property-based testing para fortalecer invariantes fundamentais sem acoplamento a casos específicos.

## Objetivo
Cobrir invariantes principais com Hypothesis:
- Parsing de datas/horas/TZ: round-trips e equivalências.
- Dedupe: idempotência, comutatividade parcial, estabilidade de escolha por prioridade.
- Ordenação ICS: estabilidade sob empates.

## Escopo
- Adicionar `hypothesis` a `requirements-dev.txt`.
- Criar propriedades mínimas em `tests/unit/` (ou `tests/property/`):
  - `test_prop_datetime_parsing_roundtrip.py`
  - `test_prop_dedupe_invariants.py`
  - `test_prop_ical_ordering_stability.py`
- Targets: `src/event_processor.py`, `src/ical_generator.py`, `sources/base_source.py`.

## Critérios de Aceite
- Propriedades executam localmente 3× sem flakes (<30s total).
- Invariantes cobertos com shrinking útil em falhas.
- Documentação atualizada (`tests/README.md`, `docs/tests/overview.md`).

## Tarefas (da issue)
- [ ] Adicionar `hypothesis` ao `requirements-dev.txt`.
- [ ] Implementar propriedades de parsing de datas/TZ.
- [ ] Implementar propriedades de dedupe (idempotência/estabilidade).
- [ ] Implementar propriedades de ordenação estável no ICS.
- [ ] Atualizar documentação e notas (CHANGELOG/RELEASES).

---

# Plano de Resolução (proposto)

## 1) Dependência e setup
- Incluir `hypothesis` em `requirements-dev.txt`.
- Criar pasta `tests/property/` (separada, opcional) com conftest mínimo.

## 2) Propriedades
- Datas/TZ: gerar `datetime` com timezones, validar round-trip parser↔formatter.
- Dedupe: propriedade de idempotência e estabilidade de seleção.
- ICS: ordenar e reordenar eventos com empates, garantir estabilidade.

## 3) Execução e flakiness
- Rodar 3× localmente; ajustar deadlines/healthcheck se necessário.

## 4) Documentação
- Atualizar guias em `docs/tests/overview.md` e `tests/README.md` (como rodar, interpretar falhas).

## Riscos e Mitigações
- Flakiness por geradores muito amplos: restringir estratégias, usar `@settings(deadline=None)` quando pertinente.

## Checklist de Execução
- [ ] Dependência adicionada.
- [ ] Propriedades implementadas.
- [ ] Execução estável validada.
- [ ] Documentação atualizada.

---

## Status
- Aberta; aguardando priorização/triagem.
