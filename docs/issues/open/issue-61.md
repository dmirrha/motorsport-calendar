# Issue #61 — Fase 1.1: Cobertura de src/event_processor.py ≥60%

Referências:
- Epic: #58 — Fase 1.1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/61

## Objetivo
Elevar cobertura de `src/event_processor.py` para ≥60%.

## Checklist
- [ ] Criar fixtures de entrada/saída (tmp_path) para validar processamento de eventos
- [ ] Testar validações, merges e cenários de dados faltantes
- [ ] Garantir isolamento de FS/env e determinismo de random/TZ
- [ ] Atualizar documentação e rastreabilidade (planos, cenários, tests/README, CHANGELOG)

## PARE — Autorização
- PR inicia em draft até validação deste plano.

## Progresso
- [x] Branch criada
- [ ] PR (draft) aberta
- [ ] Testes implementados e passando
- [ ] Documentação sincronizada

## Critérios de aceite
- [ ] Cobertura de `src/event_processor.py` ≥60%
- [ ] Testes determinísticos e isolados
- [ ] Documentação sincronizada
