import pytest
from datetime import datetime

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


def test_validate_event_data_true_minimal(source):
    assert source.validate_event_data({"name": "X", "date": "01/08/2025"}) is True


def test_validate_event_data_false_missing_name(source):
    assert source.validate_event_data({"date": "01/08/2025"}) is False


def test_validate_event_data_false_missing_date(source):
    assert source.validate_event_data({"name": "X"}) is False


def test_validate_event_data_false_empty_name(source):
    assert source.validate_event_data({"name": "", "date": "01/08/2025"}) is False


def test_validate_event_data_false_none_date(source):
    assert source.validate_event_data({"name": "Race", "date": None}) is False


def test_validate_event_data_true_with_datetime(source):
    dt = datetime(2025, 8, 1, 12, 0, 0)
    assert source.validate_event_data({"name": "Race", "date": dt}) is True


def test_validate_event_data_logs_missing_field(monkeypatch):
    messages = []

    class Logger:
        def debug(self, msg):
            messages.append(msg)

    src = DummySource(logger=Logger())
    result = src.validate_event_data({"date": "01/08/2025"})

    assert result is False
    assert any("missing required field 'name'" in m for m in messages)
