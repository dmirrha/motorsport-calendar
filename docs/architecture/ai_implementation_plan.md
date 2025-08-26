# Plano de Implementação de IA — Motorsport Calendar

Este plano detalha como implementar as melhorias de IA descritas na Seção 8 do relatório técnico (`docs/architecture/race_calendar_technical_report.md`), focando em:
- Reduzir a quantidade de tecnologias/modelos (evitar over-engineering)
- Execução local/offline, reuso máximo e degradação graciosa
- Metas mensuráveis (KPIs) e rollout por fases com testes e rastreabilidade

---

## 1) Objetivos e KPIs (alinhados à Seção 8)

- Categorias: reduzir em 60% eventos mal categorizados
- Deduplicação: reduzir em 80% falsos positivos de duplicata
- Anomalias: alcançar 95% de precisão na identificação (opcional Fase 2)

Medição: criar um conjunto de validação rotulado mínimo (amostragem dos testes de integração atuais + amostras adicionais), com métricas baseline vs. pós-IA.

---

## 2) Estratégia de IA Minimalista

- Núcleo comum: **um único modelo de embeddings** multilíngue, reutilizado para categorização e deduplicação.
- Execução local: CPU-first, sem chamadas externas; cache em disco para embeddings.
- Dependências enxutas: começar com `sentence-transformers` + `onnxruntime` (opcional). Avaliar quantização INT8 posteriormente.
- Degradação graciosa: recursos de IA são opcionais e possuem fallback para heurísticas atuais.

Modelo proposto (multilíngue, leve): `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- Razões: bom custo/benefício, cobre PT/EN, tamanho moderado, amplamente usado.
- Alternativa futura (se exigido por footprint): exportar para ONNX e quantizar com `onnxruntime`.

---

## 3) Componentes e Pontos de Integração

- Embeddings (comum)
  - Novo utilitário: `src/ai/embeddings.py`
  - Funções: carregar modelo único; gerar embeddings para textos; cache local.
  - Uso: chamado por categorização e deduplicação.

- Categorização Inteligente (Seção 8.1)
  - Integração em `src/category_detector.py` (sem quebrar API pública)
  - Lógica: calcular embedding de título (e opcionalmente local/descrição), comparar com protótipos de categorias; se `score >= threshold`, classificar como semântica; senão, manter heurísticas atuais.

- Deduplicação Semântica (Seção 8.2)
  - Integração em `src/event_processor.py` na etapa de deduplicação
  - Lógica multiestágio:
    1) Filtros rápidos (mesma data/mesmo circuito aproximado → candidatos)
    2) Fuzzy/string matching atual
    3) Apenas para pares inconclusivos: similaridade de embeddings; se `similaridade >= threshold`, consolidar.

- Detecção de Anomalias (Seção 8.3) — Fase 2 opcional
  - Novo: `src/anomaly_detector.py` (regra-primeiro)
  - Integração: no passo de auditoria antes do iCal (em `motorsport_calendar.py`)
  - Começar com regras determinísticas (datas inválidas, TZs suspeitas, duração incomum, baixa confiança de categoria), depois considerar `IsolationForest` com `scikit-learn`.

---

## 4) Arquitetura Lógica (Pipeline)

```
Coleta (src/data_collector.py)
   ↓
Normalização (src/event_processor.py)
   ↓
Categorização (src/category_detector.py) ← usa embeddings
   ↓
Deduplicação (src/event_processor.py) ← usa embeddings (apenas candidatos)
   ↓
[Opcional] Anomalias (src/anomaly_detector.py) ← regra-primeiro
   ↓
