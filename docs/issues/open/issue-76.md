# Issue #76 — Bug: BaseSource logger None causa AttributeError em log_source_error/save_payload

Referências:
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/76
- Arquivo: `sources/base_source.py`
- Métodos: `__init__()`, `make_request()`
- Teste: `tests/unit/sources/base_source/test_make_request.py::test_make_request_logger_none_safe`

## Objetivo
Garantir que, quando `logger=None`, a classe seja resiliente e não invoque métodos específicos de logger inexistentes, mantendo o fluxo de erro esperado e registrando `stats` corretamente.

## Causa
Fallback para `logging.getLogger(__name__)` não possui métodos customizados (`save_payload`, `log_source_error`), gerando `AttributeError` no último retry.

## Correção aplicada
- Mantido `self.logger = None` quando não fornecido (sem fallback).
- Protegidas chamadas a métodos específicos via `getattr(self.logger, "save_payload", None)` e `getattr(self.logger, "log_source_error", None)`.

## Testes
- `test_make_request_logger_none_safe`: valida comportamento seguro sem exceções.

## Critérios de aceite
- Nenhum `AttributeError` quando `logger=None`.
- `stats.failed_requests` incrementado e retorno `None` no último retry.
- Suíte íntegra sem regressões.

## Plano de resolução
- [x] Reproduzir falha com `logger=None`
- [x] Ajustar inicialização (sem fallback) e proteger chamadas com `getattr`
- [x] Validar com teste dedicado
- [x] Rodar suíte 3× (zero flakes)
- [ ] Documentar em CHANGELOG/RELEASES/TEST_AUTOMATION_PLAN

## Métricas
- Suíte: 205 passed; 3× locais; gate 45% atingido
- `sources/base_source.py`: 98% de cobertura

## Comandos
```
# Apenas documentação/rastreio local
git add docs/issues/open/issue-76.*
git commit -m "docs(issues): rastreio local da Issue #76 (BaseSource logger None)"
```
