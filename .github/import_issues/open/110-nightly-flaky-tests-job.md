# P0: Job noturno para detecção de flaky tests (múltiplas execuções)

## Contexto
A auditoria recomendou um job agendado para detectar flakiness executando a suíte diversas vezes e consolidando métricas.

## Objetivo
- Criar workflow agendado (cron) no GitHub Actions para rodar a suíte N vezes.
- Consolidar resultados, identificar testes flaky e publicar artefatos/relatório.

## Escopo
- Novo workflow `.github/workflows/flaky-nightly.yml` executando 5–10 iterações.
- Estratégias: `pytest -q --maxfail=1` + coleta de falhas; opcionalmente `pytest-rerunfailures`/`pytest-repeat`.
- Publicar artefatos (logs, junitxml consolidado) e métricas (CSV/JSON) para histórico em `reports/gha/`.

## Critérios de Aceite
- Workflow roda via cron (ex.: diariamente às 03:00 UTC) e pode ser disparado manualmente.
- Artefatos disponíveis para download; relatório consolidado no repositório (pasta `reports/gha/latest_main/`).
- Documentação atualizada com instruções de triagem de flaky tests.

## Tarefas
- [ ] Adicionar workflow agendado.
- [ ] Adicionar geração/coleta de relatórios (JUnit, CSV/JSON).
- [ ] Publicar artefatos e atualizar docs.

## Referências
- `docs/tests/audit/TEST_AUDIT_2025-08-19.md`
- `.github/workflows/tests.yml`
- `reports/gha/`
