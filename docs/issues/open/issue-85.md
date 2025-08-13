# Issue #85 — Fase 2 — Infra de Testes de Integração e Markers

Vinculado ao épico: #78

Referências:
- Epic: #78 — Épico Fase 2
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/85
- Plano: `docs/TEST_AUTOMATION_PLAN.md`

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

## Progresso
- [ ] Infra criada
- [ ] Smoke test passando 3× (<30s)
- [ ] Documentação sincronizada
