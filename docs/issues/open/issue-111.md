# Issue #111 - Implementar retry por fonte no DataCollector (flag retry_failed_sources sem efeito)
Link: https://github.com/dmirrha/motorsport-calendar/issues/111
Autor: dmirrha
Criada em: 2025-08-16T14:38:15Z
Atualizada em: 2025-08-20T01:19:14Z
Estado: CLOSED
Labels: enhancement collector tech-debt 
Assignees: 

## Descrição
# Implementar retry por fonte no DataCollector (flag retry_failed_sources sem efeito)

A flag `retry_failed_sources` é carregada em `src/data_collector.py` (no `__init__` e em `_load_config()`), porém não há implementação de tentativas adicionais por fonte. Isso impede reprocessamento de falhas transitórias (ex.: timeouts intermitentes) conforme a intenção.

## Contexto
- A flag é atribuída, mas não utilizada nos fluxos de coleta (`_collect_sequential()`, `_collect_concurrent()` ou `_collect_from_source()`).
- Estatísticas contabilizam falhas/sucessos, porém não há retry.

## Proposta
- Tornar o retry configurável: `retry_failed_sources` (bool), `max_retries` (int), `retry_backoff_seconds` (float).
- Aplicar retry por fonte para exceções transitórias (TimeoutError, I/O), com contabilização/ logging por tentativa.
- Padrão conservador (ex.: desabilitado ou `max_retries=1`).

## Critérios de Aceite
- Retry por fonte funcional e configurável.
- Testes determinísticos (sucesso após retry; falha após esgotar retries).
- Documentação e exemplos de config atualizados.

## Referências
- Código: `src/data_collector.py`
- Tests: `tests/unit/data_collector/test_data_collector_basic.py`, `tests/unit/data_collector/test_data_collector_more.py`


## Plano de Resolução
- [x] Validar/normalizar retry em data_sources (validate_data_sources_config)
- [x] Integrar defaults no ConfigManager e invocar validação
- [x] Atualizar config exemplo (config/config.example.json)
- [x] Atualizar docs (CONFIGURATION_GUIDE, CHANGELOG, RELEASES, DATA_SOURCES)
- [ ] Rodar suíte completa de testes com coverage
- [ ] Abrir PR referenciando #111 e monitorar CI