Geração iCal (src/ical_generator.py)
```

---

## 5) Configuração (mínima e opcional)

Arquivo `config.json` — nova seção compacta e coerente com a arquitetura atual:

```json
{
  "ai": {
    "enabled": true,
    "embed_model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "cache_dir": "./.cache/embeddings",
    "categorization": {"enabled": true, "threshold": 0.75},
    "dedup": {"enabled": true, "threshold": 0.85},
    "anomaly": {"rules_enabled": true, "ml_enabled": false}
  }
}
```

Validador (`src/utils/config_validator.py`):
- Garantir tipos e intervalos (0–1 para thresholds)
- Verificar diretórios de cache e permissões
- Habilitar por padrão `ai.enabled=false` para não impactar testes existentes

---

## 6) Detalhes de Implementação

- `src/ai/embeddings.py`
  - Classe `EmbeddingService` com:
    - `__init__(model_name, cache_dir, device="cpu")`
    - `embed_texts(list[str]) -> np.ndarray` (batching + cache)
    - Cache em disco (ex.: SQLite/DBM ou `joblib` + hash do texto)
  - Carregamento lazy e singleton por processo para evitar re-load

- `src/category_detector.py`
  - Nova rota de decisão:
    1) Se houver `raw_category` válida: manter heurística prioritária (estado atual)
    2) Caso contrário: `EmbeddingService` → similaridade com protótipos de categoria
    3) Abaixo do threshold: fallback heurístico (atual)
  - Prototipagem de categorias: lista fixa de rótulos/descrições com embeddings pré-computados e cacheados
  - Sinais de confiabilidade: `category_confidence` e `source="semantic" | "pattern_matching" | "pattern_matching+context"`

- `src/event_processor.py` (deduplicação)
  - Pré-filtro: janela temporal e local aproximado para reduzir pares
  - Fase 1: regras atuais (fuzzy/normalização)
  - Fase 2 (apenas para pares borderline): embeddings
  - Consolidação: merge de campos preservando informações únicas das fontes
  - Telemetria: contadores de casos evitados/confirmados por embeddings

- `src/anomaly_detector.py` (opcional)
  - Regras iniciais: TZ inválida, duração fora de faixa, datas invertidas, título suspeito, baixa confiança de categoria
  - Saída: lista de alertas com severidade e recomendação
  - Integração de logs estruturados via `src/logger.py`

- Performance e memória
  - Batch embeddings (ex.: 64–128) e cache agressivo
  - Limite de custo: `ai.max_embeddings_per_run` (opcional) para evitar explosões em execuções grandes

---

## 7) Dependências e Execução Local

- Pacotes (extra opcional `ai`):
  - `sentence-transformers`
  - `onnxruntime` (opcional)
- Execução local/offline:
  - Primeira execução faz cache do modelo em `~/.cache` (ou `cache_dir`)
  - Pré-carregar via Makefile/script (download local) para ambientes CI/offline
- Quantização (opcional):
  - Futuro: exportar para ONNX + INT8 para reduzir memória e startup

---

## 8) Plano de Entrega por Fases

- Fase 0 — Baseline e dados de avaliação (1–2 dias)
  - Extrair amostras rotuladas dos testes de integração (PT/EN)
  - Medir baseline de erro de categoria e falsos-positivos de duplicata

- Fase 1 — Embeddings + Categorização (2–3 dias)
  - `src/ai/embeddings.py` + cache
  - Protótipos de categoria + integração em `src/category_detector.py`
  - Flag `ai.enabled=false` por padrão; testes dedicados com `ai.enabled=true`

- Fase 1b — Deduplicação Semântica (2–3 dias)
  - Integração condicionada no `src/event_processor.py`
  - Métricas: variação de FP/latência vs baseline

- Fase 2 — Anomalias (regra-primeiro) (1–2 dias, opcional)
  - `src/anomaly_detector.py`, logs e GITHUB_STEP_SUMMARY opcional

- Fase 3 — Otimizações (opcional)
  - ONNX/quantização, tuning de thresholds, limpeza de dependências

Cada fase encerra com: atualização de docs, `CHANGELOG.md`, `RELEASES.md`, e rastreabilidade em `docs/issues/*` (conforme política do repositório).

---

## 9) Plano de Testes

- Unit
  - Mock de `EmbeddingService` para vetores determinísticos
  - Cache: acertos/misses; hashing de texto; concorrência básica
- Integração
  - Cenários com `ai.enabled=false` (status quo) — não pode quebrar
  - Cenários com `ai.enabled=true` focados em PT/EN e nomes ambíguos
- Métricas/KPIs
  - Script de avaliação: relata % de erro de categoria e FP de duplicata vs baseline
- Performance
  - Orçamentos-alvo: +<200ms/100 eventos para categorização; dedup somente em pares candidatos

---

## 10) Riscos e Mitigações

- Peso de dependências (PyTorch/Transformers)
  - Mitigar com ONNX/`onnxruntime` e cache
- Variação linguística
  - Modelo multilíngue + manutenção de heurísticas atuais
- Latência
  - Cache agressivo + batching + limitação de candidatos na dedup
- Mudanças de sites/fontes
  - IA não substitui validações existentes; apenas complementa

---

## 11) Impactos em Documentação e Governança

- Atualizar ao final de cada fase (conforme política do repositório):
  - `CHANGELOG.md`, `RELEASES.md`, `README.md`, `docs/CONFIGURATION_GUIDE.md`, `PROJECT_STRUCTURE.md`
  - Exemplos em `config/config.example.json` (nova seção `ai`)
  - Rastreabilidade em `docs/issues/open/*.md|json`

---

## 12) Solicitação de Validação

- Confirmar:
  - Uso de **um único modelo** (`paraphrase-multilingual-MiniLM-L12-v2`) para categorização e deduplicação
  - Fase 2 (anomalias) como opcional, começando por regras
  - `ai.enabled=false` como padrão, ativado via config por opt-in
  - Thresholds iniciais: categorização 0.75; dedup 0.85

Após aprovação, sigo para Fase 0 (baseline) e Fase 1 (categorização) conforme este plano.
