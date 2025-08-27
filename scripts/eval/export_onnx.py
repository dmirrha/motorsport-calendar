#!/usr/bin/env python3
"""
Exporta um modelo de embeddings para ONNX localmente, com opções de quantização e verificação.

Requisitos sugeridos:
  pip install --upgrade transformers optimum onnx onnxruntime
  # GPU NVIDIA (opcional):
  # pip install onnxruntime-gpu

Exemplos:
  # Exporta MiniLM para ONNX (feature-extraction), sem quantização
  python scripts/eval/export_onnx.py \
    --model-id sentence-transformers/all-MiniLM-L6-v2 \
    --outdir models/embeddings-onnx

  # Exporta com quantização dinâmica (int8 em camadas lineares)
  python scripts/eval/export_onnx.py \
    --model-id sentence-transformers/all-MiniLM-L6-v2 \
    --outdir models/embeddings-onnx \
    --quantize dynamic

  # Após exportar, rode benchmarks
  python scripts/eval/benchmarks.py \
    --task embeddings --engine both \
    --emb-count 5000 --batch-size 64 \
    --input docs/tests/scenarios/data/eval_dataset.csv \
    --outdir docs/tests/audit/benchmarks \
    --onnx-model models/embeddings-onnx/model.onnx \
    --providers mps,cpu
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="Exporta modelo para ONNX com opções de quantização")
    p.add_argument("--model-id", required=True, help="ID do modelo no Hugging Face Hub ou caminho local")
    p.add_argument("--outdir", required=True, help="Diretório de saída (será criado)")
    p.add_argument("--task", default="feature-extraction", help="Tarefa ONNX (default: feature-extraction)")
    p.add_argument("--opset", type=int, default=14, help="Versão do opset ONNX (default: 14)")
    p.add_argument("--quantize", choices=["none", "dynamic", "float16"], default="none",
                   help="Tipo de quantização a aplicar após export (default: none)")
    p.add_argument("--force", action="store_true", help="Sobrescreve diretório de saída se existir")
    p.add_argument("--verify", action="store_true", help="Tenta abrir a sessão ORT e listar I/O")
    return p.parse_args()


def ensure_outdir(outdir: Path, force: bool) -> None:
    if outdir.exists():
        if force:
            # Não remover conteúdo: apenas garantir existência
            outdir.mkdir(parents=True, exist_ok=True)
        else:
            # Se já existir e não forçar, seguimos mas avisamos
            print(f"[info] Diretório já existe: {outdir}")
    else:
        outdir.mkdir(parents=True, exist_ok=True)


def run_optimum_export(model_id: str, outdir: Path, task: str, opset: int) -> Path:
    """Invoca o exporter do Optimum via módulo CLI para evitar dependências de API instável.
    Retorna o caminho do arquivo model.onnx gerado (ou o encontrado)."""
    try:
        import optimum  # type: ignore  # noqa: F401
    except Exception as e:
        print("[erro] Optimum não encontrado. Instale com: pip install optimum")
        raise SystemExit(1) from e

    cmd = [
        sys.executable, "-m", "optimum.exporters.onnx",
        "--model", model_id,
        str(outdir),
        "--task", task,
        "--opset", str(opset),
    ]
    print("[exec] ", " ".join(cmd))
    res = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr, file=sys.stderr)
        raise SystemExit(res.returncode)

    # Heurística: procurar model.onnx no outdir
    candidate = outdir / "model.onnx"
    if not candidate.exists():
        # Alguns exports criam nomes diferentes, procurar o primeiro .onnx
        found = list(outdir.glob("*.onnx"))
        if not found:
            print("[erro] Arquivo .onnx não encontrado no diretório de saída")
            raise SystemExit(2)
        candidate = found[0]
    print(f"[ok] ONNX exportado: {candidate}")
    return candidate


def quantize_dynamic(onnx_path: Path) -> Path:
    try:
        from onnxruntime.quantization import quantize_dynamic, QuantType  # type: ignore
    except Exception as e:
        print("[erro] onnxruntime não oferece quantização dinâmica. Instale onnxruntime.")
        raise SystemExit(3) from e
    out_path = onnx_path.with_name(onnx_path.stem + ".qdyn.onnx")
    print(f"[quantize] dinâmica -> {out_path}")
    quantize_dynamic(model_input=str(onnx_path), model_output=str(out_path), weight_type=QuantType.QInt8)
    return out_path


def quantize_fp16(onnx_path: Path) -> Path:
    # Tenta usar conversor FP16
    try:
        from onnxconverter_common import float16  # type: ignore
        import onnx  # type: ignore
    except Exception as e:
        print("[erro] FP16 requer onnxconverter-common e onnx. Instale: pip install onnxconverter-common onnx")
        raise SystemExit(4) from e
    out_path = onnx_path.with_name(onnx_path.stem + ".fp16.onnx")
    print(f"[quantize] fp16 -> {out_path}")
    model = onnx.load(str(onnx_path))
    model_fp16 = float16.convert_float_to_float16(model)
    onnx.save(model_fp16, str(out_path))
    return out_path


def verify_session(onnx_path: Path) -> None:
    try:
        import onnxruntime as ort  # type: ignore
    except Exception as e:
        print("[warn] onnxruntime não instalado; verificação de sessão pulada.")
        return
    sess = ort.InferenceSession(str(onnx_path))
    inputs = [(i.name, i.type) for i in sess.get_inputs()]
    outputs = [(o.name, o.type) for o in sess.get_outputs()]
    print("[verify] inputs:", inputs)
    print("[verify] outputs:", outputs)


def main() -> None:
    a = parse_args()
    outdir = Path(a.outdir).resolve()
    ensure_outdir(outdir, force=a.force)

    onnx_path = run_optimum_export(a.model_id, outdir, a.task, a.opset)

    if a.quantize == "dynamic":
        onnx_path = quantize_dynamic(onnx_path)
    elif a.quantize == "float16":
        onnx_path = quantize_fp16(onnx_path)

    print(f"[ok] Arquivo final: {onnx_path}")

    if a.verify:
        verify_session(onnx_path)
        print("[ok] Verificação concluída")

    # Dica de uso no projeto
    rel = onnx_path.relative_to(Path.cwd()) if str(onnx_path).startswith(str(Path.cwd())) else onnx_path
    print("\nSugestão de configuração em config/config.json (ai.onnx):\n")
    print("{" )
    print("  \"ai\": {\n    \"onnx\": {\n      \"enabled\": true,\n      \"model_path\": \"%s\",\n      \"providers\": [\"cpu\"]\n    }\n  }" % rel)
    print("}")


if __name__ == "__main__":
    main()
