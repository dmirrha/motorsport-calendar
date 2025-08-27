# Benchmarks — Baseline vs IA

Dataset: `docs/tests/scenarios/data/eval_dataset.csv`

Executado em: 2025-08-27T17:48:33

## Embeddings

modo | métrica 1 | métrica 2 | métrica 3 | total_itens | lat(ms)/item
--- | --- | --- | --- | ---: | ---:
emb-default | hits=1000 | misses=0 | dim=256 | 1000 | 1.078
emb-default-warm | hits=1000 | misses=0 | dim=256 | 1000 | 0.001
emb-onnx | hits=1000 | misses=0 | dim=256 | 1000 | 0.625
emb-onnx-warm | hits=1000 | misses=0 | dim=256 | 1000 | 0.001
