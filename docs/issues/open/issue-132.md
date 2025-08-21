# Issue #132 — P0: Job noturno para detecção de flaky tests (múltiplas execuções)

- Estado: open
- Prioridade: P0
- Labels: enhancement, ci, testing, needs-triage, priority: P0
- Link: https://github.com/dmirrha/motorsport-calendar/issues/132
- Criado em: 2025-08-20 08:13 UTC

## Contexto
A auditoria de testes (`docs/tests/audit/TEST_AUDIT_2025-08-19.md`) recomenda implementar um job agendado para detectar flakiness executando a suíte diversas vezes, consolidando métricas por teste e publicando artefatos para triagem.

## Objetivo
- Executar a suíte N vezes (5–10) toda madrugada para observar instabilidade.
- Consolidar resultados por `nodeid` (pytest) com contagens de `passes`, `fails`, `flakes` e taxa de flakiness.
- Publicar artefatos (logs, JUnit XML, CSV/JSON consolidado) e resumo no job.

## Escopo
- Novo workflow: `.github/workflows/flaky-nightly.yml`.
- Gatilhos: `schedule` (cron diário ~03:00 UTC) e `workflow_dispatch` (manual).
- Execução: 5 a 10 iterações completas da suíte por execução (sem `--maxfail=1` para não interromper métricas). Usar `pytest -q`, `pytest-timeout`, `pytest-randomly`.
- Saída por iteração:
  - `junitxml`: `reports/gha/run_${{ github.run_id }}/iter_<N>/junit.xml`
  - `pytest.log`/stdout: `reports/gha/run_${{ github.run_id }}/iter_<N>/pytest.log`
- Consolidação:
  - Agregar JUnit XML em `reports/gha/run_${{ github.run_id }}/summary/`:
    - `flaky_summary.csv`
    - `flaky_summary.json`
    - `summary.md` (resumo humano + top N flaky)
  - Espelhar para `reports/gha/latest_main/` (somente em execução no `default` branch). Esses arquivos serão publicados como artefatos (não commitados).
- Publicação:
  - Upload de artefatos: `name: flaky-nightly-${{ github.run_id }}` com `retention-days: 14`.
  - `GITHUB_STEP_SUMMARY`: tabela dos testes com maior flakiness.

## Fora de Escopo
- Alterar a suíte de testes em si.
- Introduzir commits automáticos no repositório a partir do CI.

## Critérios de Aceite
- Workflow executa via cron diário (03:00 UTC) e pode ser disparado manualmente.
- Artefatos contendo resultados por iteração e consolidados disponíveis para download na execução do workflow.
- Relatório consolidado acessível na pasta `reports/gha/latest_main/` dentro do artefato e resumo publicado no `GITHUB_STEP_SUMMARY`.
- Documentação atualizada com instruções de triagem (README/overview) antes do merge da PR, seguindo a preferência de deixar S5 por último.

## Plano de Resolução (limpo)
- Workflow `.github/workflows/flaky-nightly.yml` implementado com cron 03:00 UTC e gatilho manual.
- Execução multi-iterações (padrão 6), coleta por iteração e consolidação (CSV/JSON/MD) concluídas.
- Publicação de artefatos e `GITHUB_STEP_SUMMARY` ativa.
- Próximo: atualizar documentação e release notes (S5) e realizar merge da PR #141.

## Riscos e Mitigações
- Tempo de execução elevado: manter `-q`, usar `pytest-timeout`, limitar `ITERATIONS` inicial (ex.: 5-6) e ajustar depois.
- Intermitência por ambiente de CI: fixar versão de Python/OS igual ao `tests.yml`, cache de deps, seeds variados.
- Ruído por testes genuinamente quebrados: consolidar por período e observar tendência antes de ações corretivas.

## Tarefas
- [x] Criar workflow `.github/workflows/flaky-nightly.yml` com cron e manual.
- [x] Loop de iterações, coleta de `junit.xml` e logs.
- [x] Consolidação em CSV/JSON e `summary.md`.
- [x] Upload de artefatos e `GITHUB_STEP_SUMMARY`.
- [ ] Atualizar documentação e release notes.
- [ ] Merge da PR #141.

## Progresso
- Workflow implementado em `.github/workflows/flaky-nightly.yml` com `schedule` (03:00 UTC) e `workflow_dispatch`.
- Iterações padrão (6), timeout (60s) e variação de seed por iteração configuradas; saída por iteração em `reports/gha/run_${{ github.run_id }}/iter_<N>/`.
- Consolidação (CSV/JSON/MD), espelho em `reports/gha/latest_main/`, upload de artefatos e resumo no `GITHUB_STEP_SUMMARY` implementados.
- Smoke executado via evento `pull_request` (2 iterações) em 2025-08-21T06:56:51-03:00; artefatos e resumo validados com sucesso.
- Último run: https://github.com/dmirrha/motorsport-calendar/actions/runs/17125351566 (success)
- Próximos passos: atualizar documentação e release notes (S5) e, em seguida, realizar o merge da PR #141. A validação via cron ocorrerá no `main` após o merge.

## Referências
- `.github/workflows/tests.yml`
- `docs/tests/audit/TEST_AUDIT_2025-08-19.md`
- `reports/gha/`
- `requirements-dev.txt` (pytest, pytest-cov, pytest-timeout, pytest-randomly)

---

CONFIRMAÇÃO: Plano aprovado e implementação aplicada em 2025-08-21T06:20:15-03:00. Smoke concluído em 2025-08-21T06:56:51-03:00. Aguardando a primeira execução agendada às 03:00 UTC.
