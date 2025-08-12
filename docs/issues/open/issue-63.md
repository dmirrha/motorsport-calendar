# Issue #63 — Fase 1.1: Aumentar gate de cobertura para ≥45% (pytest.ini)

Referências:
- Epic: #58 — Fase 1.1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/63

## Objetivo
Elevar o gate de cobertura global para ≥45% no `pytest.ini`.

## Plano de Execução
1. Atualizar `pytest.ini` (`--cov-fail-under=45`)
2. Garantir suíte passando localmente
3. Atualizar documentação (README, tests/README, TEST_AUTOMATION_PLAN, CHANGELOG/RELEASES)

## PARE — Autorização
- PR inicia em draft até validação deste plano.
 - Aprovado pelo usuário em 2025-08-11T21:51:43-03:00.

## Progresso
 - [x] Branch criada (chore/issue-63-coverage-gate-45)
 - [ ] PR (draft) aberta
 - [x] Suíte passando com gate (45%)
 - [x] Documentação sincronizada

## Plano de Resolução

1) Preparação e validação
- Confirmar correção do leak de `monkeypatch` em `tests/unit/processing/test_event_processor_pipeline.py` (já validado anteriormente com 156 passed e ~51.92% cobertura)
- Documentar evidências de execução local neste arquivo (logs resumidos)

2) Gate de cobertura
- Atualizar `pytest.ini` para `--cov-fail-under=45` (ou chave equivalente na seção `[tool:pytest]`)
- Padronizar comandos recomendados:
  - `pytest --cov=src --cov-report=term-missing --cov-fail-under=45`
  - `pytest -q` para execução rápida

3) Sincronização documental
- Atualizar `README.md` (requisitos, como rodar testes, gate 45%)
- Atualizar `tests/README.md` (comandos com gate, práticas de patch/monkeypatch)
- Atualizar `docs/TEST_AUTOMATION_PLAN.md` (refletir gate da Fase 1.1)
- Atualizar `CHANGELOG.md` e `RELEASES.md` conforme SemVer (0.x.y) e política de notas cumulativas

4) Automação/qualidade (se aplicável)
- Verificar targets no `Makefile` para testes+cobertura (ex.: `make test`, `make coverage`)
- Adicionar/ajustar badges de cobertura no `README.md` (se presentes)

5) PR e rastreabilidade
- Abrir PR em draft a partir da branch `chore/issue-63-coverage-gate-45`
- Vincular a issue #63 e seguir checklist de conformidade
- Após validação, marcar a seção "PARE — Autorização" como aprovada e prosseguir com merge

## PARE — Autorização aprovada (2025-08-11T21:51:43-03:00)
Confirma que devo prosseguir com:
- Atualização do `pytest.ini` para gate 45%
- Execução da suíte com o gate
- Sincronização de documentação e atualização dos arquivos listados

## Evidências
- Gate configurado em `pytest.ini`: `--cov-fail-under=45`
- Execução local: **170 passed**; cobertura global: **57.86%**
- Novos testes adicionados:
  - `tests/unit/category/test_category_detector_basic.py`
  - `tests/unit/utils/test_payload_manager_extended.py`
  - `tests/unit/config/test_config_manager_basic.py`
 - Documentação sincronizada: `tests/README.md`, `docs/TEST_AUTOMATION_PLAN.md`, `README.md`, `CHANGELOG.md`, `RELEASES.md`
