# Scripts de Teste

Este diretório contém scripts utilitários para executar testes de forma automatizada no projeto Motorsport Calendar.

## Estrutura de Arquivos

```
scripts/test/
├── __init__.py           # Inicialização do pacote
├── README.md             # Este arquivo
└── run_embeddings_tests.py  # Script para executar testes de integração do serviço de embeddings
```

## Scripts Disponíveis

### run_embeddings_tests.py

Executa os testes de integração do serviço de embeddings, incluindo suporte a ONNX.

#### Uso Básico

```bash
# Executar todos os testes de integração de embeddings
python scripts/test/run_embeddings_tests.py

# Executar com saída detalhada
python scripts/test/run_embeddings_tests.py -v

# Executar testes que correspondam a um padrão
python scripts/test/run_embeddings_tests.py -k "test_onnx_embeddings_generation"
```

#### Opções

- `-k, --test-pattern`: Filtra testes por padrão de nome
- `--onnx-model`: Caminho para o modelo ONNX de teste (padrão: `tests/data/onnx/model.onnx`)
- `--cov`: Habilita relatório de cobertura
- `--cov-report`: Tipo de relatório de cobertura (term, html, xml, annotate)
- `-v, --verbose`: Saída detalhada

#### Exemplos

```bash
# Gerar relatório de cobertura HTML
python scripts/test/run_embeddings_tests.py --cov --cov-report=html

# Usar um modelo ONNX personalizado
python scripts/test/run_embeddings_tests.py --onnx-model /caminho/para/modelo.onnx
```

## Requisitos

- Python 3.8+
- Dependências de desenvolvimento listadas em `requirements-dev.txt`
- Para testes ONNX:
  - `onnx`
  - `onnxruntime`
  - `optimum`
  - `onnxconverter-common`
  - `transformers`

## Como Adicionar Novos Scripts

1. Crie um novo arquivo `.py` no diretório `scripts/test/`
2. Adicione uma seção neste README.md explicando a finalidade do script
3. Certifique-se de que o script tenha uma função `main()` e seja executável
4. Adicione tratamento de erros adequado e mensagens de ajuda

## Boas Práticas

- Use `argparse` para opções de linha de comando
- Documente todas as opções e parâmetros
- Inclua exemplos de uso
- Trate erros de forma adequada
- Mantenha os scripts independentes e reutilizáveis
