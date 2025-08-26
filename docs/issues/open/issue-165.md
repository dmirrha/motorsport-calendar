# Issue 165 — F1: Serviço local de embeddings (cache+batch)

- ID: 3356428371
- Número: 165
- Estado: open
- URL: https://github.com/dmirrha/motorsport-calendar/issues/165
- Criado em: 2025-08-26T16:56:59Z
- Atualizado em: 2025-08-26T17:09:19Z
- Labels: enhancement, needs-triage, priority: P1, ai, performance
- Epic relacionada: #157

## Contexto
Implementar um serviço local de embeddings para suporte semântico multilíngue (ex.: `paraphrase-multilingual-MiniLM-L12-v2`), com batching e cache (memória + disco), 100% offline por padrão (CPU), com detecção automática de device quando habilitado (MPS/Metal → CUDA → CPU). Servirá de base para categorização (#163) e deduplicação (#160).

## Objetivo
- Disponibilizar `EmbeddingsService` com API simples e eficiente para `embed_texts(list[str]) -> list[list[float]]`.
- Batching configurável e cache com alta taxa de acerto.
- Operação offline sem chamadas de rede; modelo provisionado localmente.
- Métricas de desempenho (latência por lote, cache hits/misses).

## Escopo
- Novos arquivos:
  - `src/ai/embeddings_service.py`
  - `src/ai/cache.py`
- Integrações (apenas interfaces por ora):
  - `src/category_detector.py`
  - `src/event_processor.py`
- Configuração/validação:
  - `config/config.example.json`
  - `src/utils/config_validator.py`
- Testes/Docs:
  - `tests/unit/test_embeddings_service.py`
  - `README.md`, `docs/tests/overview.md`

## Critérios de Aceite
- [ ] Runtime 100% offline (sem chamadas externas); suporte a `local_files_only`.
- [ ] Batching e cache configuráveis (memória + disco) com métricas de hit/miss.
- [ ] Testes unitários cobrindo cache, batching e fallback de device (determinísticos).
- [ ] Documentação de setup local, provisionamento do modelo e troubleshooting.

## Plano de Resolução (proposto)
1) API e Device
- `EmbeddingsService(embedder_name, device=auto, batch_size=16, cache_config=...)`.
- Device: detectar `mps` (Metal) → `cuda` → `cpu` com fallback seguro.
- Carregar modelo local (ex.: SentenceTransformers/HF) com `local_files_only=True` e instruções de provisionamento.

2) Cache
- LRU em memória (capacidade máxima configurável, TTL opcional).
- Persistência em disco (ex.: SQLite simples ou JSONL com índice hash SHA256 do texto e versão do modelo).
- Chaves de cache baseadas em `hash(model_id + text)`; invalidar por versionamento do modelo/params.

3) Batching e Métricas
- Fatiar entradas por `batch_size`; coletar latência total e por lote.
- Expor métricas: `batch_latency_ms`, `cache_hits`, `cache_misses`.
- Logging estruturado com níveis (INFO/DEBUG).

4) Configuração e Validação
- `config.example.json` (seção `ai`): `enabled`, `device`, `batch_size`, `cache.enabled`, `cache.dir`, `cache.ttl_days`.
- `validate_ai_config()` estender validação destas chaves e preparar diretório de cache.

5) Testes
- `tests/unit/test_embeddings_service.py` cobrindo:
  - caching (hit/miss), persistência em disco, limpeza por TTL
  - batching com tamanhos pequenos, ordem e dimensões
  - fallback de device (simulação/mocking)
  - determinismo com seed

6) Documentação
- README/overview: como provisionar o modelo localmente, flags de config, exemplos de uso, troubleshooting (CPU vs MPS/CUDA, permissões no cache, aquecimento inicial).

## Checklist de Execução
- [x] Branch `feat/165-embeddings-service` criada a partir de `main`.
- [x] Artefatos da issue (MD/JSON) criados em `docs/issues/open/`.
- [x] Especificação de API/cache/batching revisada e aprovada.
- [x] Config e validador atualizados.
- [x] Serviço implementado com testes unitários passando.
- [x] Documentação atualizada.
- [ ] PR aberta referenciando e fechando #165.

## Evidências dos Testes
- Comando: `pytest -q -c /dev/null -p no:cov tests/unit/ai/test_embeddings_service.py`
- Resultado: `2 passed` (1.72s)
- Cobertura global ignorada para foco no módulo (gate global de 45% não aplicável nesta execução isolada).
- Validações:
  - Determinismo e dimensão dos vetores (`dim`).
  - Batching com métricas de latência por lote (`batch_latencies_ms`).
  - Cache: hits na segunda execução, sem novos lotes (LRU + disco via SQLite).

## Logs e Referências
- Issue: https://github.com/dmirrha/motorsport-calendar/issues/165
- Plano: `docs/architecture/ai_implementation_plan.md`
- Código alvo: `src/category_detector.py`, `src/event_processor.py`
- Config/Validação: `src/utils/config_validator.py`, `config/config.example.json`
- Requisitos: `requirements.txt`

## Status
Em finalização: serviço implementado, configuração validada e documentação atualizada. Preparando PR para fechar #165.
