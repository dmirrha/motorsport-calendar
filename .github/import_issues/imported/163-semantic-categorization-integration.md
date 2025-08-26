# F1: Integração de categorização semântica (threshold 0.75)

## 📝 Descrição
Integrar categorização semântica por embeddings em `src/category_detector.py`, mantendo heurísticas atuais como fallback. Expor `category_confidence` e `category_source`.

## 🔍 Contexto
- Serviço de embeddings (#146) provê `embed_texts()`.
- Threshold de categorização: 0.75 (ajustável por config `ai.thresholds.category`).

## 🎯 Comportamento Esperado
- Quando `ai.enabled=true`, categorizar por similaridade semântica (nomes/aliases) e atualizar campos no evento.
- Quando desabilitado, manter pipeline atual (regras/fuzzy/aliases).

## 🛠️ Passos
1. Adicionar modo batch em `detect_categories_batch()` para usar embeddings.
2. Mapear classes-alvo e vetores de referência (cachear no serviço).
3. Combinar sinais (semântico + heurístico) com fallback.
4. Logging de decisão (fonte/confiança) para auditoria.
5. Testes de integração cobrindo idiomas e variações comuns.

## 📋 Critérios de Aceitação
- [ ] Precisão mínima conforme plano; não piorar baseline.
- [ ] Flag de origem e confiança presentes (`category_source`, `category_confidence`).
- [ ] Opt-in garantido via `ai.enabled`.
- [ ] Testes de integração verdes.

## 📊 Impacto
Médio — melhora de classificação com controle de risco via opt-in.

## 🔗 Referências
- `src/category_detector.py`, `src/utils/config_validator.py`
- `motorsport_calendar.py`
- `docs/architecture/ai_implementation_plan.md`
- `requirements.txt`
