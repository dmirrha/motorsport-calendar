# Fase 0 — Cenários, Inventário e Decisões

Data: 2025-08-09T08:16:47-03:00
Relatório base: `test_results/inventory/phase0_inventory_20250809-081647.md`

## 1) Testes fora de `tests/`
- Encontrado: `./test_issue_3_fixes.py`

Decisão proposta:
- Mover para `tests/` e padronizar nome se necessário (`test_*.py`).

## 2) Artefatos gerados versionados
Diretórios encontrados:
- `./.pytest_cache`
- `./tests/unit/test_results`
- `./tests/test_results`
- `./test_results`

Arquivos encontrados:
- `./tests/unit/.coverage`
- `./tests/.coverage`
- `./tests/test_results/coverage.xml`
- `./test_results/coverage.xml`
- `./tests/unit/test_results/junit.xml`
- `./tests/test_results/junit.xml`
- `./test_results_github/junit.xml`
- `./test_results/junit.xml`
- `./junit.xml`

Observação: `.gitignore` já cobre esses artefatos (linhas: `.pytest_cache/`, `htmlcov/`, `.coverage*`, `coverage.xml`, `junit.xml`, `test_results/`, `test_results_github/`, `tests/**/test_results/`). É necessário removê-los do índice do Git (mantendo ignore).

## 3) Scripts temporários
- Não foram encontrados scripts temporários de testes no diretório `scripts/` com o padrão `tmp_*(tester|tests)*.sh`.

## 4) Workflows de CI
- Apenas `./.github/workflows/release-drafter.yml`. Não há pipeline de testes ainda.

## 5) Configurações antigas
- Não foram encontrados `nose.cfg` ou `tox.ini`.

---

## Itens Derivados (a rastrear na Fase 0)
- [ ] Mover `./test_issue_3_fixes.py` para `tests/` e adequar nome (padrão `test_*.py`).
- [ ] Remover artefatos versionados do índice do Git (manter `.gitignore`):
  - [ ] Remover diretórios: `.pytest_cache/`, `tests/**/test_results/`, `test_results/`, `test_results_github/` (do índice).
  - [ ] Remover arquivos: `.coverage`, `.coverage.*`, `coverage.xml`, `junit.xml` (e variantes sob `tests/**/test_results/`, `test_results/`).
  - [ ] Criar `.gitkeep` em `tests/test_results/` e/ou `test_results/` se necessário.
- [ ] Adicionar workflow de testes (`.github/workflows/tests.yml`) na fase apropriada (ver plano).

Status:
- Inventário executado via `scripts/tests_phase0_inventory.sh`. Relatório salvo em `test_results/inventory/phase0_inventory_20250809-081647.md`.
- Aguardando execução da limpeza e movimentação conforme checklist da Fase 0.
