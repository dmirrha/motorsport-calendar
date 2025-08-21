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
- Documentação atualizada com instruções de triagem (README/overview) antes do merge da PR, seguindo a preferência de deixar S5 por último (hub PR #110).

## Plano de Resolução
1) Configurar workflow `.github/workflows/flaky-nightly.yml`:
   - `on: schedule` (cron `0 3 * * *`) e `workflow_dispatch`.
   - Rodar apenas no `default` branch em `schedule`.
   - Reutilizar setup do `.github/workflows/tests.yml` (instalação deps, cache pip, etc.).
2) Executar suíte em loop (ex.: `ITERATIONS=6`):
   - Para cada iteração: setar `PYTEST_ADDOPTS` com `-q -rA --timeout=60 --durations=25 --junitxml=<path>`.
   - Opcional: variar `--randomly-seed` por iteração para aumentar cobertura de ordem aleatória.
   - Salvar logs/saídas por iteração em `reports/gha/run_${{ github.run_id }}/iter_<N>/`.
3) Consolidação de resultados:
   - Script Python (embutido no job) para agregar todos os `junit.xml`:
     - Por `nodeid`: contar `runs`, `passes`, `fails`, `skips` e derivar `flaky = 1 se passes>0 e fails>0`.
     - Exportar `flaky_summary.csv` e `flaky_summary.json`.
     - Gerar `summary.md` com top N por flakiness e dicas de triagem.
4) Publicação:
   - Copiar `summary/*` também para `reports/gha/latest_main/` quando branch = default.
   - Upload de artefatos (pasta `reports/gha/`).
   - Imprimir resumo em `GITHUB_STEP_SUMMARY` (tabela compacta + links de artefatos).
5) Documentação (no fim):
   - Atualizar `docs/tests/overview.md` (nova seção Flaky Nightly), `README.md` (referência rápida), `CHANGELOG.md` e `RELEASES.md`.
   - Manter alinhado ao hub PR #110 e processo SemVer adotado.

## Riscos e Mitigações
- Tempo de execução elevado: manter `-q`, usar `pytest-timeout`, limitar `ITERATIONS` inicial (ex.: 5-6) e ajustar depois.
- Intermitência por ambiente de CI: fixar versão de Python/OS igual ao `tests.yml`, cache de deps, seeds variados.
- Ruído por testes genuinamente quebrados: consolidar por período e observar tendência antes de ações corretivas.

## Tarefas
- [ ] Criar workflow `.github/workflows/flaky-nightly.yml` com cron e manual.
- [ ] Loop de iterações, coleta de `junit.xml` e logs.
- [ ] Consolidação em CSV/JSON e `summary.md`.
- [ ] Upload de artefatos e `GITHUB_STEP_SUMMARY`.
- [ ] Atualizar documentação e release notes.

## Referências
- `.github/workflows/tests.yml`
- `docs/tests/audit/TEST_AUDIT_2025-08-19.md`
- `reports/gha/`
- `requirements-dev.txt` (pytest, pytest-cov, pytest-timeout, pytest-randomly)

---

PEDE CONFIRMAÇÃO: Confirmar este plano para iniciar a implementação do workflow.
