# F1b: Deduplicação semântica (threshold 0.85)

## 📝 Descrição
Adicionar camada de similaridade semântica à deduplicação em `src/event_processor.py::_are_events_similar()`, mantendo fuzzy/heurísticas existentes e determinismo do `_select_best_event()`.

## 🔍 Contexto
- Usa serviço de embeddings (#165) para nomes normalizados e, se disponível, local.
- Threshold de dedup: 0.85 (`ai.thresholds.dedup`).

## 🎯 Comportamento Esperado
- Quando `ai.enabled=true`, combinar fuzzy + semântico (ex.: média/concat) antes dos cortes.
- Empates mantêm regras determinísticas atuais.

## 🛠️ Passos
1. Gerar vetores para nome e local (se houver) e calcular similaridade.
2. Combinar com `fuzz.ratio` existentes via score composto.
3. Respeitar `time_tolerance_minutes` e categorias.
4. Testes para falsos positivos/negativos mais comuns.
5. Métricas: duplicatas removidas vs baseline.

## 📋 Critérios de Aceitação
- [ ] Não regressar determinismo de `_select_best_event()`.
- [ ] Melhorar recall/precisão de dedup comparado ao baseline.
- [ ] Opt-in via `ai.enabled`.
- [ ] Testes de integração cobrindo cenários chave.

## 📊 Impacto
Médio — consolida eventos redundantes com maior robustez.

## 🔗 Relacionamento
 - EPIC: #157

## 🔗 Referências
- `src/event_processor.py`
- `src/utils/config_validator.py`
- `docs/architecture/ai_implementation_plan.md`
- `requirements.txt`
