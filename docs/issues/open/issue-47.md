---
issue: 47
title: "Fase 1 — Organização de testes"
epic: 45
milestone: 2
branch: chore/tests-organization-47-20250809
created_at: 2025-08-09T22:57:20-03:00
status: "em andamento (planejamento)"
---

# Issue #47 — Plano de Resolução

- Link: https://github.com/dmirrha/motorsport-calendar/issues/47
- Epic: #45
- Milestone: #2 — Automação de testes - Fase 1
- Branch: chore/tests-organization-47-20250809

## Descrição
Organizar a suíte de testes para escalabilidade, padronização de descoberta e reutilização de utilitários/fixtures.

## Logs e Evidências
- Coleta atual confirmada somente em `tests/` via `pytest.ini`
- Itens pendentes de organização detalhados abaixo

## Plano de Resolução
- [ ] Estruturar `tests/unit/` por domínio/componente
- [ ] Garantir nomenclatura `test_*.py` e ausência de `__init__.py` onde não necessário
- [ ] Consolidar utilitários (helpers/fixtures) reutilizáveis
- [ ] Verificar descoberta apenas em `tests/` (consistência local/CI)
- [ ] Atualizar documentação em `docs/TEST_AUTOMATION_PLAN.md` e `README.md` se necessário

## Critérios de Aceite
- Hierarquia estável documentada em `docs/TEST_AUTOMATION_PLAN.md`
- Coleta consistente local/CI

## PARE
PARE aqui para aprovação antes de qualquer alteração na estrutura dos testes.
