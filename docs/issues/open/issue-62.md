# Issue #62 — Fase 1.1: Cobertura de src/ical_generator.py ≥60% (validação ICS)

Referências:
- Epic: #58 — Fase 1.1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/62

## Objetivo
Elevar cobertura de `src/ical_generator.py` para ≥60% com validação de campos ICS.

## Plano de Execução
1. Validar campos ICS obrigatórios (UID, DTSTART, DTEND, TZID, SUMMARY)
2. Usar fixtures "golden" (snapshots) controladas em `tests/fixtures/`
3. Garantir determinismo (TZ/random) e isolamento de FS
4. Atualizar documentação e rastreabilidade (planos, cenários, tests/README, CHANGELOG)

## PARE — Autorização
- PR inicia em draft até validação deste plano.

## Progresso
- [ ] Branch criada
- [ ] PR (draft) aberta
- [ ] Testes implementados e passando
- [ ] Documentação sincronizada
