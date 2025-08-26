# F1: Serviço local de embeddings (cache+batch)

## 📝 Descrição
Implementar um serviço local de embeddings para suporte semântico (multilíngue) usando modelo `paraphrase-multilingual-MiniLM-L12-v2`, com batching e cache (memória/disco), executando offline (CPU por padrão; GPU/MPS se disponível).

## 🔍 Contexto
- Integrações futuras: categorização (issue #147) e deduplicação (issue #148).
- Padrão opt-in: `ai.enabled=false`.
- Arquivos alvo: `src/ai/embeddings_service.py`, `src/ai/cache.py` (novos), integração via `src/category_detector.py` e `src/event_processor.py`.

## 🎯 Comportamento Esperado
- Serviço carrega modelo localmente; sem chamadas de rede.
- Cache hit-rate reportável; batching configurável.
- Fallback seguro: se `ai.enabled=false`, não deve impactar pipeline.

## 🛠️ Passos
1. Criar `src/ai/embeddings_service.py` com interface simples: `embed_texts(list[str]) -> list[vec]`.
2. Implementar cache LRU em memória e cache persistente opcional em disco (`ai.cache_dir`).
3. Suportar `ai.device=auto` (CPU/MPS/GPU) e `ai.batch_size`.
4. Logging e métricas: tempo por lote, cache hits/misses.
5. Testes unitários determinísticos (seed) com lotes pequenos.

## 📋 Critérios de Aceitação
- [ ] Rodar 100% offline; sem dependências de rede em runtime.
- [ ] Batching e cache habilitados e configuráveis.
- [ ] Testes unitários cobrindo casos de cache, batch e device fallback.
- [ ] Documentação de setup e troubleshooting local.

## 📊 Impacto
Médio/Alto — base para recursos semânticos com controle de performance local.

## 🔗 Referências
- Plano: `docs/architecture/ai_implementation_plan.md`
- Código: `src/category_detector.py`, `src/event_processor.py`
- Config: `src/utils/config_validator.py`, `config/config.example.json`
- Requisitos: `requirements.txt`
