from datetime import datetime
from typing import Optional

import pytest
import pytz
from hypothesis import given, strategies as st

from sources.base_source import BaseSource
from src.event_processor import EventProcessor


class DummySource(BaseSource):
    def get_display_name(self) -> str:
        return "Dummy"

    def get_base_url(self) -> str:
        return "http://example.com"

    def collect_events(self, target_date: Optional[datetime] = None):  # pragma: no cover - not used here
        return []


tz_name = "America/Sao_Paulo"

def _mk_date_str(y: int, m: int, d: int, fmt: str) -> str:
    if fmt == "br-slash":
        return f"{d:02d}/{m:02d}/{y:04d}"
    elif fmt == "iso":
        return f"{y:04d}-{m:02d}-{d:02d}"
    else:
        return f"{d:02d}-{m:02d}-{y:04d}"


@pytest.mark.property
@given(
    year=st.integers(min_value=2022, max_value=2026),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28),  # mantém simples para evitar datas inválidas
    hour=st.integers(min_value=0, max_value=23),
    minute=st.integers(min_value=0, max_value=59),
    include_time=st.booleans(),
    fmt=st.sampled_from(["br-slash", "iso", "br-dash"]),
)
def test_parse_datetime_roundtrip(year, month, day, hour, minute, include_time, fmt):
    src = DummySource(config_manager=None, logger=None, ui_manager=None)
    ep = EventProcessor(config_manager=None, logger=None, ui_manager=None)

    date_str = _mk_date_str(year, month, day, fmt)
    time_str = f"{hour:02d}:{minute:02d}" if include_time else ""

    dt = src.parse_date_time(date_str, time_str, timezone_str=tz_name)
    assert dt is not None, "parse_date_time deve retornar datetime válido"
    assert dt.tzinfo is not None, "datetime deve ser timezone-aware"

    # Roundtrip via EventProcessor._compute_datetime
    rt_date = dt.strftime("%Y-%m-%d")
    rt_time = dt.strftime("%H:%M")

    dt2 = ep._compute_datetime(rt_date, rt_time, tz_name)
    assert dt2 is not None

    # Igualdade até minuto (ambos têm resolução de minuto)
    dt_norm = dt.replace(second=0, microsecond=0)
    assert dt2 == dt_norm
