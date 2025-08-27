 
## Diretórios de saída e artefatos

- `output/`: diretório onde os arquivos `.ics` são gerados (mantém `output/.gitkeep`).
- `logs/`: diretório para logs e payloads (`logs/rotated_logs/`, `logs/payloads/`).
- `tests/regression/test_data/output/`: artefatos gerados por testes de regressão (ignorado pelo Git).

Esses caminhos não exigem configuração específica, mas podem ser ajustados via parâmetros em `config.json` (ex.: `general.output_directory`, opções em `logging.file_structure`).
# Guia de Configuração do Motorsport Calendar Generator

Este documento descreve todas as opções de configuração disponíveis no arquivo `config.json` do Motorsport Calendar Generator.

> Nota pós-rollback (0.5.1)
>
> O projeto foi revertido para o snapshot do commit `9362503`. Algumas opções documentadas podem se referir a funcionalidades que serão reintroduzidas em PRs futuros. Consulte `RELEASES.md` para detalhes.

## Visão Geral

O arquivo de configuração é dividido em várias seções principais, cada uma responsável por aspectos específicos do comportamento da aplicação. Todas as configurações são opcionais, com valores padrão sensíveis fornecidos internamente.

## Seção: `general`

Configurações gerais da aplicação.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `timezone` | string | `"America/Sao_Paulo"` | Fuso horário padrão para os eventos |
| `language` | string | `"pt-BR"` | Idioma preferido para os textos da aplicação |
| `log_level` | string | `"INFO"` | Nível de log global (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `output_directory` | string | `"./output"` | Diretório para salvar os arquivos iCal gerados |

### Subseção: `visual_interface`

Configurações da interface visual.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `enabled` | boolean | `true` | Habilita/desabilita a interface visual |
| `colors` | boolean | `true` | Habilita/desabilita cores na saída do console |
| `progress_bars` | boolean | `true` | Habilita/desabilita barras de progresso |
| `icons` | boolean | `true` | Habilita/desabilita ícones na saída |

### Subseção: `advanced_logging`

Configurações avançadas de log.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `debug_logs` | boolean | `true` | Habilita logs de depuração detalhados |
| `payload_storage` | boolean | `true` | Habilita armazenamento de payloads brutos |
| `log_rotation` | boolean | `true` | Habilita rotação automática de logs |
| `retention_days` | number | `30` | Número de dias para reter logs antigos |

### Subseção: `silent_periods`

Define períodos de silêncio onde notificações são suprimidas.

Cada período contém:

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `enabled` | boolean | Não | Se o período está ativo |
| `name` | string | Sim | Nome descritivo do período |
| `start_time` | string | Sim | Hora de início (formato HH:MM) |
| `end_time` | string | Sim | Hora de término (formato HH:MM) |
| `days_of_week` | array | Sim | Dias da semana (ex: ["monday", "tuesday"]) |

Notas de validação:
- Horários devem estar no formato HH:MM com horas 00–23 e minutos 00–59. Valores são normalizados com zero à esquerda quando necessário (ex.: `7:5` → `07:05`).
- `days_of_week` é case-insensitive; valores inválidos são ignorados. Se nenhum dia válido for informado, utiliza-se todos os dias da semana por padrão.
- `enabled` assume `true` quando omitido.
- `name` é obrigatório; quando ausente, é atribuído automaticamente como "Período N".

## Seção: `data_sources`

Configurações das fontes de dados.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `priority_order` | array | `["tomada_tempo"]` | Ordem de prioridade das fontes |
| `excluded_sources` | array | `[]` | Fontes a serem ignoradas |
| `timeout_seconds` | number | `10` | Timeout em segundos para requisições |
| `max_concurrent_sources` | number | `3` | Máximo de fontes executadas em paralelo |
| `collection_timeout_seconds` | number | `300` | Timeout total da coleta (cancela remanescentes de forma cooperativa) |
| `use_process_pool` | boolean | `false` | Executa fontes em pool de processos (isolamento opcional) |
| `per_source_timeout_seconds` | number | não definido | Timeout individual por fonte; quando ausente, não é aplicado explicitamente |
| `retry_attempts` | number | `3` | Número de tentativas (legado; sobrescrito se novas chaves de retry estiverem definidas) |
| `retry_failed_sources` | boolean | `true` | Habilita retry por fonte para erros transitórios |
| `max_retries` | number | `1` | Máximo de novas tentativas por fonte (exclui a tentativa inicial) |
| `retry_backoff_seconds` | number | `0.5` | Atraso entre tentativas (backoff linear, em segundos) |
| `rate_limit_delay` | number | `1.0` | Atraso entre requisições (segundos) |
| `user_agents` | array | Lista padrão | User-Agents para requisições HTTP |

Notas:
- Retry aplica-se apenas a exceções transitórias: `TimeoutError`, `OSError`, `IOError`.
- Compatibilidade: `retry_attempts` é mantido para configurações antigas; quando `retry_failed_sources` está presente, as novas chaves (`max_retries`, `retry_backoff_seconds`) têm precedência.
- `user_agents` é normalizado como lista de strings; valores vazios são descartados e duplicatas removidas mantendo a ordem.
- `timeout_seconds` deve ser > 0. `rate_limit_delay` e `retry_backoff_seconds` devem ser ≥ 0.
- Concorrência: `max_concurrent_sources` limita a quantidade de fontes que executam em paralelo; excedentes aguardam em fila.
- Tempo limite total: `collection_timeout_seconds` encerra a coleta restante de forma cooperativa. Implementações podem registrar avisos de cancelamento nas tarefas remanescentes.
- Timeout por fonte: quando `per_source_timeout_seconds` estiver definido e for > 0, aplica-se ao trabalho de cada fonte. Quando ausente/ inválido, não é aplicado explicitamente (o sistema depende de timeouts internos e do `collection_timeout_seconds`).
- Pool de processos: `use_process_pool` habilita execução em processos separados (isolamento de memória/CPU). Pode introduzir overhead e diferenças na ordenação dos logs; avalie manter `false` a menos que haja necessidade de isolamento.

## Seção: `event_filters`

Filtros para processamento de eventos.

### Subseção: `category_detection`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `enabled` | boolean | `true` | Habilita detecção automática de categorias |
| `learning_mode` | boolean | `true` | Habilita aprendizado de novas categorias |
| `confidence_threshold` | number | `0.7` | Limite de confiança para detecção (0-1) |

### Outros filtros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `included_categories` | array | `["*"]` | Categorias a incluir ("*" para todas) |
| `excluded_categories` | array | `[]` | Categorias a excluir |
| `included_countries` | array | `[]` | Países a incluir |
| `excluded_countries` | array | `[]` | Países a excluir |

### Subseção: `event_types`

Habilita/desabilita tipos específicos de eventos.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `race` | boolean | `true` | Corridas principais |
| `qualifying` | boolean | `true` | Treinos classificatórios |
| `practice` | boolean | `false` | Treinos livres |
| `sprint` | boolean | `true` | Corridas de sprint |
| `other` | boolean | `false` | Outros tipos de eventos |

### Subseção: `weekend_detection`

Configura a detecção de finais de semana.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `algorithm` | string | `"first_event_based"` | Algoritmo de detecção |
| `days_range` | array | `["friday", "saturday", "sunday"]` | Dias considerados do final de semana |
| `extend_to_thursday` | boolean | `false` | Estende para quinta-feira |
| `extend_to_monday` | boolean | `false` | Estende para segunda-feira |

## Seção: `quality`

Configurações relacionadas a validações leves e observabilidade de qualidade.

### Subseção: `anomaly_detection`

Avaliação opcional de anomalias em eventos após a normalização no `EventProcessor.process_events()`.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `enabled` | boolean | `false` | Habilita a detecção de anomalias |
| `hours.min` | number | `6` | Hora mínima esperada (0–23) para flag de horário improvável |
| `hours.max` | number | `23` | Hora máxima esperada (0–23) para flag de horário improvável |
| `examples_per_type` | number | `3` | Número máximo de exemplos por tipo de anomalia no resumo de logs |

Regras cobertas pelo `AnomalyDetector` (`src/utils/anomaly_detector.py`):
- Datas fora do fim de semana alvo.
- Horários improváveis (fora de `hours.min`–`hours.max`).
- Inconsistências de categoria (categoria bruta ausente e baixa confiança).
- Local ausente.

Comportamento e observabilidade:
- Execução ao final do pipeline de eventos; não bloqueia o processamento principal.
- Resumo agregado por tipo de anomalia é registrado no logger.
- Exceções durante a avaliação são capturadas e logadas; o fluxo segue normalmente.

Exemplo mínimo de configuração:

```json
{
  "quality": {
    "anomaly_detection": {
      "enabled": true,
      "hours": { "min": 6, "max": 23 },
      "examples_per_type": 3
    }
  }
}
```

## Seção: `ical_parameters`

Configurações para geração de arquivos iCal.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `calendar_name` | string | `"Motorsport Events"` | Nome do calendário |
| `calendar_description` | string | `"Weekend motorsport events calendar"` | Descrição do calendário |
| `timezone` | string | `"America/Sao_Paulo"` | Fuso horário do calendário |
| `default_duration_minutes` | number | `120` | Duração padrão dos eventos (minutos) |
| `include_streaming_links` | boolean | `true` | Inclui links de transmissão |
| `include_source_info` | boolean | `true` | Inclui informações da fonte no campo de descrição |
| `enforce_sort` | boolean | `true` | Garante ordenação determinística dos eventos no arquivo iCal |

### Subseção: `reminders`

Lembretes para os eventos.

Cada lembrete contém:

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `minutes` | number | Sim | Minutos antes do evento |

Notas:
- No snapshot atual, apenas `minutes` é utilizado pelo gerador iCal. O campo `method` (ex.: "popup"/"email") é ignorado.

### Subseção: `output`

Define opções de saída específicas do iCal.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `directory` | string | `"output"` | Diretório onde o arquivo `.ics` será gerado |
| `filename_template` | string | `"motorsport_events_{date}.ics"` | Template do nome do arquivo (usa `{date}` do primeiro evento) |

Notas:
- Essas opções em `ical_parameters.output` controlam apenas a geração do `.ics`. A opção global `general.output_directory` continua válida para outros artefatos.

Notas de compatibilidade (snapshot 0.5.1):
- Chaves legadas como `event_category`, `event_priority`, `event_status`, `include_location` e `include_description` podem existir em configurações antigas, mas não têm efeito no snapshot atual e podem ser reintroduzidas em PRs futuros.

## Seção: `streaming_providers`

Configura provedores de streaming por região.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `region` | string | `"BR"` | Região padrão |
| `mappings` | object | - | Mapeamento de categorias para provedores |
| `fallback_providers` | object | - | Provedores alternativos por região |

## Seção: `deduplication`

Configurações para remoção de eventos duplicados.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `algorithm` | string | `"fuzzy_matching"` | Algoritmo de deduplicação |
| `name_similarity_threshold` | number | `0.85` | Limite de similaridade de nomes (0-1) |
| `time_tolerance_minutes` | number | `30` | Tolerância de tempo (minutos) |
| `location_matching` | boolean | `true` | Considerar localização na deduplicação |
| `category_matching` | boolean | `true` | Considerar categoria na deduplicação |
| `source_priority_resolution` | boolean | `true` | Resolver conflitos por prioridade da fonte |

## Seção: `category_mapping`

Mapeamento de categorias e classificação.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `learning_enabled` | boolean | `true` | Habilita aprendizado de mapeamentos |
| `custom_mappings` | object | - | Mapeamentos personalizados de nomes para categorias |
| `type_classification` | object | - | Classificação de tipos de veículos |

## Seção: `ai`

Configurações de recursos de IA locais (desabilitados por padrão).

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `enabled` | boolean | `false` | Habilita a seção de IA |
| `device` | string | `"auto"` | Dispositivo de execução: `auto`, `cpu`, `cuda`, `mps` |
| `batch_size` | number | `16` | Tamanho do lote para inferências |

### Subseção: `thresholds`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `category` | number | `0.75` | Limite de confiança (0–1) para decisões de categoria |
| `dedup` | number | `0.85` | Limite (0–1) para deduplicação baseada em similaridade |

### Subseção: `onnx`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `enabled` | boolean | `false` | Habilita execução via ONNX Runtime |
| `provider` | string | `"cpu"` | Provider (shorthand): `cpu`, `cuda`, `coreml`, `dml` |
| `opset` | number | `17` | Versão mínima suportada: `>= 11` |

### Subseção: `cache`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `enabled` | boolean | `true` | Habilita cache local (ex.: embeddings) |
| `dir` | string | `"cache/embeddings"` | Diretório do cache; criado se não existir |
| `ttl_days` | number | `30` | Tempo de vida (dias) para limpeza de itens de cache (>= 0) |

Notas:
- `device` e `provider` são case-insensitive e validados. Valores inválidos geram erro de validação.
- `dir` é convertido para caminho absoluto e criado automaticamente; é exigida permissão de escrita. Falhas na preparação do diretório são reportadas como `OUTPUT-5000-ERROR`.
- Quando `enabled=false`, a seção pode permanecer configurada para uso futuro, mas não será utilizada.

### Configuração de Embeddings ONNX

O serviço de embeddings suporta modelos ONNX para inferência acelerada, com fallback para o método de hashing padrão quando desabilitado.

```json
{
  "ai": {
    "enabled": true,
    "onnx": {
      "enabled": true,
      "model_path": "models/embeddings-onnx/model.onnx",
      "providers": ["CPUExecutionProvider"]
    },
    "device": "auto",
    "batch_size": 64,
    "cache": {
      "enabled": true,
      "dir": "cache/embeddings",
      "ttl_days": 7
    }
  }
}
```

#### Opções de Configuração

| Seção | Parâmetro | Tipo | Padrão | Descrição |
|-------|-----------|------|--------|-----------|
| `ai` | `enabled` | boolean | `true` | Habilita/desabilita todo o subsistema de IA |
| `ai.onnx` | `enabled` | boolean | `false` | Habilita o backend ONNX (requer modelo) |
|  | `model_path` | string | - | Caminho para o arquivo .onnx (obrigatório se `enabled=true`) |
|  | `providers` | array | `["CPUExecutionProvider"]` | Provedores de inferência em ordem de preferência |
| `ai` | `device` | string | `"auto"` | Dispositivo para inferência (`auto`, `cpu`, `cuda`, `mps`) |
|  | `batch_size` | integer | `64` | Tamanho do lote para processamento paralelo |
| `ai.cache` | `enabled` | boolean | `true` | Habilita cache de embeddings |
|  | `dir` | string | `"cache/embeddings"` | Diretório para armazenar o cache em disco |
|  | `ttl_days` | integer | `7` | Dias até a expiração dos itens em cache |

#### Provedores Suportados

| Provedor | Plataforma | Requisitos |
|----------|------------|-------------|
| `CPUExecutionProvider` | CPU | - |
| `CUDAExecutionProvider` | NVIDIA GPU | CUDA + cuDNN |
| `CoreMLExecutionProvider` | Apple Silicon | macOS 11+ |
| `DmlExecutionProvider` | DirectML | Windows 10+ |

Notas sobre providers:
- Você pode informar providers usando shorthand (`cpu`, `cuda`, `coreml`, `dml`) ou os nomes completos do ONNX Runtime (`CPUExecutionProvider`, `CUDAExecutionProvider`, etc.).
- A validação normaliza para a forma shorthand em minúsculas e filtra valores inválidos. Quando nenhum válido for informado, o fallback é `cpu`.
- A ordem de preferência é respeitada. Internamente, os nomes são mapeados para os equivalentes do ONNX Runtime ao criar a sessão.

#### Métricas de Desempenho

O serviço expõe as seguintes métricas via `EmbeddingsService.metrics`:

- `batch_latencies_ms`: Lista de latências por lote (em milissegundos)
- `cache_hits`: Número de acertos de cache
- `cache_misses`: Número de falhas de cache
- `onnx_init_time_ms`: Tempo de inicialização do runtime ONNX
- `last_error`: Último erro ocorrido (se houver)

#### Notas de compatibilidade e tipos de saída
- Backend ONNX retorna embeddings como `np.ndarray` (`float32`).
- Backend hashing retorna embeddings como listas de `float` (determinístico, 100% offline).
- O cache persiste embeddings como listas JSON-serializáveis; ao ler do cache, o backend ONNX converte de volta para `np.ndarray(float32)` automaticamente.
- Para eficiência, o backend ONNX realiza uma única chamada de inferência por lote; quando aplicável, itens além do primeiro no mesmo lote podem usar o fallback hashing para manter compatibilidade de desempenho e testes.
### Categorização semântica offline (determinística)

Esta funcionalidade complementa a detecção heurística de categorias. Quando `ai.enabled=true`, um classificador semântico local e determinístico é utilizado para sugerir a categoria de eventos com base em embeddings estáticos e comparação por distância (L2), sem chamadas externas.

- Parâmetros principais:
  - `ai.enabled` (bool, padrão `false`): habilita recursos de IA locais, incluindo categorização semântica.
  - `ai.thresholds.category` (float, padrão `0.75`): confiança mínima para aceitar a predição semântica.
  - `ai.batch_size` (int, padrão `16`): tamanho de lote para inferência offline.
  - `ai.device` (string, padrão `"auto"`): `auto`, `cpu`, `cuda`, `mps`.
  - `ai.cache.enabled` (bool, padrão `true`): cache local de embeddings para acelerar execuções repetidas.

- Natureza offline e determinística:
  - Não realiza chamadas de rede; roda 100% on-device.
  - Embeddings determinísticos via hashing n‑gram e comparação L2; resultados reprodutíveis com mesma entrada e configuração.

- Integração com a heurística existente:
  - A heurística continua sendo aplicada. A categorização semântica só é usada quando habilitada e quando a confiança calculada ultrapassa `ai.thresholds.category`.
  - Aliases e mapeamentos canônicos existentes em `CategoryDetector` permanecem com prioridade quando há match de alta confiança.

- Observabilidade em runtime:
  - Respeita configurações de UI em `general.visual_interface` (barras de progresso, ícones, cores) quando disponíveis.
  - Métricas e contadores de eventos são atualizados normalmente (sem telemetry externa).

Exemplo mínimo de configuração:

```json
{
  "ai": {
    "enabled": true,
    "device": "auto",
    "batch_size": 16,
    "thresholds": { "category": 0.75 },
    "cache": { "enabled": true }
  }
}
```

Referências de implementação: `src/ai/embeddings_service.py` e integrações no `CategoryDetector`.

### Deduplicação semântica offline (determinística)

Quando `ai.enabled=true`, o serviço de embeddings determinísticos também pode auxiliar na remoção de duplicatas, comparando similaridade semântica entre pares candidatos de eventos. Essa abordagem complementa o algoritmo heurístico de deduplicação (ex.: similaridade de nome/timestamps/local), não o substitui.

- Parâmetros principais:
  - `ai.enabled` (bool, padrão `false`): habilita os recursos de IA locais.
  - `ai.thresholds.dedup` (float, padrão `0.85`): limiar mínimo de similaridade (0–1) para considerar dois eventos como duplicados do ponto de vista semântico.
  - `ai.batch_size` (int, padrão `16`): tamanho de lote nas comparações.
  - `ai.device` (string, padrão `"auto"`): `auto`, `cpu`, `cuda`, `mps`.
  - `ai.cache.*`: acelera reavaliações mantendo embeddings localmente.

- Integração com `deduplication.*`:
  - O resultado semântico é combinado com as regras de `deduplication` (por exemplo `time_tolerance_minutes`, `source_priority_resolution`, `location_matching`, `category_matching`).
  - A deduplicação é aplicada quando o escore semântico ≥ `ai.thresholds.dedup` e as demais condições configuradas são satisfeitas. Em conflitos, a resolução por prioridade de fonte (`source_priority_resolution=true`) define qual evento permanece.

- Natureza offline/determinística:
  - Não há chamadas externas; execução 100% on‑device.
  - Embeddings determinísticos com hashing n‑gram e comparação por distância; resultados reprodutíveis para mesma entrada/configuração.

Exemplo mínimo de configuração:

```json
{
  "ai": {
    "enabled": true,
    "device": "auto",
    "batch_size": 16,
    "thresholds": { "dedup": 0.85 },
    "cache": { "enabled": true, "dir": "cache/embeddings", "ttl_days": 30 }
  },
  "deduplication": {
    "algorithm": "fuzzy_matching",
    "name_similarity_threshold": 0.85,
    "time_tolerance_minutes": 30,
    "location_matching": true,
    "category_matching": true,
    "source_priority_resolution": true
  }
}
```

Observabilidade e validação:
- Logs detalham pares avaliados, escores e decisões (INFO/DEBUG), respeitando `general.visual_interface` quando aplicável.
- Benchmarks e métricas (precision, recall, F1) podem ser produzidos via `scripts/eval/benchmarks.py` (ver `README.md`).
- Parâmetros são validados; valores fora de faixa geram erros de validação (consulte `src/utils/config_validator.py`).

## Seção: `logging`

Configurações detalhadas de log.

### Subseção: `file_structure`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `main_log` | string | `"logs/motorsport_calendar.log"` | Arquivo de log principal |
| `debug_directory` | string | `"logs/debug"` | Diretório para logs de depuração |
| `payload_directory` | string | `"logs/payloads"` | Diretório para armazenar payloads |

### Subseção: `retention`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `enabled` | boolean | `true` | Habilita retenção de logs |
| `max_logs_to_keep` | number | `10` | Número máximo de arquivos de log |
| `max_payloads_to_keep` | number | `20` | Número máximo de payloads |
| `delete_older_than_days` | number | `30` | Excluir arquivos mais antigos que X dias |

### Subseção: `levels`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `console` | string | `"INFO"` | Nível de log para console |
| `file` | string | `"DEBUG"` | Nível de log para arquivo |
| `debug_file` | string | `"DEBUG"` | Nível de log para arquivo de depuração |

### Subseção: `format`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `console` | string | Formato padrão | Formato para saída no console |
| `file` | string | Formato detalhado | Formato para arquivos de log |

Notas (formatos padrão quando não definidos em `config.json`):

```json
{
  "console": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  "file": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
}
```

### Subseção: `rotation`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `enabled` | boolean | `true` | Habilita rotação de logs |
| `max_size_mb` | number | `10` | Tamanho máximo do arquivo (MB) |
| `backup_count` | number | `5` | Número de backups a manter |

### Subseção: `payload_settings`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `save_raw` | boolean | `true` | Salva payloads brutos |
| `pretty_print` | boolean | `true` | Formatação legível dos payloads |
| `include_headers` | boolean | `true` | Inclui cabeçalhos HTTP |
| `separate_by_source` | boolean | `true` | Separa por fonte de dados |
| `compress` | boolean | `true` | Comprime payloads salvos para economizar espaço |
| `max_files_per_source` | number | `50` | Máximo de arquivos de payload por fonte (rotação por quantidade) |
| `max_age_days` | number | `30` | Remove payloads mais antigos que X dias (limpeza por idade) |

## Exemplo Completo

Consulte `config/config.example.json` para um exemplo completo de configuração com todas as opções.

## Atualizando a Configuração

1. Faça uma cópia de segurança do seu arquivo `config.json` atual
2. Atualize as seções necessárias
3. Teste a configuração com: `python motorsport_calendar.py --validate-config`
4. Verifique os logs para possíveis avisos ou erros

## Solução de Problemas

- **Configuração inválida**: Verifique a sintaxe JSON e os valores aceitos
- **Permissões**: Certifique-se de que a aplicação tem permissão para escrever nos diretórios especificados
- **Logs**: Consulte o arquivo de log principal para mensagens de erro detalhadas

## Timezone e Comparações de Datas
- Todas as comparações de datas/horas são realizadas com objetos timezone-aware.
- Configure a timezone via `ConfigManager.get_timezone()` (padrão: America/Sao_Paulo).
- `EventProcessor.process_events()` normaliza `target_weekend` (datetime/tupla) para a timezone configurada antes do filtro do fim de semana.
