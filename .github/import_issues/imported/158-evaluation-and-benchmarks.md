# F0: Avaliação e benchmarks (baseline vs IA)

## 📝 Descrição
Criar scripts e cenários de avaliação para comparar baseline (heurístico/fuzzy) vs IA (semântico) em categorização e deduplicação, com coleta de métricas e reproducibilidade.

## 🔍 Contexto
- Pasta sugerida para relatórios: `docs/tests/audit/` ou `docs/tests/scenarios/`.
- Métricas: precisão, cobertura, latência por lote, cache hit rate.

## 🎯 Comportamento Esperado
- Facilitar execução local com seeds fixos e dataset de exemplo.
- Exportar relatórios Markdown/CSV simples.

## 🛠️ Passos
1. Preparar dataset sintético/exemplar e seeds.
2. Rodar baseline vs IA (cat e dedup) e cronometrar.
3. Gerar relatórios comparativos com gráficos simples (opcional).
4. Documentar como rodar e interpretar.

## 📋 Critérios de Aceitação
- [ ] Scripts documentados e reprodutíveis.
- [ ] Métricas salvas em arquivos versionáveis.
- [ ] Sem dependência de nuvem.

## 📊 Impacto
Médio — garante visibilidade de qualidade/performance e reduz risco.

## 🔗 Relacionamento
- EPIC: #157

## 🔗 Referências
- `docs/architecture/ai_implementation_plan.md`
- `requirements.txt`
- Código: `src/category_detector.py`, `src/event_processor.py`
