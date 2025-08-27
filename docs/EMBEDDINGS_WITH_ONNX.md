# Serviço de Embeddings com ONNX

Este documento descreve como utilizar o serviço de embeddings com suporte a ONNX no projeto Motorsport Calendar.

## Visão Geral

O serviço de embeddings foi aprimorado para suportar modelos ONNX, permitindo:

- **Aceleração de hardware**: CPU, NVIDIA GPU (CUDA) e Apple Silicon (CoreML)
- **Benchmark integrado**: Compare o desempenho entre backends
- **Cache inteligente**: Reduza a latência com cache em memória e disco
- **Fallback automático**: Volta para o backend de hashing se o ONNX não estiver disponível

## Configuração

### Dependências

Instale as dependências opcionais do ONNX:

```bash
pip install onnx onnxruntime optimum onnxconverter-common
```

### Configuração do Serviço

No arquivo `config.json`, adicione ou atualize a seção `ai`:

```json
{
  "ai": {
    "enabled": true,
    "backend": "onnx",
    "onnx": {
      "enabled": true,
      "model_path": "models/embeddings-onnx/model.onnx",
      "providers": ["CPUExecutionProvider"]
    },
    "dim": 384,
    "batch_size": 32,
    "cache": {
      "enabled": true,
      "dir": "cache/embeddings",
      "ttl_days": 7
    }
  }
}
```

### Opções de Configuração

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `ai.enabled` | boolean | `true` | Habilita/desabilita todo o subsistema de IA |
| `ai.backend` | string | `"hashing"` | Backend a ser usado (`"hashing"` ou `"onnx"`) |
| `ai.onnx.enabled` | boolean | `false` | Habilita o backend ONNX |
| `ai.onnx.model_path` | string | - | Caminho para o arquivo .onnx |
| `ai.onnx.providers` | array | `["CPUExecutionProvider"]` | Provedores de inferência em ordem de preferência |
| `ai.dim` | integer | `256` | Dimensão dos vetores de embedding |
| `ai.batch_size` | integer | `32` | Tamanho do lote para inferência |
| `ai.cache.enabled` | boolean | `true` | Habilita cache de embeddings |
| `ai.cache.dir` | string | `"cache/embeddings"` | Diretório para armazenar o cache em disco |
| `ai.cache.ttl_days` | integer | `7` | Dias até a expiração dos itens em cache |

## Provedores Suportados

| Provedor | Plataforma | Requisitos |
|----------|------------|------------|
| `CPUExecutionProvider` | CPU | - |
| `CUDAExecutionProvider` | NVIDIA GPU | CUDA + cuDNN |
| `CoreMLExecutionProvider` | Apple Silicon | macOS 11+ |
| `DmlExecutionProvider` | DirectML | Windows 10+ |

## Exportando Modelos para ONNX

### Usando o Script de Exportação

O projeto inclui um script para exportar modelos do Hugging Face para ONNX:

```bash
python scripts/eval/export_onnx.py \
  --model_id sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 \
  --output_dir models/embeddings-onnx \
  --quantize
```

### Opções do Script

| Argumento | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `--model_id` | string | - | ID do modelo no Hugging Face Hub |
| `--output_dir` | string | - | Diretório de saída para o modelo ONNX |
| `--quantize` | flag | `False` | Aplica quantização dinâmica (recomendado para CPU) |
| `--fp16` | flag | `False` | Usa precisão FP16 (para GPUs modernas) |
| `--opset` | int | `12` | Versão do Opset do ONNX |

## Executando Benchmarks

Compare o desempenho entre diferentes backends:

```bash
python scripts/eval/benchmarks.py \
  --task embeddings \
  --engine both \
  --onnx-model models/embeddings-onnx/model.onnx \
  --providers cpu cuda
```

### Métricas Coletadas

- **Latência por lote** (ms)
- **Taxa de acertos no cache** (%)
- **Uso de memória** (MB)
- **Taxa de transferência** (textos/segundo)

## Exemplo de Uso no Código

```python
from src.ai import EmbeddingsService, EmbeddingsConfig

# Configuração
cfg = EmbeddingsConfig(
    enabled=True,
    backend="onnx",
    onnx_enabled=True,
    onnx_model_path="models/embeddings-onnx/model.onnx",
    onnx_providers=["CPUExecutionProvider"],
    dim=384,
    batch_size=32,
    cache_enabled=True,
    cache_dir="cache/embeddings",
    ttl_days=7
)

# Cria o serviço
svc = EmbeddingsService(cfg)

# Gera embeddings
texts = ["F1 Grande Prêmio do Brasil", "MotoGP Argentina"]
embeddings = svc.embed_texts(texts)

# Acessa métricas
print(f"Cache hits: {svc.metrics['cache_hits']}")
print(f"Cache misses: {svc.metrics['cache_misses']}")
print(f"Latência média: {sum(svc.metrics['batch_latencies_ms'])/len(svc.metrics['batch_latencies_ms']):.2f}ms")
```

## Solução de Problemas

### Erro ao Carregar o Modelo

- Verifique se o caminho do modelo está correto
- Confirme que o arquivo .onnx é válido
- Verifique as permissões do arquivo

### Desempenho Ruim

- Aumente o `batch_size` para melhor utilização da GPU
- Use `CUDAExecutionProvider` para GPUs NVIDIA
- Ative a quantização com `--quantize` para CPUs

### Falha na Inicialização

- Verifique se todas as dependências estão instaladas
- Confira os logs para mensagens de erro específicas
- Tente reiniciar o serviço

## Limitações

- O modelo ONNX deve ser compatível com o formato de entrada/saída esperado
- A quantização pode reduzir ligeiramente a qualidade dos embeddings
- O cache em disco pode consumir espaço significativo para grandes conjuntos de dados
