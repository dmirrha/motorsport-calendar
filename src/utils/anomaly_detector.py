from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime


@dataclass
class AnomalyConfig:
    enabled: bool = False
    min_hour: int = 6
    max_hour: int = 23
    examples_per_type: int = 3


@dataclass
class AnomalyInstance:
    type: str
    message: str
    event_id: str
    sample: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyReport:
    counts: Dict[str, int] = field(default_factory=dict)
    examples: Dict[str, List[AnomalyInstance]] = field(default_factory=dict)

    def add(self, anomaly: AnomalyInstance, examples_per_type: int) -> None:
        t = anomaly.type
        self.counts[t] = self.counts.get(t, 0) + 1
        bucket = self.examples.setdefault(t, [])
        if len(bucket) < examples_per_type:
            bucket.append(anomaly)

    def is_empty(self) -> bool:
        return sum(self.counts.values()) == 0


class AnomalyDetector:
    """
    Detector de anomalias leve e opcional.
    Regras implementadas (warning):
      - outside_weekend: evento fora do intervalo alvo.
      - improbable_hour: horário < min_hour ou > max_hour.
      - category_inconsistency: categoria bruta ausente e detecção desconhecida/baixa confiança.
      - location_missing: local vazio.
    """

    def __init__(self, cfg: Optional[AnomalyConfig] = None):
        self.cfg = cfg or AnomalyConfig()

    def evaluate(
        self,
        events: List[Dict[str, Any]],
        *,
        target_weekend: Optional[Tuple[datetime, datetime]] = None,
    ) -> AnomalyReport:
        report = AnomalyReport()
        if not self.cfg.enabled or not events:
            return report

        for ev in events:
            try:
                self._check_outside_weekend(ev, target_weekend, report)
                self._check_improbable_hour(ev, report)
                self._check_category(ev, report)
                self._check_location(ev, report)
            except Exception:
                # Nunca quebra o pipeline por erro de detecção
                continue
        return report

    # Regras
    def _check_outside_weekend(
        self,
        ev: Dict[str, Any],
        target_weekend: Optional[Tuple[datetime, datetime]],
        report: AnomalyReport,
    ) -> None:
        if not target_weekend:
            return
        dt = ev.get("datetime")
        if not isinstance(dt, datetime):
            return
        start, end = target_weekend
        if not (start <= dt <= end):
            report.add(
                AnomalyInstance(
                    type="outside_weekend",
                    message="Evento fora do fim de semana alvo",
                    event_id=str(ev.get("event_id", "")),
                    sample={
                        "name": ev.get("display_name") or ev.get("name"),
                        "datetime": str(dt),
                    },
                ),
                self.cfg.examples_per_type,
            )

    def _check_improbable_hour(self, ev: Dict[str, Any], report: AnomalyReport) -> None:
        dt = ev.get("datetime")
        if not isinstance(dt, datetime):
            return
        h = dt.hour
        if h < int(self.cfg.min_hour) or h > int(self.cfg.max_hour):
            report.add(
                AnomalyInstance(
                    type="improbable_hour",
                    message=f"Horário improvável: {h:02d}h",
                    event_id=str(ev.get("event_id", "")),
                    sample={
                        "name": ev.get("display_name") or ev.get("name"),
                        "datetime": str(dt),
                    },
                ),
                self.cfg.examples_per_type,
            )

    def _check_category(self, ev: Dict[str, Any], report: AnomalyReport) -> None:
        raw_cat = (ev.get("raw_category") or ev.get("category") or "").strip()
        detected = (ev.get("detected_category") or "").strip()
        conf = float(ev.get("category_confidence", 0.0) or 0.0)
        if not raw_cat and (not detected or conf < 0.3):
            report.add(
                AnomalyInstance(
                    type="category_inconsistency",
                    message="Categoria ausente/baixa confiança",
                    event_id=str(ev.get("event_id", "")),
                    sample={
                        "raw_category": raw_cat,
                        "detected_category": detected,
                        "confidence": conf,
                    },
                ),
                self.cfg.examples_per_type,
            )

    def _check_location(self, ev: Dict[str, Any], report: AnomalyReport) -> None:
        loc = (ev.get("location") or "").strip()
        if not loc:
            report.add(
                AnomalyInstance(
                    type="location_missing",
                    message="Local ausente",
                    event_id=str(ev.get("event_id", "")),
                    sample={
                        "name": ev.get("display_name") or ev.get("name"),
                    },
                ),
                self.cfg.examples_per_type,
            )

    # Utilitário de logging
    def log_summary(self, report: AnomalyReport, logger: Any = None) -> None:
        if report.is_empty():
            return
        lines = ["\u26a0\ufe0f Anomalias detectadas:"]
        for t, count in report.counts.items():
            lines.append(f"- {t}: {count}")
            for ex in report.examples.get(t, []):
                lines.append(f"  * {ex.message} — {ex.sample}")
        msg = "\n".join(lines)
        if logger and hasattr(logger, "log_warning"):
            logger.log_warning(msg)
        else:
            print(msg)
