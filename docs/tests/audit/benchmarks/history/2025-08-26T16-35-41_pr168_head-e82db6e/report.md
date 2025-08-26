# Benchmarks — Baseline vs IA

Dataset: `docs/tests/scenarios/data/eval_dataset.csv`

Executado em: 2025-08-26T16:35:41

## Categorização

modo | métrica 1 | métrica 2 | métrica 3 | total_itens | lat(ms)/item
--- | --- | --- | --- | ---: | ---:
baseline | acc=0.5333 | cov=1.0 | conf=1.0 | 15 | 0.003
ia | acc=0.9333 | cov=1.0 | conf=0.9967 | 15 | 1.333

## Deduplicação

modo | métrica 1 | métrica 2 | métrica 3 | total_itens | lat(ms)/item
--- | --- | --- | --- | ---: | ---:
baseline | P=0.0 | R=0.0 | F1=0.0 | 15 | 0.017
ia | P=0.0 | R=0.0 | F1=0.0 | 15 | 1.124
