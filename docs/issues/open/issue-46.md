---
issue: 46
title: "Fase 1 — Configuração mínima do Pytest"
epic: 45
milestone: 2
branch: chore/pytest-min-config-46-20250809
created_at: 2025-08-09T20:10:15Z
status: "concluída (aguardando PR)"
---

# Issue #46 — Plano de Resolução

- Link: https://github.com/dmirrha/motorsport-calendar/issues/46
- Epic: #45
- Milestone: #2 — Automação de testes - Fase 1
- Branch: chore/pytest-min-config-46-20250809

## Descrição
Configurar o Pytest de forma mínima para a Fase 1, com cobertura inicial e geração de relatórios, garantindo determinismo de TZ e documentação.

## Logs e Evidências
- Execução local: 37 passed, 1 warning (urllib3/OpenSSL), ~2s
- Gate de cobertura: 40% (atingido)
- Saídas geradas: `coverage.xml`, `htmlcov/`, `test_results/junit.xml`

## Plano de Resolução
- [x] Definir configuração base (`pytest.ini`: `testpaths = tests`, `addopts` com `--cov=src --cov=sources`)
- [x] Relatórios: `--cov-report=term-missing:skip-covered`, `--cov-report=xml:coverage.xml`, `--cov-report=html`, `--junitxml=test_results/junit.xml`
- [x] Ajustes de testes: `tests/conftest.py` com sys.path (raiz e `src/`) e fixture autouse `TZ=America/Sao_Paulo`
- [x] Marcadores: registrar `unit` e `integration` em `pytest.ini`
- [x] Cobertura mínima: `--cov-fail-under=40`
- [x] Dependências de dev: `requirements-dev.txt` com `pytest~=8` e `pytest-cov~=5`
- [x] Documentação: seção "🧪 Testes" no `README.md` e progresso marcado em `docs/TEST_AUTOMATION_PLAN.md`
- [x] Execução local validada: 37 testes passando

## Critérios de Aceite
- Suíte de testes passa localmente (37 passed)
- Gate de cobertura inicial respeitado (40%)
- Artefatos de relatório gerados (XML/HTML/JUnit)
- Documentação atualizada (README e Plano)
- PR aberta referenciando a issue e épico (pendente nesta etapa)

## PARE
Mudanças aprovadas e executadas em 2025-08-09T22:29:26-03:00. Aguardando abertura da PR para encerramento automático da issue.
