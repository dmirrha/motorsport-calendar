# Issue #60 — Fase 1.1: Cobertura de sources/base_source.py ≥60% (erros/retries)

Referências:
- Epic: #58 — Fase 1.1
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/60

## Objetivo
Elevar cobertura de `sources/base_source.py` para ≥60%, cobrindo tratamento de erros e políticas de retry.

## Plano de Execução
1. Testar timeouts, HTTP errors (4xx/5xx), backoff/retries e limites
2. Mockar `requests` e simular exceções
3. Cobrir logging e caminhos de falha (retornos nulos, validação de payload)
4. Atualizar documentação e rastreabilidade (planos, cenários, tests/README, CHANGELOG)

## PARE — Autorização
- PR inicia em draft até validação deste plano.

## Progresso
- [x] Branch criada
- [x] PR (draft) aberta — https://github.com/dmirrha/motorsport-calendar/pull/67
- [x] Testes implementados e passando
- [x] Documentação sincronizada
 - [x] Cobertura por ramos de BaseSource concluída

## Métricas (2025-08-11)
- Suíte: 132 passed
- Cobertura global: 38.57%
- Cobertura `sources/base_source.py`: 97%

## Escopo entregue (resumo)
- Erros HTTP 4xx/5xx com retries e logs
- Backoff exponencial/rate-limit com monkeypatch em `time.sleep` (sem sleeps reais)
- Comportamento seguro quando `logger=None` via `getattr` para métodos customizados
- Verificações de logs de debug e salvamento de payloads
- Teste opcional: rotação de `User-Agent` (determinístico via `random.choice`)
- Helpers/parsers cobertos: `parse_date_time`, `normalize_event_data`, `filter_weekend_events`, `_setup_session` (headers), `get_streaming_links`

- Incrementais entregues: campos ausentes/HTML malformado, slice de `recent_errors` em `get_statistics`, `filter_weekend_events(None)`, formatos adicionais de data/segundos e timezone custom, estabilidade/variação de `_generate_event_id`.

## Cobertura por ramos — Concluída
- Exceção em `filter_weekend_events` (ramo de erro ao parsear data)
- Limpeza de campos com espaços em `normalize_event_data` (cleanup loop)
- Uso do context manager `__enter__/__exit__` e validações de `__str__`/`__repr__`

## Referências
- `tests/unit/sources/base_source/test_make_request.py`
- `tests/unit/sources/base_source/test_helpers_and_parsers.py`
- Documentação atualizada: `tests/README.md`, `CHANGELOG.md`, `RELEASES.md`, `docs/TEST_AUTOMATION_PLAN.md`
