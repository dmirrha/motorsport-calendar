#!/usr/bin/env python3
"""
Script para executar testes de integração do serviço de embeddings com ONNX.

Este script executa os testes de integração do serviço de embeddings, incluindo
os testes específicos para o backend ONNX. Ele também pode ser usado para gerar
relatórios de cobertura de código.

Uso:
  # Executar todos os testes de integração
  python scripts/test/run_embeddings_tests.py

  # Executar apenas testes específicos
  python scripts/test/run_embeddings_tests.py -k "test_onnx_embeddings_integration"

  # Gerar relatório de cobertura
  python scripts/test/run_embeddings_tests.py --cov

  # Executar com um modelo ONNX específico
  python scripts/test/run_embeddings_tests.py --onnx-model path/to/model.onnx
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para permitir imports relativos
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Verifica se o pytest está instalado
try:
    import pytest
except ImportError:
    print("Erro: pytest não está instalado. Instale com: pip install pytest pytest-cov")
    sys.exit(1)

def export_test_model(model_path: Path) -> bool:
    """Exporta um modelo de teste para ONNX se não existir."""
    if model_path.exists():
        print(f"Modelo ONNX já existe em {model_path}")
        return True
    
    print(f"Exportando modelo de teste para {model_path}...")
    try:
        from transformers import AutoTokenizer, AutoModel
        import torch
        
        model_id = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Baixando modelo {model_id}...")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModel.from_pretrained(model_id)
        
        dummy_input = tokenizer("Teste de exportação ONNX", return_tensors="pt")
        
        print(f"Exportando para ONNX...")
        torch.onnx.export(
            model,
            (dummy_input["input_ids"], dummy_input["attention_mask"]),
            model_path,
            input_names=["input_ids", "attention_mask"],
            output_names=["last_hidden_state", "pooler_output"],
            dynamic_axes={
                "input_ids": {0: "batch", 1: "sequence"},
                "attention_mask": {0: "batch", 1: "sequence"},
                "last_hidden_state": {0: "batch", 1: "sequence"},
            },
            opset_version=12,
        )
        
        print(f"Modelo exportado com sucesso para {model_path}")
        return True
    except Exception as e:
        print(f"Erro ao exportar modelo: {e}")
        return False

def run_tests(
    test_path: str,
    onnx_model: Path,
    cov: bool = False,
    cov_report: str = None,
    test_pattern: str = None,
    verbose: bool = False
) -> int:
    """Executa os testes de integração."""
    cmd = [
        sys.executable, "-m", "pytest",
        "-v" if verbose else "-v",
        "--durations=10",
    ]
    
    # Adiciona opções de cobertura
    if cov:
        cmd.extend([
            "--cov=src.ai",
            "--cov-report=term-missing",
        ])
        if cov_report:
            cmd.append(f"--cov-report={cov_report}")
    
    # Adiciona o padrão de teste, se especificado
    if test_pattern:
        cmd.extend(["-k", test_pattern])
    
    # Adiciona o caminho do teste
    cmd.append(test_path)
    
    # Define variáveis de ambiente para o teste
    env = os.environ.copy()
    env["ONNX_TEST_MODEL"] = str(onnx_model)
    
    # Executa os testes
    print(f"\nExecutando testes em {test_path}...")
    result = subprocess.run(cmd, env=env)
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description="Executa testes de integração do serviço de embeddings")
    parser.add_argument(
        "-k", "--test-pattern",
        help="Filtra testes por padrão de nome"
    )
    parser.add_argument(
        "--onnx-model",
        default="tests/data/onnx/model.onnx",
        help="Caminho para o modelo ONNX de teste"
    )
    parser.add_argument(
        "--cov", action="store_true",
        help="Habilita relatório de cobertura"
    )
    parser.add_argument(
        "--cov-report",
        help="Tipo de relatório de cobertura (term, html, xml, annotate)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Saída detalhada"
    )
    args = parser.parse_args()
    
    # Converte para Path
    onnx_model = Path(args.onnx_model).resolve()
    
    # Exporta o modelo de teste se necessário
    if not export_test_model(onnx_model):
        print("Aviso: Não foi possível exportar o modelo de teste. Testes ONNX serão pulados.")
        env_skip_onnx = True
    else:
        env_skip_onnx = False
    
    # Define variáveis de ambiente
    if env_skip_onnx:
        os.environ["SKIP_ONNX_TESTS"] = "true"
    
    # Caminho para os testes de integração
    test_path = str(ROOT / "tests/integration/ai/test_onnx_embeddings_integration.py")
    
    # Executa os testes
    return_code = run_tests(
        test_path=test_path,
        onnx_model=onnx_model,
        cov=args.cov,
        cov_report=args.cov_report,
        test_pattern=args.test_pattern,
        verbose=args.verbose
    )
    
    sys.exit(return_code)

if __name__ == "__main__":
    main()
