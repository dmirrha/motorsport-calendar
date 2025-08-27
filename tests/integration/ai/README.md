# Testes de Integração - Módulo de IA

Este diretório contém testes de integração para os componentes de IA do projeto, com foco no serviço de embeddings com suporte a ONNX.

## Estrutura de Arquivos

```
tests/integration/ai/
├── __init__.py
├── test_onnx_embeddings_integration.py  # Testes de integração do serviço de embeddings com ONNX
└── README.md                            # Este arquivo
```

## Pré-requisitos

Para executar os testes de integração com suporte a ONNX, é necessário ter instalado:

```bash
pip install onnx onnxruntime optimum onnxconverter-common
```

## Configuração do Ambiente

### 1. Exportar o Modelo de Teste

Antes de executar os testes de integração, você precisa exportar um modelo ONNX de teste:

```bash
# A partir do diretório raiz do projeto
python scripts/export_test_onnx_model.py
```

Este comando irá:
1. Baixar um modelo pequeno do Hugging Face
2. Exportá-lo para o formato ONNX
3. Salvar em `tests/data/onnx/model.onnx`

### 2. Variáveis de Ambiente

Os testes de integração podem ser controlados com as seguintes variáveis de ambiente:

- `SKIP_ONNX_TESTS`: Define como "true" para pular todos os testes de integração ONNX
- `ONNX_TEST_DEVICE`: Define o dispositivo para execução ("cpu", "cuda", "coreml")

## Executando os Testes

### Executar Todos os Testes de Integração

```bash
pytest tests/integration/ai -v
```

### Executar Apenas Testes ONNX

```bash
pytest tests/integration/ai/test_onnx_embeddings_integration.py -v
```

### Executar com Cobertura de Código

```bash
pytest tests/integration/ai --cov=src.ai --cov-report=term-missing
```

## Tipos de Testes

### 1. Testes de Integração do Serviço de Embeddings

O arquivo `test_onnx_embeddings_integration.py` contém testes que:

1. Verificam a geração correta de embeddings
2. Validam o comportamento do cache
3. Medem o desempenho com diferentes tamanhos de lote
4. Testam o fallback para o backend de hashing

### Marcadores de Teste

- `@pytest.mark.integration`: Testes de integração
- `@pytest.mark.slow`: Testes que podem ser lentos devido a operações de E/S

## Solução de Problemas

### Erro ao Carregar o Modelo ONNX

Verifique se:
1. O modelo foi exportado corretamente
2. O caminho do modelo está acessível
3. As permissões do arquivo estão corretas

### Testes Muito Lentos

- Use a variável `SKIP_ONNX_TESTS=true` para pular testes ONNX
- Reduza o tamanho dos lotes nos testes modificando `batch_size`

## Contribuindo

Ao adicionar novos testes de integração:

1. Mantenha os testes independentes
2. Use fixtures para configuração comum
3. Adicione marcadores apropriados
4. Documente novos requisitos ou configurações

## Recursos Adicionais

- [Documentação do ONNX Runtime](https://onnxruntime.ai/)
- [Guia de Exportação de Modelos](docs/EMBEDDINGS_WITH_ONNX.md)
- [Plano de Testes de Automação](docs/TEST_AUTOMATION_PLAN.md)
