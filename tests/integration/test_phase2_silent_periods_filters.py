"""
Phase 2 Integration — Silent Periods & Filters
Objetivo: validar períodos silenciosos e filtros aplicados na geração/seleção de eventos.
Marcadores: integration
"""

import pytest
from datetime import datetime
from src.silent_period import SilentPeriod

pytestmark = pytest.mark.integration


def test_silent_period_basic_in_range_allows_filtering():
    # Período silencioso ativo: segunda-feira, 09:00–17:00
    period = SilentPeriod({
        "enabled": True,
        "name": "Business Hours",
        "start_time": "09:00",
        "end_time": "17:00",
        "days_of_week": ["monday"],
    })

    # Evento numa segunda às 10:00 deve entrar no período
    dt = datetime(2025, 8, 18, 10, 0, 0)  # Monday
    assert period.is_event_in_silent_period(dt) is True


def test_silent_period_cross_midnight_cases():
    # Período atravessando meia-noite: 22:00–06:00 em sexta e sábado
    period = SilentPeriod({
        "enabled": True,
        "name": "Night Quiet",
        "start_time": "22:00",
        "end_time": "06:00",
        "days_of_week": ["friday", "saturday"],
    })

    # Sexta 23:30 — dentro
    dt_fri_late = datetime(2025, 8, 15, 23, 30, 0)  # Friday
    assert period.is_event_in_silent_period(dt_fri_late) is True

    # Sábado 05:30 — dentro (continua após meia-noite)
    dt_sat_early = datetime(2025, 8, 16, 5, 30, 0)  # Saturday
    assert period.is_event_in_silent_period(dt_sat_early) is True

    # Sábado 07:00 — fora
    dt_sat_morning = datetime(2025, 8, 16, 7, 0, 0)
    assert period.is_event_in_silent_period(dt_sat_morning) is False
