# Issue #111 — Implementar retry por fonte no DataCollector (flag retry_failed_sources sem efeito)

Referências:
- GitHub: https://github.com/dmirrha/motorsport-calendar/issues/111
- Código principal: `src/data_collector.py`
- Testes relevantes: `tests/unit/data_collector/test_data_collector_basic.py`, `tests/unit/data_collector/test_data_collector_more.py`

## Descrição
A flag `retry_failed_sources` é carregada em `src/data_collector.py` (no `__init__` e em `_load_config()`), porém não há implementação de tentativas adicionais por fonte, impedindo reprocessamento de falhas transitórias (ex.: timeouts intermitentes).

## Detalhes da Issue (GitHub)
- Título: Implementar retry por fonte no DataCollector (flag retry_failed_sources sem efeito)
- URL: https://github.com/dmirrha/motorsport-calendar/issues/111
- Criada em: 2025-08-16T14:38:15Z
- Atualizada em: 2025-08-16T14:38:15Z
- Labels: enhancement, collector, tech-debt

### Corpo da Issue
> Tornar o retry configurável: `retry_failed_sources` (bool), `max_retries` (int) e `retry_backoff_seconds` (float). Aplicar retry por fonte para exceções transitórias (TimeoutError, I/O), com contabilização e logging por tentativa. Padrão conservador.

## Contexto atual
- A flag é atribuída, mas não utilizada nos fluxos de coleta (`_collect_sequential()`, `_collect_concurrent()` e/ou `_collect_from_source()`).
- Estatísticas contabilizam falhas/sucessos por fonte, porém sem retry.

## Plano de resolução (proposto)
1) Implementação (código)
- Adicionar suporte de retry por fonte em `src/data_collector.py`:
  - Local: `_collect_from_source()` (ponto único para encapsular tentativas), refletindo no sequencial e concorrente.
  - Config: usar `retry_failed_sources` (bool), `max_retries` (int), `retry_backoff_seconds` (float) carregados em `_load_config()`.
  - Erros transitórios: tratar `TimeoutError`, `OSError`/`IOError` (I/O) e exceções similares das fontes; manter falhas não transitórias sem retry.
  - Backoff: `time.sleep(retry_backoff_seconds * attempt)` (linear) ou multiplicativo simples; logar tentativa N/total, exceção e decisão.
  - Estatísticas: contabilizar tentativas e resultado final por fonte; não duplicar eventos em caso de sucesso após retry.

2) Testes (determinísticos, unit)
- Novos casos focados em retry por fonte:
  - Sucesso após 1–2 tentativas (primeiras falham com TimeoutError, depois sucesso). 
  - Falha após esgotar tentativas (sempre lança erro transitório).
- Estratégia de mocks: fontes dummy controladas que levantam exceções nas primeiras chamadas e retornam sucesso depois; sem I/O real.
- Onde colocar:
  - Extender suites existentes ou criar `tests/unit/data_collector/test_data_collector_retry.py` (preferência por isolamento).

3) Documentação e configuração
- Atualizar exemplos em `config/config.example.json` com chaves:
  - `retry_failed_sources` (bool, default false), `max_retries` (int, default 1) e `retry_backoff_seconds` (float, default 0.5–1.0).
- Atualizar docs obrigatórias: `CHANGELOG.md`, `RELEASES.md`, `README.md`, `CONFIGURATION_GUIDE.md`, `CONTRIBUTING.md`, `REQUIREMENTS.md`, `PROJECT_STRUCTURE.md`, `DATA_SOURCES.md`.

4) Observabilidade
- Logs por tentativa com nível apropriado (`INFO`/`WARNING`) e resumo ao final; manter mensagens curtas e objetivas.

## Critérios de aceite (da issue)
- Retry por fonte funcional e configurável.
- Testes determinísticos cobrindo sucesso após retry e falha após esgotar retries.
- Documentação e exemplos de configuração atualizados.

## Atualizações recentes
- 2025-08-20: Criada branch de trabalho `feat/issue-111-datacollector-retry`.

## Checklist de execução (sincronizado com GitHub)
- [x] Criar branch `feat/issue-111-datacollector-retry`.
- [x] Registrar rastreabilidade local (`issue-111.md` e `issue-111.json`).
- [x] Aguardar confirmação para iniciar implementação.
- [x] Implementar retry por fonte em `src/data_collector.py`.
- [x] Adicionar/ajustar testes unitários determinísticos de retry.
- [x] Atualizar `config/config.example.json` com novas chaves/valores padrão.
- [x] Atualizar documentação: `CHANGELOG.md`, `RELEASES.md`, `README.md`, `CONFIGURATION_GUIDE.md`, `CONTRIBUTING.md`, `REQUIREMENTS.md`, `PROJECT_STRUCTURE.md`, `DATA_SOURCES.md`.
- [ ] Abrir PR referenciando a issue #111.

## Solução implementada

- DataCollector com retry por fonte em `_collect_from_source()`.
- Configurações suportadas e documentadas em `data_sources`:
  - `retry_failed_sources` (bool)
  - `max_retries` (int) com fallback para legado `retry_attempts`
  - `retry_backoff_seconds` (float)
- Escopo de retry restrito a erros transitórios: `TimeoutError`, `OSError`, `IOError`.
- Backoff linear: `time.sleep(retry_backoff_seconds * attempt)`.
- Estatísticas por fonte preservadas; propagação de erro após esgotar tentativas.

## Resultados dos testes

- Arquivo: `tests/unit/data_collector/test_data_collector_retry.py`.
- Casos:
  - Sucesso após erro transitório e retry.
  - Falha após esgotar tentativas.
- Execução local: ambos passaram. Observação: o gate global de cobertura pode falhar em runs focados; não afeta a validade funcional dos testes de retry.

## Próximos passos

- Abrir PR referenciando a Issue #111, anexando este arquivo como corpo do PR.
- Aguardar CI e revisão.

Closes #111
