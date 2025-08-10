# Issue #47 — Fase 1: Organização da suíte de testes

Referências:
- Epic: #45 — Automação de testes
- Milestone: #2 — Automação de testes - Fase 1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/47

## Objetivo
Organizar a suíte de testes para escalabilidade e manutenção:
- Estrutura por domínio/componente em `tests/unit/`
- Padrão de nomes `test_*.py`
- Remover `__init__.py` desnecessários
- Consolidar utilitários/fixtures
- Garantir descoberta apenas em `tests/`

## Plano de Execução
1. Mapear módulos-alvo dos testes (`sources/tomada_tempo.py`, `src/silent_period.py`, `src/utils/config_validator.py`).
2. Criar estrutura-alvo em `tests/unit/` por domínio:
   - `tests/unit/sources/tomada_tempo/`
   - `tests/unit/silent_period/`
   - `tests/unit/utils/`
3. Remover hacks de `sys.path` dos testes (usar `tests/conftest.py`).
4. Mover/renomear arquivos conforme domínio.
5. Criar `tests/README.md` com convenções e estrutura.
6. Rodar `pytest` e ajustar se necessário.
7. Atualizar documentação e changelog.

## PARE — Autorização
- PR #54 aprovada: execução autorizada.

## Progresso
- [x] Branch criada: `chore/tests-organization-47-20250809`
- [x] Estrutura criada: `tests/unit/sources/tomada_tempo/`, `tests/unit/silent_period/`, `tests/unit/utils/`
- [x] Removidos hacks de path em `tests/test_tomada_tempo.py`, `tests/test_silent_period.py`, `tests/unit/test_config_validator.py`
- [x] Movidos:
  - `tests/unit/sources/tomada_tempo/test_tomada_tempo.py`
  - `tests/unit/silent_period/test_silent_period.py`
  - `tests/unit/utils/test_config_validator.py`
  - `tests/regression/test_processing/test_issue_3_fixes.py`
- [x] Criado `tests/README.md` (convenções)
- [x] Validação: `pytest -q` → 37 passed
- [x] Atualizar `docs/TEST_AUTOMATION_PLAN.md` com item do `tests/README.md`
- [x] Atualizar `PROJECT_STRUCTURE.md` com nova árvore de `tests/`
- [x] Atualizar `CHANGELOG.md` (Não lançado)
  - [x] Atualizar `README.md` (seção Testes) com link para `tests/README.md`

## Notas
- Descoberta segue restrita a `tests/` via `pytest.ini`.
- TZ fixa: `America/Sao_Paulo` via fixture autouse em `tests/conftest.py`.
- Sem alterações funcionais no código de produção.
