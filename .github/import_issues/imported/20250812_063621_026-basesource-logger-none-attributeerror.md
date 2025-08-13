# Bug: BaseSource logger None causa AttributeError em log_source_error/save_payload

## 📝 Descrição
Quando `logger` não é fornecido ao inicializar `BaseSource`, o código usava `logging.getLogger(__name__)` como fallback. Esse objeto de logger padrão não possui os métodos personalizados `log_source_error` e `save_payload` utilizados por `BaseSource.make_request()`. No último retry com falha, a chamada a `logger.log_source_error(...)` gerava `AttributeError`, interrompendo o fluxo de erro esperado.

## 🔍 Contexto
- Arquivo: `sources/base_source.py`
- Métodos: `__init__()` e `make_request()`
- Testes relacionados: `tests/unit/sources/base_source/test_make_request.py::test_make_request_logger_none_safe`
- PR relacionado: #67 (draft) — escopo de melhoria de cobertura de testes da Issue #60

## 🎯 Comportamento Esperado
- Se `logger` for `None`, o código deve falhar de forma segura (retornar `None` quando necessário), registrar estatísticas em `self.stats` e não tentar invocar métodos específicos de logger inexistentes.
- As chamadas a rotinas de logging específicas devem ser condicionais à existência dos métodos (`save_payload`, `log_source_error`).

## 🛠️ Passos para Reproduzir
1. Monkeypatch em `time.sleep` para evitar esperas reais.
2. Patch em `sources.base_source.requests.Session` para lançar `requests.ConnectionError()` em todas as tentativas.
3. Instanciar `BaseSource` (ou subclasse) com `logger=None`.
4. Invocar `make_request("https://example.com/error")`.
5. Resultado antes do ajuste: `AttributeError: 'Logger' object has no attribute 'log_source_error'`.

## ✅ Ajuste Aplicado (local)
- `__init__`: mantido `self.logger = None` quando não fornecido, retirando o fallback ao `logging.getLogger(...)`.
- `make_request`: uso de `getattr(self.logger, "save_payload", None)` e `getattr(self.logger, "log_source_error", None)` antes de invocar métodos específicos.
- Novos testes adicionados para validar comportamento com `logger=None` e garantir ausência de exceção.

## 📱 Ambiente
- SO: macOS
- Python: 3.11
- Ferramentas: pytest

## 📋 Tarefas
- [x] Reproduzir falha com `logger=None`
- [x] Ajustar inicialização para não usar fallback que não possui métodos esperados
- [x] Proteger chamadas a métodos específicos com `getattr`
- [x] Adicionar testes unitários cobrindo o caso
- [ ] Atualizar documentação (`docs/TEST_AUTOMATION_PLAN.md`, `tests/README.md`)
- [ ] Atualizar notas de versão (`CHANGELOG.md`, `RELEASES.md`) conforme SemVer

## 📊 Impacto
Médio — Em cenários sem logger customizado, o fluxo de tratamento de falhas poderia ser interrompido por `AttributeError`. O ajuste garante robustez e previsibilidade do caminho de erro.
