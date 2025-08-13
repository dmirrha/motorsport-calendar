# Fase 2 — Infra de Testes de Integração e Markers
Vinculado ao épico: #78

## Descrição
Criar a infraestrutura mínima para testes integrados com pytest.

## Tarefas
- [ ] Criar diretório `tests/integration/` e `tests/integration/__init__.py`
- [ ] Definir marker `integration` em `pytest.ini` (com registro de markers)
- [ ] Adicionar seleção `-m "integration"` na documentação (`tests/README.md`)
- [ ] Teste de fumaça em `tests/integration/test_smoke.py`

## Critérios de Aceite
- [ ] `pytest -m integration` executa e passa localmente (<30s)
- [ ] CI reconhece o marker (job conseguirá filtrar)
- [ ] Documentação atualizada

## Referências
- `docs/TEST_AUTOMATION_PLAN.md` (Fase 2)
- `.windsurf/rules/tester.md`
