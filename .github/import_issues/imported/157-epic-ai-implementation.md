# EPIC: Implementação do Plano de IA (F0–F3)

## 📝 Descrição
EPIC para conduzir a implementação incremental do plano de IA descrito em `docs/architecture/ai_implementation_plan.md`. Abrange F0 (baseline e medições), F1 (categorização semântica), F1b (deduplicação semântica), F2 (opcional: detecção de anomalias), F3 (opcional: otimizações ONNX/quantização) e sincronização de documentação/governança.

## 🔍 Contexto
- Orquestração principal: `motorsport_calendar.py`
- Categorização atual por regras: `src/category_detector.py`
- Deduplicação atual (fuzzy): `src/event_processor.py` em `_are_events_similar()`
- Validador de config: `src/utils/config_validator.py`
- Dependências atuais: `requirements.txt` (sem `sentence-transformers`/`onnxruntime` por padrão)

## 🎯 Comportamento Esperado
- AI opt-in: `ai.enabled=false` por padrão.
- Ativando IA: categorização e dedup semânticas passam a operar com thresholds (cat: 0.75; dedup: 0.85) e fallback para heurísticas existentes.
- Scripts de avaliação local para aferir precisão, latência e estabilidade (cache/batching).

## 📋 Tarefas
- [ ] #146 F1: Serviço local de embeddings (cache+batch)
- [ ] #147 F1: Integração de categorização semântica (0.75)
- [ ] #148 F1b: Deduplicação semântica (0.85)
- [ ] #149 F0: Avaliação e benchmarks (baseline vs IA)
- [ ] #150 F3 (opcional): ONNX/quantização
- [ ] #151 Config/validador: chaves `ai.*`
- [ ] #152 Docs/governança e release notes
- [ ] #153 F2 (opcional): Regras simples de anomalias

## 📊 Impacto
- Médio/Alto: Melhora de qualidade (categorias/dedup), mantendo compatibilidade ao deixar IA desativada por padrão.

## 🔗 Referências
- Plano: `docs/architecture/ai_implementation_plan.md`
- Código: `src/category_detector.py`, `src/event_processor.py`, `src/utils/config_validator.py`, `motorsport_calendar.py`
- Config: `config/config.example.json`, `docs/CONFIGURATION_GUIDE.md`
- Requisitos: `requirements.txt`
