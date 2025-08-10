import pytest
from datetime import datetime
import pytz

from sources.base_source import BaseSource


class DummySource(BaseSource):
    def get_display_name(self) -> str:
        return "Dummy"

    def get_base_url(self) -> str:
        return "https://example.com"

    def collect_events(self, target_date=None):
        return []


@pytest.fixture()
def source():
    return DummySource()


def test_parse_date_time_with_time_and_tz(source):
    dt = source.parse_date_time("01/08/2025", "16:30", "America/Sao_Paulo")
    assert dt is not None
    assert dt.hour == 16 and dt.minute == 30
    assert getattr(dt.tzinfo, 'zone', None) == "America/Sao_Paulo"


def test_parse_date_time_date_only_default_midnight(source):
    dt = source.parse_date_time("01/08/2025", "", "America/Sao_Paulo")
    assert dt is not None
    assert dt.hour == 0 and dt.minute == 0


def test_parse_date_time_iso_date(source):
    dt = source.parse_date_time("2025-08-01", "", "America/Sao_Paulo")
    assert dt is not None
    assert dt.day == 1 and dt.month == 8 and dt.year == 2025


def test_parse_date_time_fallback_dateutil_dotted(source):
    # Usa fallback do dateutil com dayfirst=True
    dt = source.parse_date_time("01.08.2025", "", "America/Sao_Paulo")
    assert dt is not None
    assert dt.day == 1 and dt.month == 8 and dt.year == 2025


def test_parse_date_time_invalid_time_is_ignored(source):
    # Hora inválida não deve falhar o parse; retorna apenas a data
    dt = source.parse_date_time("01/08/2025", "25:00", "America/Sao_Paulo")
    assert dt is not None
    assert dt.hour == 0 and dt.minute == 0


def test_parse_date_time_invalid_timezone_returns_none(source):
    dt = source.parse_date_time("01/08/2025", "16:30", "America/Invalid_TZ")
    assert dt is None


def test_parse_date_time_invalid_date_returns_none(source):
    dt = source.parse_date_time("32/13/2025", "", "America/Sao_Paulo")
    assert dt is None


def test_validate_event_data_minimum_fields(source):
    assert source.validate_event_data({"name": "X", "date": "01/08/2025"}) is True


def test_validate_event_data_missing_fields(source):
    assert source.validate_event_data({"date": "01/08/2025"}) is False
    assert source.validate_event_data({"name": "X"}) is False
