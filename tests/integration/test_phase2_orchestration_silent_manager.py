"""
Phase 2 Integration — Orquestração: SilentPeriodManager + ConfigManager
Objetivo: validar filtragem de eventos ao integrar configuração mínima com o gerenciador de períodos silenciosos.
Marcadores: integration
"""

import pytest
from datetime import datetime
from src.config_manager import ConfigManager
from src.silent_period import SilentPeriodManager

pytestmark = pytest.mark.integration


def test_orchestration_silent_manager_filters_and_metadata(tmp_path):
    # Configuração mínima em memória via ConfigManager
    cm = ConfigManager(config_path=None)

    # Período silencioso: 22:00–06:00 em sexta/sábado
    cm.set(
        "general.silent_periods",
        [
            {
                "enabled": True,
                "name": "Night Quiet",
                "start_time": "22:00",
                "end_time": "06:00",
                "days_of_week": ["friday", "saturday"],
            }
        ],
    )

    spm = SilentPeriodManager(config_manager=cm)

    # Eventos: antes, durante e após o período
    events = [
        {"name": "FP1", "datetime": datetime(2025, 8, 15, 21, 0, 0)},  # sexta 21:00 — fora
        {"name": "Quali", "datetime": datetime(2025, 8, 15, 23, 0, 0)},  # sexta 23:00 — dentro
        {"name": "Warmup", "datetime": datetime(2025, 8, 16, 5, 30, 0)},  # sábado 05:30 — dentro
        {"name": "Race", "datetime": datetime(2025, 8, 16, 7, 0, 0)},  # sábado 07:00 — fora
    ]

    allowed, filtered = spm.filter_events(events)

    # Dois eventos devem ser filtrados (sexta 23:00 e sábado 05:30)
    assert len(filtered) == 2
    assert {e["name"] for e in filtered} == {"Quali", "Warmup"}

    # Metadados de filtragem preservados
    for e in filtered:
        assert e.get("silent_period") == "Night Quiet"
        assert "filter_reason" in e and "Night Quiet" in e["filter_reason"]

    # Eventos remanescentes (fora do período)
    assert len(allowed) == 2
    assert {e["name"] for e in allowed} == {"FP1", "Race"}

    # Estatísticas mínimas
    stats = spm.get_statistics()
    assert stats["events_checked"] == 4
    assert stats["events_filtered"] == 2
