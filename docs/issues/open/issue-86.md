# Issue #86 — Fase 2 — Fixtures e Cenários Integrados (HTML/JSON/ICS)

Vinculado ao épico: #78

Referências:
- Epic: #78 — Épico Fase 2
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/86
- Plano: `docs/TEST_AUTOMATION_PLAN.md`

## Descrição
Criar fixtures e dados de cenários realistas para a suíte de integração.

## Tarefas
- [x] `tests/fixtures/integration/` com HTML/JSON mínimos e claros
- [x] `tests/snapshots/phase2/` para snapshots `.ics`
- [x] Fixture utilitária para carregar cenário + normalizar ICS
- [x] Documentar convenções de nomes e estrutura

## Critérios de Aceite
- [x] Fixtures reutilizáveis e pequenas
- [x] Normalização cobre campos voláteis (ex.: DTSTAMP, UID)
- [x] Documentação em `tests/README.md` e `docs/tests/scenarios/phase2_scenarios.md`

## Plano de Resolução (PARE)
1) Criar branch: `chore/issue-86-integration-fixtures`.
2) Estrutura inicial:
    - `tests/fixtures/integration/` (HTML/JSON mínimos: `scenario_basic.html`, `scenario_basic.json`).
    - `tests/snapshots/phase2/` (armazenar `.ics` canônicos normalizados).
    - `tests/utils/ical_snapshots.py` (normalizar UID, DTSTAMP, PRODID, SEQUENCE, CREATED, LAST-MODIFIED; CRLF/ordem; TZ fixa).
3) Teste mínimo de integração: `tests/integration/test_phase2_basic.py`
    - Fluxo: eventos mínimos (dict) → `ICalGenerator.generate_calendar()` → validação/snapshot `.ics`.
    - Asserts simples: count de eventos, propriedades básicas (SUMMARY/DTSTART/DTEND/UID/URL/CATEGORIES) via snapshot.
4) Documentação:
    - Atualizar `docs/tests/scenarios/phase2_scenarios.md` (status do cenário básico) e `tests/README.md` (como rodar integração/snapshots).
    - Preparar entradas em `CHANGELOG.md` e `RELEASES.md` (Não Lançado/Próximo).
5) Abrir PR (draft) mencionando a Issue #86; checklist sincronizado.

Solicitação de confirmação: autorizar criação da branch e aplicação do esqueleto (itens 2–3) antes de prosseguir.

## Progresso
- [x] Fixtures criadas (`tests/fixtures/integration/scenario_basic.json`)
- [x] Normalização validada (`tests/utils/ical_snapshots.py` — `normalize_ics_text`, `compare_or_write_snapshot`)
- [x] Teste de integração estável 3× sem flakes (<2s cada) com `pytest -m integration -q -o addopts=""`
- [x] Documentação sincronizada: `tests/README.md` (seção Snapshots ICS), `docs/tests/scenarios/phase2_scenarios.md` (cenário básico concluído), `CHANGELOG.md` e `RELEASES.md` (entradas em Não Lançado/Próximo)
