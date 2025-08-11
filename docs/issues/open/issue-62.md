# Issue #62 — Fase 1.1: Cobertura de src/ical_generator.py ≥60% (validação ICS)

Referências:
- Epic: #58 — Fase 1.1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/62
- PR: https://github.com/dmirrha/motorsport-calendar/pull/69

## Objetivo
Elevar cobertura de `src/ical_generator.py` para ≥60% com validação de campos ICS.

## Checklist
- [ ] Validar campos ICS obrigatórios (UID, DTSTART, DTEND, TZID, SUMMARY)
- [ ] Usar fixtures "golden" (snapshots) controladas em `tests/fixtures/`
- [ ] Garantir determinismo (TZ/random) e isolamento de FS
- [ ] Atualizar documentação e rastreabilidade (planos, cenários, tests/README, CHANGELOG)

## Critérios de aceite
- [ ] Cobertura de `src/ical_generator.py` ≥60%
- [ ] Geração ICS validada e determinística
- [ ] Documentação sincronizada

## PARE — Autorização
- PR inicia em draft até validação deste plano.

## Progresso
- [x] Branch criada
- [x] PR (draft) aberta
- [ ] Testes implementados e passando
- [ ] Documentação sincronizada
