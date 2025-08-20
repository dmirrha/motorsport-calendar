import time
import json
from pathlib import Path
from datetime import datetime as _dt

import pytest
from icalendar import Calendar

from src.event_processor import EventProcessor
from src.ical_generator import ICalGenerator
from tests.utils.ical_snapshots import compare_or_write_snapshot


@pytest.mark.integration
def test_phase2_dedupe_order_consistency(freeze_datetime):
    """
    Integração Fase 2: deduplicação, consistência de timezone e ordenação.

    - Usa fixture estática (sem rede) para eventos do mesmo fim de semana
      contendo pares quase-duplicados (variação de nome/horário/local).
    - Valida deduplicação mantendo o melhor por prioridade de fonte.
    - Gera ICS e valida conteúdo + snapshot normalizado.
    - Execução < 30s.
    """
    # Determinismo de tempo (facilita validações com janelas relativas)
    freeze_datetime(dt=_dt(2025, 8, 1, 12, 0, 0))  # Sexta 01/08/2025

    # Carrega fixture
    fixture_path = Path("tests/fixtures/integration/scenario_dedupe_order.json")
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    raw_events = data["events"]

    t0 = time.monotonic()

    # Processa eventos (normaliza -> detecta categorias -> filtra fim de semana -> dedup -> valida/silent)
    processor = EventProcessor()
    processed = processor.process_events(raw_events)

    # 1) Deduplicação — esperamos reduzir de 4 para 3 (dois F1 TL1 -> 1)
    assert len(raw_events) == 4
    assert len(processed) == 3, f"Esperado 3 eventos após dedupe, obtido {len(processed)}: {[e.get('display_name') for e in processed]}"

    # Verifica que o melhor evento do par F1 TL1 foi mantido (source_priority mais alto)
    f1_practice = [
        e for e in processed
        if e.get("session_type") == "practice" and "Hungaroring" in (e.get("location") or "")
    ]
    assert len(f1_practice) == 1, f"Esperado 1 evento de practice (F1 TL1) em Hungaroring, obtido {len(f1_practice)}"
    best = f1_practice[0]
    # Melhor deve vir da fonte F1TV (priority 90) e manter horário 08:20 local
    assert best.get("source") == "F1TV"
    assert best.get("time") == "08:20"

    # 2) Geração de ICS + validação
    ical = ICalGenerator()
    ics_path = ical.generate_calendar(processed, output_filename="phase2_dedupe_order_consistency.ics")

    validation = ical.validate_calendar(ics_path)
    assert validation.get("valid") is True, f"ICS inválido: {validation}"
    assert validation.get("events_count", 0) == 3, "ICS deve conter 3 eventos"

    # 3) Snapshot normalizado e estável
    compare_or_write_snapshot(
        generated_path=ics_path,
        snapshot_path="tests/snapshots/phase2/phase2_dedupe_order_consistency.ics",
    )

    # 4) Timezone — garantir que todos os DTSTART possuem tz-aware
    cal = Calendar.from_ical(Path(ics_path).read_bytes())
    dtstarts = []
    for comp in cal.walk():
        if comp.name == "VEVENT":
            dt = comp.get("dtstart").dt
            assert hasattr(dt, "tzinfo") and dt.tzinfo is not None, "DTSTART deve ser timezone-aware"
            dtstarts.append(dt)

    # 5) Ordenação — esperado crescente por horário (ordenção determinística habilitada)
    assert dtstarts == sorted(dtstarts)

    # 6) Performance
    dt = time.monotonic() - t0
    assert dt < 30.0, f"Teste demorou {dt:.2f}s (esperado < 30s)"
