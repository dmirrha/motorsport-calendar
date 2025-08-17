# Fase 3 — CategoryDetector Variants (Integração)

Referências:
- Teste: `tests/integration/test_phase3_category_detector_variants.py`
- Issue: #105 — Aumentar a cobertura de testes integrados para >80%
- Plano: `docs/TEST_AUTOMATION_PLAN.md`
- Regras: `.windsurf/rules/tester.md`

## Objetivo
Validar variantes do `CategoryDetector` em cenários realistas de integração, cobrindo tolerância a ruído/acentos, aprendizado e persistência, e fallback determinístico entre `raw_category` e `name` no modo em lote.

## Cenários Cobertos
- Tolerância a ruído/acentos para categorias conhecidas (ex.: `F1`, `WEC`).
- Fallback combinatório em `detect_categories_batch` (prioriza `raw_category`; combina com `name` apenas quando necessário).
- Aprendizado habilitado adiciona variações e persiste (save) corretamente.
- Roundtrip de persistência: `save_learned_categories` → `load_learned_categories` preserva dados.

## Execução e Estabilidade
Comandos utilizados (sem gates globais para medir tempo cru):

```bash
pytest -o addopts="" tests/integration/test_phase3_category_detector_variants.py -m integration --durations=0
```

Resultados (3 execuções consecutivas):
- Run 1: 0.72s — 11/11 passed
- Run 2: 0.71s — 11/11 passed
- Run 3: 0.60s — 11/11 passed

Observações:
- Zero flakes nas 3 execuções.
- Casos mais lentos (~0.01s cada):
  - `test_noise_and_accent_for_f1_and_wec`
  - `test_detect_categories_batch_fallback_combination`
  - `test_learning_enabled_adds_variation_and_persists`
  - `test_save_and_load_learned_categories_roundtrip`

## Como Reproduzir
1) Ambiente local com Python 3.11.x e dependências (`requirements.txt`).
2) Executar o comando acima na raiz do projeto.
3) Conferir tempos e estabilidade (esperado ~0.6–0.72s totais; 11/11 passed).

## Rastreabilidade
- Relacionado à meta de cobertura de integração da Issue #105 (Phase 3 — CategoryDetector Variants).
- Evidências adicionadas em `CHANGELOG.md` (Unreleased) e `RELEASES.md` (0.5.16).
