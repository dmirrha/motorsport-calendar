import io
import logging
from pathlib import Path as PathReal

import pytest

from src import logger as logger_module
from src.logger import Logger as AppLogger


class ListHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


class FakeConfigIcalOnly:
    """Config que NÃO expõe get('logging.*'), apenas get_ical_config()."""

    def __init__(self, base_logs_dir: str):
        self.base_logs_dir = base_logs_dir
        self._ical = {
            'logging': {
                'directory': base_logs_dir,
                'levels': {'console': 'INFO'},
                'rotation': {'max_size_mb': 2, 'backup_count': 4},
                'retention': {
                    'enabled': True,
                    'max_days': 1,
                    'max_logs_to_keep': 3,
                    'max_payloads_to_keep': 5,
                }
            }
        }

    def get_ical_config(self):
        return self._ical


@pytest.fixture(autouse=True)
def disable_cleanup(monkeypatch):
    monkeypatch.setattr(logger_module.Logger, "_cleanup_old_logs", lambda self: None)
    monkeypatch.setattr(logger_module.Logger, "_cleanup_rotated_logs", lambda self: None)


@pytest.fixture()
def cwd_tmp(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _attach_spy_handlers(app_logger: AppLogger):
    main = app_logger.get_logger('main')
    debug = app_logger.get_logger('debug')
    console = app_logger.get_logger('console')

    h_main, h_debug, h_console = ListHandler(), ListHandler(), ListHandler()
    main.addHandler(h_main)
    debug.addHandler(h_debug)
    console.addHandler(h_console)
    return h_main, h_debug, h_console


def test_helper_logging_methods_emit(cwd_tmp):
    cfg = FakeConfigIcalOnly(str(cwd_tmp / 'logs'))
    logger = AppLogger(config_manager=cfg)
    h_main, h_debug, h_console = _attach_spy_handlers(logger)

    logger.log_category_detection('F1', 0.91, 'detectorX')
    logger.log_duplicate_removed('GP Monaco', ['A', 'B'])
    logger.log_weekend_detection('2025-05-24', '2025-05-25', 5)
    logger.log_ical_generation('path/to/file.ics', 20)
    logger.log_source_start('tomada_tempo')
    logger.log_source_success('tomada_tempo', 10)
    logger.log_source_error('tomada_tempo', 'timeout')

    msgs_main = [r.getMessage() for r in h_main.records]
    msgs_debug = [r.getMessage() for r in h_debug.records]
    msgs_console = [r.getMessage() for r in h_console.records]

    # Espera que várias mensagens tenham sido emitidas
    # debug-only
    assert any('Category detected' in m for m in msgs_debug)
    assert any('Duplicate removed' in m for m in msgs_debug)
    # info/success
    assert any('Weekend detected' in m for m in msgs_main)
    assert any('iCal generated' in m for m in msgs_main)
    assert any('Starting data collection' in m for m in msgs_main)
    assert any('Collected' in m for m in msgs_main)
    # error
    assert any('tomada_tempo' in m and '❌' in m for m in msgs_console)


def test_get_log_config_falls_back_to_ical(cwd_tmp):
    cfg = FakeConfigIcalOnly(str(cwd_tmp / 'logs'))
    logger = AppLogger(config_manager=cfg)

    # Chaves com notação de ponto
    assert logger._get_log_config('directory') == str(cwd_tmp / 'logs')
    assert logger._get_log_config('levels.console') == 'INFO'
    assert logger._get_log_config('rotation.max_size_mb') == 2
    assert logger._get_log_config('rotation.backup_count') == 4
    assert logger._get_log_config('retention.max_logs_to_keep') == 3


def test_save_payload_handles_exception(monkeypatch, cwd_tmp):
    cfg = FakeConfigIcalOnly(str(cwd_tmp / 'logs'))
    logger = AppLogger(config_manager=cfg)

    # monkeypatch open para disparar erro
    def boom(*args, **kwargs):
        raise OSError('disk full')

    monkeypatch.setattr("builtins.open", boom)

    out = logger.save_payload('X', {'a': 1}, data_type='json')
    assert out == ""
