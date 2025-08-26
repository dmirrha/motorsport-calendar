#!/usr/bin/env python3
"""
Benchmarks (Issue #158): baseline vs IA

- Carrega um dataset CSV com eventos e ground-truth de categoria e grupos de duplicata
- Executa cenários para:
  * Categorização: baseline (heurístico) vs IA (CategoryDetector com contexto quando aplicável)
  * Deduplicação: baseline (sem detector) vs IA (com detector)
- Mede métricas e latência e exporta para CSV/Markdown

Execução exemplo:
  python scripts/eval/benchmarks.py \
    --task both --mode both \
    --input docs/tests/scenarios/data/eval_dataset.csv \
    --outdir docs/tests/audit/benchmarks \
    --seed 42
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Garante que o diretório do projeto (raiz) esteja no sys.path para importar "src.*"
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.event_processor import EventProcessor  # type: ignore
from src.category_detector import CategoryDetector  # type: ignore


@dataclass
class RunConfig:
    task: str  # category|dedup|both
    mode: str  # baseline|ia|both
    input_path: Path
    outdir: Path
    seed: int
    batch_size: int
    threads: int | None


def parse_args() -> RunConfig:
    p = argparse.ArgumentParser(description="Benchmarks baseline vs IA (Issue #158)")
    p.add_argument("--task", choices=["category", "dedup", "both"], default="both")
    p.add_argument("--mode", choices=["baseline", "ia", "both"], default="both")
    p.add_argument("--input", required=True, help="Caminho do CSV do dataset")
    p.add_argument("--outdir", default="docs/tests/audit/benchmarks", help="Diretório de saída")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--threads", type=int, default=None, help="Opcional")
    a = p.parse_args()
    return RunConfig(
        task=a.task,
        mode=a.mode,
        input_path=Path(a.input),
        outdir=Path(a.outdir),
        seed=a.seed,
        batch_size=a.batch_size,
        threads=a.threads,
    )


def ensure_outdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_dataset(csv_path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def build_normalized_events(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Usa EventProcessor apenas para normalização consistente
    ep = EventProcessor(config_manager=None, logger=None, ui_manager=None, category_detector=None)
    raw_events = []
    for r in rows:
        raw_events.append({
            "event_id": r.get("event_id", ""),
            "name": r.get("name", ""),
            "raw_category": r.get("raw_category", ""),
            "date": r.get("date"),
            "time": r.get("time"),
            "timezone": r.get("timezone") or "America/Sao_Paulo",
            "location": r.get("location", ""),
            "country": r.get("country", ""),
            "session_type": r.get("session_type", "race"),
            "source": r.get("source", "dataset"),
            "raw_data": {"category_context": {}}
        })
    normalized = ep._normalize_events(raw_events)  # type: ignore[attr-defined]
    return normalized


def display_to_code(display: str) -> str:
    # Converte formas canônicas de exibição para "códigos" usados no GT
    m = {
        "Formula 1": "F1",
        "Formula 2": "F2",
        "Formula 3": "F3",
        "Formula 4": "F4",
        "Formula E": "FormulaE",
        "Stock Car": "StockCar",
        "NASCAR": "NASCAR",
        "IndyCar": "IndyCar",
        "WEC": "WEC",
        "IMSA": "IMSA",
        "WRC": "WRC",
        "MotoGP": "MotoGP",
        "Moto2": "Moto2",
        "Moto3": "Moto3",
        "DTM": "DTM",
        "WTCR": "WTCR",
        "Super GT": "SuperGT",
        "SuperGT": "SuperGT",
        "GT World Challenge": "GTWorldChallenge",
        "Le Mans": "LeMans",
    }
    return m.get(display.strip(), display.strip())


def predict_categories_baseline(normalized_events: List[Dict[str, Any]]) -> Tuple[List[str], List[float]]:
    # Baseline: usar categoria bruta normalizada pelo EventProcessor e mapear para código
    ep = EventProcessor(config_manager=None, logger=None, ui_manager=None, category_detector=None)
    preds: List[str] = []
    confs: List[float] = []
    for e in normalized_events:
        raw_norm_display = ep._normalize_category(e.get("raw_category", ""))  # type: ignore[attr-defined]
        code = display_to_code(raw_norm_display)
        preds.append(code if code else "Unknown")
        confs.append(1.0 if code else 0.0)
    return preds, confs


def predict_categories_ia(normalized_events: List[Dict[str, Any]]) -> Tuple[List[str], List[float]]:
    det = CategoryDetector(config_manager=None, logger=None)
    t0 = time.perf_counter()
    results = det.detect_categories_batch(normalized_events)
    _ = time.perf_counter() - t0
    preds: List[str] = [r.get("category", "Unknown") for r in results]
    confs: List[float] = [float(r.get("confidence", 0.0)) for r in results]
    return preds, confs


def eval_category(rows: List[Dict[str, Any]], mode: str) -> Dict[str, Any]:
    events = build_normalized_events(rows)
    gt = [r.get("ground_truth_category", "").strip() for r in rows]

    results: List[Dict[str, Any]] = []

    def run_once(label: str, pred_func):
        t0 = time.perf_counter()
        preds, confs = pred_func(events)
        dt = time.perf_counter() - t0
        total = len(preds)
        correct = 0
        covered = 0
        for p, g in zip(preds, gt):
            if p and p != "Unknown":
                covered += 1
            if g and p == g:
                correct += 1
        acc = (correct / max(1, sum(1 for g in gt if g)))
        cov = (covered / max(1, len(gt)))
        avg_conf = (sum(confs) / len(confs)) if confs else 0.0
        results.append({
            "mode": label,
            "accuracy": round(acc, 4),
            "coverage": round(cov, 4),
            "avg_confidence": round(avg_conf, 4),
            "latency_ms_total": int(dt * 1000),
            "latency_ms_per_item": round((dt * 1000) / max(1, total), 3),
            "total_items": total,
        })

    if mode in ("baseline", "both"):
        run_once("baseline", predict_categories_baseline)
    if mode in ("ia", "both"):
        run_once("ia", predict_categories_ia)

    # Retorna apenas o último (ou agrega)
    return {"details": results}


def group_pairs_from_groups(groups: List[List[Dict[str, Any]]]) -> set[Tuple[str, str]]:
    pairs: set[Tuple[str, str]] = set()
    for grp in groups:
        ids = [str(e.get("event_id", "")) for e in grp if e.get("event_id")]
        ids = [i for i in ids if i]
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = ids[i], ids[j]
                if a <= b:
                    pairs.add((a, b))
                else:
                    pairs.add((b, a))
    return pairs


def truth_pairs_from_rows(rows: List[Dict[str, Any]]) -> set[Tuple[str, str]]:
    groups: Dict[str, List[str]] = {}
    for r in rows:
        gid = (r.get("duplicate_group") or "").strip()
        eid = (r.get("event_id") or "").strip()
        if not eid:
            continue
        if not gid:
            # Grupo único: não gera pares
            groups.setdefault(eid, [eid])
            continue
        groups.setdefault(gid, []).append(eid)
    # Constrói pares verdadeiros (mesmo grupo com >1)
    pairs: set[Tuple[str, str]] = set()
    for gid, ids in groups.items():
        ids = [i for i in ids if i]
        if len(ids) < 2:
            continue
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = ids[i], ids[j]
                if a <= b:
                    pairs.add((a, b))
                else:
                    pairs.add((b, a))
    return pairs


def predict_dedup_pairs_baseline(events: List[Dict[str, Any]]) -> set[Tuple[str, str]]:
    # Seta categoria detectada por baseline para ajudar na similaridade
    base_preds, _ = predict_categories_baseline(events)
    for e, c in zip(events, base_preds):
        e["detected_category"] = c
    ep = EventProcessor(config_manager=None, logger=None, ui_manager=None, category_detector=None)
    groups = ep._group_similar_events(events)  # type: ignore[attr-defined]
    return group_pairs_from_groups(groups)


def predict_dedup_pairs_ia(events: List[Dict[str, Any]]) -> set[Tuple[str, str]]:
    det = CategoryDetector(config_manager=None, logger=None)
    detected = det.detect_categories_batch(events)
    for e, d in zip(events, detected):
        e["detected_category"] = d.get("category", "Unknown")
    ep = EventProcessor(config_manager=None, logger=None, ui_manager=None, category_detector=det)
    groups = ep._group_similar_events(events)  # type: ignore[attr-defined]
    return group_pairs_from_groups(groups)


def compute_prf(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return round(precision, 4), round(recall, 4), round(f1, 4)


def eval_dedup(rows: List[Dict[str, Any]], mode: str) -> Dict[str, Any]:
    events = build_normalized_events(rows)
    truth = truth_pairs_from_rows(rows)
    results: List[Dict[str, Any]] = []

    def run_once(label: str, pred_func):
        # Precisamos trabalhar em uma cópia (pred_func muta events)
        import copy
        local_events = copy.deepcopy(events)
        t0 = time.perf_counter()
        predicted = pred_func(local_events)
        dt = time.perf_counter() - t0
        tp = len(predicted & truth)
        fp = len(predicted - truth)
        fn = len(truth - predicted)
        p, r, f1 = compute_prf(tp, fp, fn)
        total_pairs = len(predicted)
        results.append({
            "mode": label,
            "precision": p,
            "recall": r,
            "f1": f1,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "pred_pairs": total_pairs,
            "truth_pairs": len(truth),
            "latency_ms_total": int(dt * 1000),
            "latency_ms_per_item": round((dt * 1000) / max(1, len(events)), 3),
            "total_items": len(events),
        })

    if mode in ("baseline", "both"):
        run_once("baseline", predict_dedup_pairs_baseline)
    if mode in ("ia", "both"):
        run_once("ia", predict_dedup_pairs_ia)

    return {"details": results}


def append_metrics_csv(outdir: Path, dataset: Path, task: str, detail: Dict[str, Any]) -> None:
    ensure_outdir(outdir)
    csv_path = outdir / "metrics.csv"
    fieldnames = [
        "run_at", "dataset", "task", "mode",
        "accuracy", "coverage", "avg_confidence",
        "precision", "recall", "f1",
        "latency_ms_total", "latency_ms_per_item", "total_items",
        "tp", "fp", "fn", "pred_pairs", "truth_pairs",
    ]
    import datetime as _dt
    now = _dt.datetime.now().isoformat(timespec="seconds")

    write_header = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            w.writeheader()
        for d in detail.get("details", []):
            row = {
                "run_at": now,
                "dataset": str(dataset),
                "task": task,
                "mode": d.get("mode"),
                "accuracy": d.get("accuracy"),
                "coverage": d.get("coverage"),
                "avg_confidence": d.get("avg_confidence"),
                "precision": d.get("precision"),
                "recall": d.get("recall"),
                "f1": d.get("f1"),
                "latency_ms_total": d.get("latency_ms_total"),
                "latency_ms_per_item": d.get("latency_ms_per_item"),
                "total_items": d.get("total_items"),
                "tp": d.get("tp"),
                "fp": d.get("fp"),
                "fn": d.get("fn"),
                "pred_pairs": d.get("pred_pairs"),
                "truth_pairs": d.get("truth_pairs"),
            }
            w.writerow(row)


def write_report_md(outdir: Path, dataset: Path, cat_detail: Dict[str, Any] | None, du_detail: Dict[str, Any] | None) -> None:
    ensure_outdir(outdir)
    md = [
        "# Benchmarks — Baseline vs IA",
        "",
        f"Dataset: `{dataset}`",
        "",
    ]
    import datetime as _dt
    md.append(f"Executado em: {_dt.datetime.now().isoformat(timespec='seconds')}")
    md.append("")

    def section(title: str, details: Dict[str, Any]):
        md.append(f"## {title}")
        md.append("")
        md.append("modo | métrica 1 | métrica 2 | métrica 3 | total_itens | lat(ms)/item")
        md.append("--- | --- | --- | --- | ---: | ---:")
        for d in details.get("details", []):
            if title.startswith("Categorização"):
                md.append(
                    f"{d.get('mode')} | acc={d.get('accuracy')} | cov={d.get('coverage')} | conf={d.get('avg_confidence')} | "
                    f"{d.get('total_items')} | {d.get('latency_ms_per_item')}"
                )
            else:
                md.append(
                    f"{d.get('mode')} | P={d.get('precision')} | R={d.get('recall')} | F1={d.get('f1')} | "
                    f"{d.get('total_items')} | {d.get('latency_ms_per_item')}"
                )
        md.append("")

    if cat_detail:
        section("Categorização", cat_detail)
    if du_detail:
        section("Deduplicação", du_detail)

    (outdir / "report.md").write_text("\n".join(md), encoding="utf-8")


def main() -> None:
    cfg = parse_args()
    ensure_outdir(cfg.outdir)

    rows = read_dataset(cfg.input_path)

    cat_detail = None
    du_detail = None

    if cfg.task in ("category", "both"):
        run_mode = cfg.mode if cfg.mode != "both" else "both"
        cat_detail = eval_category(rows, run_mode)
        append_metrics_csv(cfg.outdir, cfg.input_path, "category", cat_detail)

    if cfg.task in ("dedup", "both"):
        run_mode = cfg.mode if cfg.mode != "both" else "both"
        du_detail = eval_dedup(rows, run_mode)
        append_metrics_csv(cfg.outdir, cfg.input_path, "dedup", du_detail)

    write_report_md(cfg.outdir, cfg.input_path, cat_detail, du_detail)
    print(f"✅ Concluído. Relatórios em: {cfg.outdir}")


if __name__ == "__main__":
    main()
