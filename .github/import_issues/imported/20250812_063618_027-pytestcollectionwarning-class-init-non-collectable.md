# PytestCollectionWarning: classe com __init__ não colecionável em test_helpers_and_parsers

## 📝 Descrição
O Pytest emite `PytestCollectionWarning` indicando que uma classe de testes com `__init__` não será colecionada:

> PytestCollectionWarning: cannot collect test class 'X' because it has a __init__ constructor

Isso ocorre em `tests/unit/sources/base_source/test_helpers_and_parsers.py` e pode ocultar testes futuros se a classe crescer ou se novas funções forem adicionadas inadvertidamente ao escopo da classe.

## 🔍 Contexto
- Princípios qualidade-first: eliminação de flakes e de avisos que possam impactar a manutenção da suíte.
- Evitar padrões que conflitam com o modelo de descoberta do Pytest (preferir funções soltas ou classes `Test*` sem `__init__`).

## 🎯 Comportamento Esperado
- Zero `PytestCollectionWarning` na suíte.
- Arquivo `test_helpers_and_parsers.py` organizado em funções de teste ou classe `Test*` sem `__init__`.

## 🛠️ Passos para Reproduzir
1. Executar a suíte: `pytest -q`
2. Observar o aviso de coleção referente ao arquivo `tests/unit/sources/base_source/test_helpers_and_parsers.py`.

## 📸 Evidência
- Aviso observado localmente durante as execuções 3× da suíte.

## 📱 Ambiente
- SO: macOS
- Python: 3.11.5
- Pytest: configurado via `pytest.ini` do projeto

## 📋 Tarefas
- [ ] Refatorar `tests/unit/sources/base_source/test_helpers_and_parsers.py` para remover `__init__` de classes de teste ou migrar para funções soltas.
- [ ] Garantir que a descoberta de testes permanece correta (`pytest -q` sem avisos).
- [ ] Atualizar `tests/README.md` se necessário (boas práticas de colecionamento).
- [ ] Atualizar CHANGELOG/TEST_AUTOMATION_PLAN com a correção do aviso.

## 📊 Impacto
Baixo — melhoria de manutenção e clareza da suíte, prevenindo problemas de coleção no futuro.
