import os
import glob
import shutil
from datetime import datetime

import pytest
import pytz
from icalendar import Calendar, Event

from src.ical_generator import ICalGenerator


class LoggerStub:
    def __init__(self):
        self.debugs = []
        self.errors = []
        self.steps = []
        self.success = []
        self.warnings = []

    def debug(self, msg):
        self.debugs.append(str(msg))

    def log_error(self, msg):
        self.errors.append(str(msg))

    def log_step(self, msg):
        self.steps.append(str(msg))

    def log_success(self, msg):
        self.success.append(str(msg))

    def log_warning(self, msg):
        self.warnings.append(str(msg))


class ConfigStub:
    def __init__(self, data):
        self.data = data

    def get_ical_config(self):
        return self.data


@pytest.mark.unit
def test__create_ical_event_exception_path(monkeypatch):
    logger = LoggerStub()
    gen = ICalGenerator(logger=logger)

    # Garante datetime válido
    tz = pytz.timezone("America/Sao_Paulo")
    event_dt = tz.localize(datetime(2025, 8, 10, 15, 0, 0))
    payload = {
        "event_id": "x",
        "datetime": event_dt,
        "name": "X",
        "detected_category": "F1",
        "session_type": "race",
    }

    # Força exceção dentro do bloco try
    monkeypatch.setattr(ICalGenerator, "_create_event_description", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))

    out = gen._create_ical_event(payload)
    assert out is None
    assert any("Failed to create iCal event" in d for d in logger.debugs)


@pytest.mark.unit
def test_generate_calendar_write_failure_returns_empty(monkeypatch, tmp_path):
    logger = LoggerStub()
    gen = ICalGenerator(logger=logger)
    gen.output_directory = str(tmp_path)

    tz = pytz.timezone("America/Sao_Paulo")
    event_dt = tz.localize(datetime(2025, 8, 10, 15, 0, 0))
    events = [{
        "event_id": "evt-1",
        "datetime": event_dt,
        "name": "Race",
        "detected_category": "F1",
        "session_type": "race",
    }]

    # Falha ao abrir arquivo para escrita
    def broken_open(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr("builtins.open", broken_open)

    out = gen.generate_calendar(events, output_filename="broken.ics")
    assert out == ""
    assert any("Failed to write iCal file" in e for e in logger.errors)


@pytest.mark.unit
def test_archive_old_ical_files_no_output_dir(tmp_path):
    # Sem diretório => early return
    logger = LoggerStub()
    gen = ICalGenerator(logger=logger)
    gen.output_directory = str(tmp_path / "nonexistent")
    # Não deve lançar erro
    gen._archive_old_ical_files()


@pytest.mark.unit
def test_archive_old_ical_files_logs_on_move_error(monkeypatch, tmp_path):
    logger = LoggerStub()
    gen = ICalGenerator(logger=logger)
    gen.output_directory = str(tmp_path)
    os.makedirs(gen.output_directory, exist_ok=True)

    # Cria dois .ics
    for i in range(2):
        p = tmp_path / f"old{i}.ics"
        p.write_text("BEGIN:VCALENDAR\nEND:VCALENDAR\n")

    def broken_move(src, dst):
        raise OSError("cannot move")

    monkeypatch.setattr(shutil, "move", broken_move)

    gen._archive_old_ical_files()
    # Deve logar falha
    assert any("Failed to archive" in d for d in logger.debugs)


@pytest.mark.unit
def test_generate_multiple_calendars_and_grouping(tmp_path, monkeypatch):
    logger = LoggerStub()
    gen = ICalGenerator(logger=logger)
    gen.output_directory = str(tmp_path)

    # Evita arquivamento para simplificar
    monkeypatch.setattr(ICalGenerator, "_archive_old_ical_files", lambda self: None)

    tz = pytz.timezone("America/Sao_Paulo")
    dt1 = tz.localize(datetime(2025, 8, 10, 9, 0, 0))
    dt2 = tz.localize(datetime(2025, 8, 10, 11, 0, 0))
    dt3 = tz.localize(datetime(2025, 8, 11, 13, 0, 0))

    events = [
        {"event_id": "a", "datetime": dt1, "date": "2025-08-10", "name": "A", "detected_category": "F1", "session_type": "race", "source_display_name": "TT"},
        {"event_id": "b", "datetime": dt2, "date": "2025-08-10", "name": "B", "detected_category": "MotoGP", "session_type": "qualifying", "source_display_name": "TT"},
        {"event_id": "c", "datetime": dt3, "date": "2025-08-11", "name": "C", "detected_category": "WEC", "session_type": "practice", "source_display_name": "Oficial"},
    ]

    # category
    files_cat = gen.generate_multiple_calendars(events, group_by="category")
    assert len(files_cat) >= 3

    # date
    files_date = gen.generate_multiple_calendars(events, group_by="date")
    assert len(files_date) >= 2

    # source
    files_src = gen.generate_multiple_calendars(events, group_by="source")
    assert len(files_src) >= 2

    # fallback branch (else)
    files_all = gen.generate_multiple_calendars(events, group_by="unknown")
    assert len(files_all) == 1


@pytest.mark.unit
def test_validate_calendar_missing_required_properties_logs_invalid(tmp_path):
    logger = LoggerStub()
    gen = ICalGenerator(logger=logger)

    cal = Calendar()
    cal.add('prodid', '-//Test//EN')
    cal.add('version', '2.0')

    # VEVENT sem 'summary' para falhar validação sem exceção
    ve = Event()
    ve.add('uid', 'x@test')
    tz = pytz.timezone("America/Sao_Paulo")
    ve.add('dtstart', tz.localize(datetime(2025, 8, 10, 10, 0, 0)))
    cal.add_component(ve)

    out = tmp_path / "invalid.ics"
    with open(out, 'wb') as f:
        f.write(cal.to_ical())

    res = gen.validate_calendar(str(out))
    assert res["valid"] is False
    assert any("validation failed" in d.lower() for d in logger.debugs)


@pytest.mark.unit
def test__load_config_applies_values_and_reminders():
    cfg = ConfigStub({
        'calendar_name': 'MyCal',
        'calendar_description': 'Desc',
        'timezone': 'UTC',
        'default_duration_minutes': 45,
        'reminders': [{ 'minutes': 10 }, { 'minutes': 5 }],
        'include_streaming_links': False,
        'include_source_info': False,
        'output': { 'directory': 'outdir', 'filename_template': 'ical_{date}.ics' },
    })
    gen = ICalGenerator(config_manager=cfg)

    assert gen.calendar_name == 'MyCal'
    assert gen.calendar_description == 'Desc'
    assert gen.timezone == 'UTC'
    assert gen.default_duration_minutes == 45
    assert gen.reminder_minutes == [10, 5]
    assert gen.include_streaming_links is False
    assert gen.include_source_info is False
    assert gen.output_directory == 'outdir'
    assert gen.filename_template == 'ical_{date}.ics'


@pytest.mark.unit
def test_generate_calendar_with_no_logger_executes_log_summary_early_return(tmp_path):
    # Sem logger: cobre ramo early-return em _log_generation_summary
    gen = ICalGenerator()  # logger None
    gen.output_directory = str(tmp_path)

    tz = pytz.timezone("America/Sao_Paulo")
    event_dt = tz.localize(datetime(2025, 8, 10, 15, 0, 0))
    events = [{
        "event_id": "evt0",
        "datetime": event_dt,
        "name": "R",
        "detected_category": "F1",
        "session_type": "race",
    }]

    out = gen.generate_calendar(events, output_filename="nologue.ics")
    assert os.path.exists(out)
