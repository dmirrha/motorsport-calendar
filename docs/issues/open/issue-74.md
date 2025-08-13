# Issue #74 — PytestCollectionWarning: classe com __init__ não colecionável em `test_helpers_and_parsers`

- Estado: open
- Link: https://github.com/dmirrha/motorsport-calendar/issues/74
- Labels: tests, quality, warning
- Criada em: 2025-08-12T09:36:18Z

## Descrição
O Pytest emite `PytestCollectionWarning` indicando que uma classe de testes com `__init__` não será colecionada:

> PytestCollectionWarning: cannot collect test class 'X' because it has a __init__ constructor

O aviso ocorre em `tests/unit/sources/base_source/test_helpers_and_parsers.py` e pode ocultar testes futuros se a classe crescer ou se novas funções forem adicionadas inadvertidamente ao escopo da classe.

## Contexto
- Qualidade-first: eliminar avisos que afetem manutenção e legibilidade da suíte.
- Padrão recomendado: funções soltas ou classes `Test*` sem `__init__` para compatibilidade com a coleta do Pytest.

## Comportamento Esperado
- Suíte executa sem `PytestCollectionWarning`.
- `test_helpers_and_parsers.py` organizado conforme boas práticas de coleta do Pytest.

## Passos para Reproduzir
1. Executar: `pytest -q`
2. Observar o aviso referente a `tests/unit/sources/base_source/test_helpers_and_parsers.py`.

## Ambiente
- SO: macOS
- Python: 3.11.5
- Pytest: configurado via `pytest.ini`

## Tarefas
- [ ] Refatorar `tests/unit/sources/base_source/test_helpers_and_parsers.py` para remover `__init__` em classes de teste ou migrar para funções.
- [ ] Garantir descoberta sem avisos (`pytest -q`).
- [ ] Atualizar `tests/README.md` com nota sobre classes `Test*` sem `__init__`.
- [ ] Atualizar `CHANGELOG.md` e `docs/TEST_AUTOMATION_PLAN.md` com a correção.

## Aceite
- Suíte executa sem `PytestCollectionWarning`.
- Arquivo compatível com modelo de coleta do Pytest.
- Documentação atualizada.
