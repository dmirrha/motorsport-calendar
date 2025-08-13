# Fase 1 — Cenários de Testes (Unit)

Referências:
- Issue: #50 — Geração de cenários (unit)
- PR (draft): #57 — Plano e rastreabilidade da issue #50
- Plano: `docs/TEST_AUTOMATION_PLAN.md` (seções Fase 1 e Documentação)

## Objetivo
Definir e documentar cenários e dados mínimos reutilizáveis para testes unitários de parsers/validadores/utils, assegurando consistência com o parser real de `TomadaTempoSource` e utilitários base.

## Fixtures criados
- HTML (programação de fim de semana com cabeçalho completo): `tests/fixtures/html/tomada_tempo_weekend_minimal.html`
- HTML (programação com cabeçalho alternativo): `tests/fixtures/html/tomada_tempo_weekend_alt_header.html`
- HTML (edge cases: AM/PM, ponto como separador, categoria desconhecida): `tests/fixtures/html/tomada_tempo_weekend_edge_cases.html`
 - HTML (sem minutos: "8h", "14 horas", "21", "às 10"): `tests/fixtures/html/tomada_tempo_weekend_no_minutes.html`
 - HTML (overnight: 23:50 → 00:10 com datas separadas): `tests/fixtures/html/tomada_tempo_weekend_overnight.html`

Notas:
- Estrutura compatível com `_parse_weekend_programming_structure()` e `_parse_calendar_page()` de `sources/tomada_tempo.py`.
- Datas no formato `SEXTA-FEIRA – DD/MM/YYYY` e listas `ul > li` com eventos realistas.

## Matriz de Casos — Datas/Horas
- Formatos de hora: 24h (ex.: `08:00`), AM/PM (amostrado via `edge_cases`), sem minutos (amostrado via `no_minutes`).
- Casos overnight (amostrado via `overnight`) e naive vs aware (planejado; fixture/clock control via TZ `America/Sao_Paulo`).

## Matriz de Casos — Categoria/Local
- Categorias conhecidas (ex.: F1, NASCAR, MotoGP, F2) e fallback `Unknown` (amostrado via `edge_cases`; matriz completa pendente).
- Locais/circuitos com e sem país (planejado; hoje usamos país padrão `Brasil` quando aplicável).

## Itens relacionados a iCal (preparação para Fase 2)
- PRODID, DTSTART/DTEND com TZ, URL, CATEGORIES, RRULE via `recurrence` (planejado; cobrir em Fase 2).

## Links para testes existentes (unit)
- `tests/unit/sources/tomada_tempo/test_parse_calendar_page.py` — robustez a HTML malformado.
- `tests/unit/sources/tomada_tempo/test_parse_calendar_page_fixtures.py` — valida parsing mínimo dos fixtures (inclui assert de categoria `Unknown` no edge cases).
- `tests/unit/processing/test_event_processor_validation.py` — validações no processamento.
- ICal: testes de `ICalGenerator` (generate_calendar, _create_ical_event, validate_calendar) — ver PR #56 mergeada.
- SilentPeriod: `SilentPeriodManager.log_filtering_summary` — ver PR #56 mergeada.

## Próximos Passos (Unit)
- Adicionar casos parametrizados para horas AM/PM e sem minutos.
- Adicionar casos de categoria desconhecida e eventos sem local.
 - Introduzir fixtures JSON de eventos sintéticos (planejado) para validação unitária de normalização.

## Matriz de Cenários — Status
- [x] Datas/horas 24h — ref: `tests/unit/sources/tomada_tempo/test_parse_calendar_page_fixtures.py`
- [x] AM/PM — ref: `tests/unit/sources/tomada_tempo/test_parse_calendar_page_fixtures.py`
- [x] Sem minutos — ref: `tests/unit/sources/tomada_tempo/test_parse_calendar_page_fixtures.py`
- [x] Overnight — ref: `tests/unit/sources/tomada_tempo/test_parse_calendar_page_fixtures.py`
- [x] Categoria fallback `Unknown` — ref: `tests/unit/sources/tomada_tempo/test_parse_calendar_page_fixtures.py`
- [ ] Eventos sem local — ToDo (adicionar casos e asserts)
- [ ] Locais/circuitos com e sem país — ToDo (adicionar matriz/fixtures)
- [ ] Naive vs Aware (TZ `America/Sao_Paulo`) — movido para Fase 1.1
- [ ] Itens iCal (PRODID, DTSTART/DTEND TZ, URL, CATEGORIES, RRULE) — cobrir na Fase 2

## Rastreamento
 - Status: documentos e fixtures mínimos criados.
 - Sincronizar checklists em `docs/TEST_AUTOMATION_PLAN.md` e `docs/issues/closed/issue-50.md`.
  - Sincronizado com Issue #72 e PR #77 (docs/tests) em 2025-08-12T23:26:51-03:00.
