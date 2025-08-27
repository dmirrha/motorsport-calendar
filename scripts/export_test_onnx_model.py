"""
Script para exportar um modelo ONNX de teste para uso nos testes de integração.

Este script exporta um modelo pequeno do Hugging Face para o formato ONNX,
que será usado nos testes de integração do serviço de embeddings.
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para permitir imports relativos
sys.path.insert(0, str(Path(__file__).parent.parent))

def export_test_model():
    """Exporta um modelo de teste para ONNX."""
    from transformers import AutoTokenizer, AutoModel
    import torch
    from onnxruntime.quantization import quantize_dynamic, QuantType
    
    # Configurações
    model_id = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    output_dir = Path("tests/data/onnx")
    output_dir.mkdir(parents=True, exist_ok=True)
    onnx_path = output_dir / "model.onnx"
    
    print(f"Exportando modelo {model_id} para ONNX...")
    
    # Carrega o modelo e o tokenizador
    print("Carregando modelo e tokenizador...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModel.from_pretrained(model_id)
    
    # Configuração para exportação
    dummy_input = tokenizer("Teste de exportação ONNX", return_tensors="pt")
    
    # Exporta para ONNX
    print(f"Exportando para {onnx_path}...")
    torch.onnx.export(
        model,
        (dummy_input["input_ids"], dummy_input["attention_mask"]),
        onnx_path,
        input_names=["input_ids", "attention_mask"],
        output_names=["last_hidden_state", "pooler_output"],
        dynamic_axes={
            "input_ids": {0: "batch", 1: "sequence"},
            "attention_mask": {0: "batch", 1: "sequence"},
            "last_hidden_state": {0: "batch", 1: "sequence"},
        },
        opset_version=12,
    )
    
    print(f"Modelo exportado com sucesso para {onnx_path}")
    print(f"Tamanho do arquivo: {onnx_path.stat().st_size / (1024*1024):.2f} MB")

if __name__ == "__main__":
    export_test_model()
