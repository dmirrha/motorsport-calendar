from datetime import datetime as _dt

import pytest

from src.event_processor import EventProcessor


@pytest.mark.unit
def test_process_events_normalize_and_filter_weekend(freeze_datetime):
    # Sexta de um fim de semana alvo
    freeze_datetime(dt=_dt(2025, 8, 1, 10, 0, 0))

    raw_events = [
        {
            "name": "  FórMuLa   1  - TL1  ",
            "date": "2025-08-01",
            "time": "08:00",
            "timezone": "America/Sao_Paulo",
            "category": "F1",
            "location": "Hungaroring",
            "country": "Hungria",
            "streaming_links": [
                {"name": "F1TV", "url": "https://f1tv.com"},
                "https://example.com/extra",
            ],
            "source": "test",
        },
        # Evento fora do fim de semana
        {
            "name": "NASCAR Cup - Practice",
            "date": "2025-08-05",
            "time": "12:00",
            "timezone": "America/Sao_Paulo",
            "category": "nascar",
            "location": "Daytona",
            "country": "USA",
            "streaming_links": [],
            "source": "test",
        },
    ]

    ep = EventProcessor()
    processed = ep.process_events(raw_events)

    # Apenas o primeiro deve permanecer (filtrado para o fim de semana)
    assert len(processed) == 1
    e = processed[0]

    # Normalizações básicas
    assert e["name"].startswith("formula 1")
    assert e["date"] == "2025-08-01"
    assert e["time"] == "08:00"
    assert e["datetime"].year == 2025 and e["datetime"].month == 8
    assert e["detected_category"] in {"formula 1", "f1", "single-seater"}
    assert isinstance(e["streaming_links"], list) and len(e["streaming_links"]) == 2


@pytest.mark.unit
def test_process_events_deduplicate_similar(freeze_datetime):
    freeze_datetime(dt=_dt(2025, 8, 1, 10, 0, 0))

    raw_events = [
        {
            "name": "Formula 1 – TL1",
            "date": "2025-08-01",
            "time": "08:00",
            "timezone": "America/Sao_Paulo",
            "category": "F1",
            "location": "Hungaroring",
            "country": "HU",
            "source": "tt",
        },
        {
            "name": "F1 TL1",
            "date": "2025-08-01",
            "time": "08:10",  # dentro da tolerância
            "timezone": "America/Sao_Paulo",
            "category": "formula 1",
            "location": "Hungaro ring",  # similar
            "country": "Hungria",
            "source": "tt",
        },
    ]

    ep = EventProcessor()
    processed = ep.process_events(raw_events)

    # Itens muito similares devem deduplicar
    assert len(processed) == 1
    assert processed[0]["detected_category"] in {"formula 1", "f1", "single-seater"}
