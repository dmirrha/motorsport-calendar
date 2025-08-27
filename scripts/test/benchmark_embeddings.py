#!/usr/bin/env python3
"""Benchmark para o serviço de embeddings.

Testa o desempenho dos backends de hashing e ONNX com diferentes tamanhos de lote.
"""
import argparse
import json
import time
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from tqdm import tqdm

from src.ai.embeddings_service import EmbeddingsService, EmbeddingsConfig


def generate_test_texts(n: int = 100) -> List[str]:
    """Gera textos de exemplo para teste."""
    events = ["F1", "MotoGP", "Stock Car", "Fórmula E", "WEC"]
    locations = ["Brasil", "Argentina", "EUA", "Espanha", "Japão"]
    return [f"{e} {l} {i}" for i, (e, l) in enumerate(zip(events * (n//5 + 1), locations * (n//5 + 1)))][:n]


def run_benchmark(config: Dict[str, Any], texts: List[str], rounds: int = 3) -> Dict[str, Any]:
    """Executa o benchmark com a configuração fornecida."""
    svc = EmbeddingsService(EmbeddingsConfig(**config))
    times = []
    
    # Aquecimento
    _ = svc.embed_texts(texts[:10])
    
    # Execução
    for _ in tqdm(range(rounds), desc=f"Benchmark {config['backend']} (batch={config['batch_size']})"):
        start = time.time()
        _ = svc.embed_texts(texts)
        times.append(time.time() - start)
    
    return {
        "config": config,
        "avg_time": np.mean(times),
        "std_time": np.std(times),
        "texts_per_second": len(texts) / np.mean(times),
        "metrics": {k: v for k, v in svc.metrics.items() if not k.startswith('_')}
    }


def main():
    parser = argparse.ArgumentParser(description='Benchmark do serviço de embeddings')
    parser.add_argument('--num-texts', type=int, default=100, help='Número de textos para teste')
    parser.add_argument('--batch-sizes', type=str, default='1,8,32', help='Tamanhos de lote (separados por vírgula)')
    parser.add_argument('--output', type=str, default='benchmark_results.json', help='Arquivo de saída')
    args = parser.parse_args()
    
    # Configurações
    texts = generate_test_texts(args.num_texts)
    batch_sizes = list(map(int, args.batch_sizes.split(',')))
    results = []
    
    # Testa backends
    for backend in ['hashing', 'onnx']:
        for batch_size in batch_sizes:
            config = {
                'backend': backend,
                'batch_size': batch_size,
                'dim': 128 if backend == 'hashing' else 384,
                'onnx_enabled': backend == 'onnx',
                'onnx_model_path': 'tests/data/onnx/model.onnx',
                'onnx_providers': ['CPUExecutionProvider']
            }
            try:
                result = run_benchmark(config, texts)
                results.append(result)
                print(f"{backend.upper()}, batch={batch_size}: {result['texts_per_second']:.1f} textos/seg")
            except Exception as e:
                print(f"Erro ao executar {backend} (batch={batch_size}): {e}")
    
    # Salva resultados
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResultados salvos em {args.output}")


if __name__ == '__main__':
    main()
