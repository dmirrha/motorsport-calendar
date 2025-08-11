# Issue #61 — Fase 1.1: Cobertura de src/event_processor.py ≥60%

Referências:
- Epic: #58 — Fase 1.1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/61
- PR: https://github.com/dmirrha/motorsport-calendar/pull/68

## Objetivo
Elevar cobertura de `src/event_processor.py` para ≥60%.

## Checklist
- [x] Criar fixtures de entrada/saída (tmp_path) para validar processamento de eventos
- [x] Testar validações, merges e cenários de dados faltantes
- [x] Garantir isolamento de FS/env e determinismo de random/TZ
- [x] Atualizar documentação e rastreabilidade (planos, cenários, tests/README, CHANGELOG)

## PARE — Autorização
- PR inicia em draft até validação deste plano.

## Progresso
- [x] Branch criada
- [x] PR (draft) aberta
- [x] Testes implementados e passando
- [x] Documentação sincronizada

Métricas (2025-08-11): cobertura de `src/event_processor.py` = **83%** (meta ≥60% atingida).
Documentos atualizados: `tests/README.md`, `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`, `docs/issues/open/issue-61.{md,json}`.

## Critérios de aceite
- [x] Cobertura de `src/event_processor.py` ≥60%
- [x] Testes determinísticos e isolados
- [x] Documentação sincronizada
