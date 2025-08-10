# Issue #58 — Fase 1.1: Elevação de Cobertura e Robustez Unitária (Épico)

Referências:
- Epic: #58 — Fase 1.1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/58

## Objetivo
Elevar a cobertura unitária e robustez dos módulos prioritários, consolidando determinismo e documentação.

## Escopo
- Aumentar cobertura dos alvos prioritários (`sources/tomada_tempo.py`, `sources/base_source.py`, `src/event_processor.py`, `src/ical_generator.py`)
- Consolidar determinismo (<30s local) e isolamento (FS/env/rede/TZ/random)
- Incrementar gate de cobertura (pytest.ini) de 25% → 45%
- Atualizar documentação (SCENARIOS_INDEX, phase1_scenarios, tests/README.md, TEST_AUTOMATION_PLAN.md, CHANGELOG/RELEASES)

## Critérios de Conclusão
- Cobertura global ≥ 50%
- Gate de cobertura ≥ 45% com suíte passando localmente
- Testes determinísticos (<30s local) com registro do tempo
- Documentação e rastreabilidade atualizadas

## Histórias vinculadas
- [ ] #59 — Cobertura de `sources/tomada_tempo.py` ≥55%
- [ ] #60 — Cobertura de `sources/base_source.py` ≥60%
- [ ] #61 — Cobertura de `src/event_processor.py` ≥60%
- [ ] #62 — Cobertura de `src/ical_generator.py` ≥60%
- [ ] #63 — Gate global ≥45% (pytest.ini)
- [ ] #64 — Documentação e Cenários (sincronismo)

## PARE — Autorização
- PRs das histórias devem iniciar como draft; execução só após validação do plano de cada história.

## Notas
- Sincronizar checklists entre este arquivo, corpo das issues e `docs/TEST_AUTOMATION_PLAN.md`.
