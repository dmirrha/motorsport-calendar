from datetime import datetime

import pytest

from silent_period import SilentPeriodManager


class DummyLogger:
    def __init__(self):
        self.infos = []
        self.debugs = []

    def info(self, msg):
        self.infos.append(str(msg))

    def debug(self, msg):
        self.debugs.append(str(msg))


@pytest.mark.unit
def test_log_filtering_summary_no_events():
    logger = DummyLogger()
    mgr = SilentPeriodManager(config_manager=None, logger=logger)

    mgr.log_filtering_summary([])

    # Deve registrar debug informando ausência de eventos filtrados
    assert any("No events filtered" in m for m in logger.debugs)


@pytest.mark.unit
def test_log_filtering_summary_with_events_groups_and_details():
    logger = DummyLogger()
    mgr = SilentPeriodManager(config_manager=None, logger=logger)

    events = [
        {
            "name": "P1",
            "datetime": datetime(2025, 8, 4, 23, 30),  # Monday 23:30
            "silent_period": "Night",
        },
        {
            "name": "P2",
            "datetime": datetime(2025, 8, 4, 23, 45),
            "silent_period": "Night",
        },
    ]

    mgr.log_filtering_summary(events)

    # Cabeçalho de resumo
    assert any("Silent periods filtered 2 events" in m for m in logger.infos)

    # Agrupamento por período
    assert any("Night: 2 events" in m for m in logger.infos)

    # Linhas detalhadas por evento em debug
    assert any("- P1 at 2025-08-04 23:30" in m for m in logger.debugs)
    assert any("- P2 at 2025-08-04 23:45" in m for m in logger.debugs)
