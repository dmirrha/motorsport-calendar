import pytest
from datetime import datetime
from unittest.mock import patch

from sources.tomada_tempo import TomadaTempoSource


@pytest.fixture()
def source():
    return TomadaTempoSource()


@pytest.mark.unit
def test_collect_events_uses_weekend_programming_first(source):
    target_date = datetime(2025, 8, 1)

    with patch.object(TomadaTempoSource, '_collect_from_weekend_programming', return_value=[{"name": "E1"}]) as wknd, \
         patch.object(TomadaTempoSource, 'filter_weekend_events', side_effect=lambda evs, rng: evs) as filt, \
         patch.object(TomadaTempoSource, 'normalize_event_data', side_effect=lambda e: e) as norm, \
         patch.object(TomadaTempoSource, 'validate_event_data', return_value=True) as valid:
        events = source.collect_events(target_date)

    assert events == [{"name": "E1"}]
    wknd.assert_called_once()
    # Como já há eventos, não deve chamar fallbacks; filter/normalize/validate são chamados
    assert filt.called
    assert norm.called
    assert valid.called


@pytest.mark.unit
def test_collect_events_fallbacks(source):
    target_date = datetime(2025, 8, 1)

    with patch.object(TomadaTempoSource, '_collect_from_weekend_programming', return_value=[]) as wknd, \
         patch.object(TomadaTempoSource, '_collect_from_calendar', return_value=[]) as cal, \
         patch.object(TomadaTempoSource, '_collect_from_categories', return_value=[{"name": "E2"}, {"name": "E3"}]) as cats, \
         patch.object(TomadaTempoSource, 'filter_weekend_events', side_effect=lambda evs, rng: evs) as filt, \
         patch.object(TomadaTempoSource, 'normalize_event_data', side_effect=lambda e: e) as norm, \
         patch.object(TomadaTempoSource, 'validate_event_data', return_value=True) as valid:
        events = source.collect_events(target_date)

    assert len(events) == 2
    wknd.assert_called_once()
    cal.assert_called_once()
    cats.assert_called_once()
    assert filt.called and norm.called and valid.called
