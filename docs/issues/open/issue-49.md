# Issue #49 — Fase 1: Alvos prioritários (unit)

Referências:
- Epic: #45 — Automação de testes
- Milestone: #2 — Automação de testes - Fase 1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/49

## Objetivo
Iniciar cobertura nos componentes críticos (parsers/validadores/processadores) com testes unitários simples e efetivos, seguindo `.windsurf/rules/tester.md`.

## Plano de Execução (Checklist)
- [x] Parsers de data/hora e timezone em `sources/tomada_tempo.py`
- [ ] Processadores/validadores de eventos em `src/event_processor.py`
- [ ] Utilitário iCal `src/ical_generator.py` (`generate_ical`)
- [ ] Lógica de filtro de fim de semana em `src/silent_period.py`

## PARE — Autorização
- Esta issue requer confirmação antes da implementação dos testes. A PR será aberta como draft com este PARE no corpo e labels apropriadas.

## Progresso
- [x] Branch criada: `chore/tests-priority-targets-49-20250810`
- [x] Checklists sincronizadas com `docs/TEST_AUTOMATION_PLAN.md` (seção “Alvos prioritários (unit)”).
- [x] PR (draft) aberta: #56 — https://github.com/dmirrha/motorsport-calendar/pull/56
 - [x] Validação: suíte estável `60 passed`; cobertura total 29.31% (2025-08-10)

## Notas
- Seguir mocks essenciais já padronizados: rede (requests/Session), tempo/TZ, `tmp_path` e `os.environ`.
- Manter documentação e rastreabilidade: atualizar CHANGELOG/RELEASES/README/tests/README conforme necessário a cada marco.
