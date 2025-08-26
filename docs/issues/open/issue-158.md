# Issue 158 — F0: Avaliação e benchmarks (baseline vs IA)

- ID: 3356425925
- Número: 158
- Estado: open
- URL: https://github.com/dmirrha/motorsport-calendar/issues/158
- Criado em: 2025-08-26T16:56:15Z
- Atualizado em: 2025-08-26T17:09:10Z
- Labels: needs-triage, priority: P2, testing, ai, docs

## Contexto
Criar scripts e cenários de avaliação para comparar baseline (heurístico/fuzzy) vs IA (semântico) em categorização e deduplicação, com coleta de métricas e reprodutibilidade. Relatórios devem ser simples (Markdown/CSV) e fáceis de executar localmente, sem dependências de nuvem.

Referências importadas:
- `.github/import_issues/imported/158-evaluation-and-benchmarks.md`

## Objetivo
- Comparar baseline vs IA para categorização e deduplicação.
- Medir precisão, cobertura, latência por lote e (opcional) cache hit rate.
- Geração de relatórios versionáveis em `docs/tests/audit/` e/ou `docs/tests/scenarios/`.

## Escopo (proposto)
- Scripts de avaliação:
  - `scripts/eval/benchmarks.py`: CLI para rodar cenários e exportar métricas (CSV/MD).
  - Suporte a seeds fixos e dataset de exemplo.
- Dataset sintético/exemplar:
  - `docs/tests/scenarios/data/eval_dataset.csv` (pequeno, versionável, com ground-truth de categoria e marcação de duplicatas/grupos).
- Integração com código existente:
  - Categorização via `src/category_detector.py`.
  - Deduplicação via `src/event_processor.py`.
  - Baseline: normalização simples (sem contexto/learning); IA: `CategoryDetector` com contexto e learning habilitado.
- Saídas:
  - `docs/tests/audit/benchmarks/metrics.csv` e `docs/tests/audit/benchmarks/report.md`.

## Critérios de Aceite
- [ ] Scripts documentados e reprodutíveis (seed, CLI, exemplos).
- [ ] Métricas salvas em arquivos versionáveis (CSV/MD).
- [ ] Sem dependência de nuvem.

## Plano de Resolução
1) Dataset e seeds
- Criar `docs/tests/scenarios/data/eval_dataset.csv` com colunas: `event_id,name,raw_category,date,time,timezone,location,country,session_type,source,ground_truth_category,duplicate_group`.
- Fixar seeds e padronizar timezone (ex.: America/Sao_Paulo) para estabilidade.

2) Implementar CLI de benchmarks
- `scripts/eval/benchmarks.py` com modos:
  - `--task category|dedup|both`
  - `--mode baseline|ia|both`
  - `--input <csv>` e `--outdir docs/tests/audit/benchmarks`
  - `--batch-size`, `--seed`, `--threads` (opcional)
- Medir latência total/por item; coletar métricas:
  - Categoria: precisão, cobertura, confiança média.
  - Dedup: precisão/recall por pares ou por grupo (usando `duplicate_group` como ground-truth).

3) Estratégia baseline vs IA
- Baseline categoria: usar somente `raw_category` normalizada (sem contexto), fallback para `name` simplificado.
- IA categoria: `CategoryDetector.detect_categories_batch()` com contexto por evento.
- Baseline dedup: `EventProcessor` com `category_detector=None` (usa `raw_category`); IA dedup: `EventProcessor` com `CategoryDetector` ativo.

4) Relatórios e exportação
- CSV detalhado por item (predições, confiança, tempos) + resumo agregado.
- Markdown sumarizado com tabelas e notas de execução (seed, dataset, versão do código).

5) Documentação
- Instruções rápidas no `report.md` e um bloco em `README.md`/`docs/tests/overview.md` com como rodar e interpretar.

## Checklist de Execução
- [ ] Branch criada a partir de `main`.
- [ ] Arquivos de issue (MD/JSON) criados em `docs/issues/open/`.
- [ ] Dataset sintético criado.
- [ ] CLI implementada em `scripts/eval/benchmarks.py`.
- [ ] Relatórios gerados (CSV/MD) em `docs/tests/audit/benchmarks/`.
- [ ] Documentação adicionada/atualizada.
- [ ] PR aberta referenciando `#158` e notas em `RELEASES.md`.

## Logs e Referências
- Código: `src/category_detector.py`, `src/event_processor.py`
- Docs: `docs/tests/overview.md`, `docs/architecture/ai_implementation_plan.md`
- Artefatos: `docs/tests/audit/`, `docs/tests/scenarios/`
- Issue: https://github.com/dmirrha/motorsport-calendar/issues/158
- Epic relacionada: #157

## Status
- Aberta; branch de trabalho criada: `feat/158-eval-benchmarks`. Aguardando confirmação para iniciar implementação.
