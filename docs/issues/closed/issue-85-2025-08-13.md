# Issue #85 — Fase 2 — Infra de Testes de Integração e Markers

Vinculado ao épico: #78

Referências:
- Epic: #78 — Épico Fase 2
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/85
- Plano: `docs/TEST_AUTOMATION_PLAN.md`

## Descrição
Criar a infraestrutura mínima para testes integrados com pytest.

## Tarefas
- [x] Criar diretório `tests/integration/` (sem `__init__.py`, por convenção)
- [x] Definir marker `integration` em `pytest.ini` (com registro de markers)
- [x] Adicionar seleção `-m "integration"` na documentação (`tests/README.md`)
- [x] Teste de fumaça em `tests/integration/test_smoke.py`

## Critérios de Aceite
- [x] `pytest -m integration` executa e passa localmente (<30s)
- [x] CI reconhece o marker (job conseguirá filtrar)
- [x] Documentação atualizada

## Progresso
- [x] Infra criada
- [x] Smoke test passando 3× (<30s)
- [x] Documentação sincronizada
  - Métricas (local, 2025-08-13 BRT): execuções 3× de `pytest -m integration -q -o addopts=""` em 0.84s, 0.68s, 0.71s.

## Plano de Resolução
1) Criar diretório de integração: `tests/integration/` (sem `__init__.py`, por convenção).
2) Registrar marker `integration` em `pytest.ini` (seção markers) para evitar PytestUnknownMarkWarning.
3) Criar teste de fumaça em `tests/integration/test_smoke.py` validando execução básica do runner.
4) Atualizar `tests/README.md` com instruções de seleção: `pytest -m "integration"` e combinação com outras flags (`-q`, `-k`, `-vv`).
5) Verificar CI: confirmar que o workflow `.github/workflows/tests.yml` não falha com o marker registrado (sem alterar o job por ora; apenas garantir compatibilidade).
6) Executar localmente 3×: `pytest -m integration -q -o addopts=""` (<30s), registrar métricas e sincronizar documentação.
7) Atualizar rastreabilidade (este arquivo `.md` e `issue-85.json`), `CHANGELOG.md`, `RELEASES.md` e `docs/TEST_AUTOMATION_PLAN.md`.

## Checklist de Encerramento
- [x] Rastreabilidade atualizada: `docs/issues/open/issue-85.{md,json}`
- [x] Documentação sincronizada: `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`
- [x] Smoke test de integração validado 3× (<30s) e métricas registradas
- [x] Abrir PR mencionando "Closes #85" — PR #88: https://github.com/dmirrha/motorsport-calendar/pull/88

### Entregáveis
- `tests/integration/` (sem `__init__.py`, por convenção)
- `tests/integration/test_smoke.py`
- `pytest.ini` com marker `integration` registrado
- `tests/README.md` atualizado

### Notas/Riscos/Assunções
- Escopo mínimo viável, sem testes de integração reais ainda.
- CI já existente deve aceitar markers registrados; ajuste de jobs será avaliado depois.
- Tempo alvo: < 30s local para suite `-m integration` (smoke).
 - Por convenção do projeto (ver `tests/README.md`), não usamos `__init__.py` em diretórios de teste; o arquivo foi omitido.

## PARE — Confirmação Necessária
Antes de prosseguir com as alterações de arquivos e criação dos testes:
- [x] Confirmar execução do plano acima (itens 1–7).
- [x] Confirmar que não haverá ajustes de CI nesta issue além do registro de marker no `pytest.ini`.

Ao confirmar, seguirei com os commits na branch `chore/issue-85-integration-markers`.
