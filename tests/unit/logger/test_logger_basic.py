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


class FakeConfig:
    """Config fake que cobre ambos os caminhos de _get_log_config.
    - get(key) retorna valores para 'logging.'
    - get_ical_config() retorna estrutura aninhada quando necessário
    """

    def __init__(self, base_logs_dir: str):
        self.base_logs_dir = base_logs_dir
        self._map = {
            'logging.directory': base_logs_dir,
            'logging.levels.console': 'DEBUG',
            'logging.rotation.max_size_mb': 1,  # 1 MB
            'logging.rotation.backup_count': 2,
            # Evita chamar limpeza em _setup_directories
            'logging.retention.enabled': False,
        }
        self._ical = {
            'logging': {
                'retention': {
                    'enabled': True,
                    'max_days': 1,
                    'max_logs_to_keep': 3,
                    'max_payloads_to_keep': 5,
                }
            }
        }

    def get(self, key: str, default=None):
        return self._map.get(key, default)

    def get_ical_config(self):
        return self._ical


@pytest.fixture(autouse=True)
def disable_cleanup(monkeypatch):
    """Desabilita limpezas globais para não afetar logs reais do projeto."""
    monkeypatch.setattr(logger_module.Logger, "_cleanup_old_logs", lambda self: None)
    monkeypatch.setattr(logger_module.Logger, "_cleanup_rotated_logs", lambda self: None)


@pytest.fixture()
def cwd_tmp(monkeypatch, tmp_path):
    # Isola CWD para que Path("logs") escreva dentro do tmp_path
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


def test_get_logger_unknown_returns_main(cwd_tmp):
    cfg = FakeConfig(str(cwd_tmp / 'logs'))
    logger = AppLogger(config_manager=cfg)

    main_logger = logger.get_logger('main')
    unknown_logger = logger.get_logger('does_not_exist')

    assert unknown_logger is main_logger


def test_console_level_update_affects_logger_and_handler(cwd_tmp):
    cfg = FakeConfig(str(cwd_tmp / 'logs'))
    logger = AppLogger(config_manager=cfg)

    # nível inicial do logger é INFO (implementação), handlers usam config (DEBUG)
    console = logger.get_logger('console')
    assert console.level == logging.INFO
    for handler in console.handlers:
        assert handler.level == logging.DEBUG

    # Atualiza dinamicamente
    logger.set_console_level('WARNING')
    assert console.level == logging.WARNING
    for handler in console.handlers:
        assert handler.level == logging.WARNING


def test_log_methods_emit_expected_records(cwd_tmp):
    cfg = FakeConfig(str(cwd_tmp / 'logs'))
    logger = AppLogger(config_manager=cfg)
    # Para este teste, queremos console em INFO para não receber debug
    logger.set_console_level('INFO')
    h_main, h_debug, h_console = _attach_spy_handlers(logger)

    logger.log_success('ok')
    logger.log_warning('be careful')
    logger.log_error('failed', exception=ValueError('invalid'))
    logger.log_info('plain info')
    logger.log_debug('debug only')

    # main recebe info/warn/error/debug/success
    messages_main = [r.getMessage() for r in h_main.records]
    assert any('✅' in m for m in messages_main)
    assert any('⚠️' in m for m in messages_main)
    assert any('❌' in m for m in messages_main)
    assert any('plain info' in m for m in messages_main)
    assert any('debug only' in m for m in messages_main)

    # debug recebe tudo e com error
    messages_debug = [r.getMessage() for r in h_debug.records]
    assert any('✅' in m for m in messages_debug)
    assert any('⚠️' in m for m in messages_debug)
    assert any('❌' in m for m in messages_debug)
    assert any('plain info' in m for m in messages_debug)
    assert any('debug only' in m for m in messages_debug)

    # console não recebe debug
    messages_console = [r.getMessage() for r in h_console.records]
    assert any('✅' in m for m in messages_console)
    assert any('⚠️' in m for m in messages_console)
    assert any('❌' in m for m in messages_console)
    assert any('plain info' in m for m in messages_console)
    assert not any('debug only' in m for m in messages_console)


def test_save_payload_json_and_text(cwd_tmp):
    cfg = FakeConfig(str(cwd_tmp / 'logs'))
    logger = AppLogger(config_manager=cfg)

    # JSON payload
    out_json = logger.save_payload('sourceA', {"k": 1}, data_type='json')
    assert out_json
    p_json = PathReal(out_json)
    assert p_json.exists()
    content = p_json.read_text(encoding='utf-8')
    assert 'metadata' in content and 'k' in content

    # HTML/text payload
    out_html = logger.save_payload('sourceB', '<html>snippet</html>', data_type='html')
    assert out_html
    p_html = PathReal(out_html)
    assert p_html.exists()
    assert 'snippet' in p_html.read_text(encoding='utf-8')


def test_main_log_rotation_on_existing_log(cwd_tmp):
    # Prepara log existente que deve ser rotacionado
    logs_dir = cwd_tmp / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    existing = logs_dir / 'motorsport_calendar.log'
    existing.write_text('old log')

    cfg = FakeConfig(str(logs_dir))
    _ = AppLogger(config_manager=cfg)

    rotated_dir = logs_dir / 'rotated_logs'
    # Deve existir pelo menos um arquivo rotacionado
    rotated = list(rotated_dir.glob('motorsport_calendar_*.log'))
    assert len(rotated) >= 1


def test_rotating_file_handler_uses_config_sizes(cwd_tmp):
    cfg = FakeConfig(str(cwd_tmp / 'logs'))
    logger = AppLogger(config_manager=cfg)
    main = logger.get_logger('main')

    # encontra RotatingFileHandler e valida maxBytes/backupCount
    rfh = None
    for h in main.handlers:
        if h.__class__.__name__ == 'RotatingFileHandler':
            rfh = h
            break

    assert rfh is not None
    # 1 MB em bytes
    assert getattr(rfh, 'maxBytes', None) == 1 * 1024 * 1024
    assert getattr(rfh, 'backupCount', None) == 2


def test_get_execution_summary_and_finalize(cwd_tmp):
    cfg = FakeConfig(str(cwd_tmp / 'logs'))
    logger = AppLogger(config_manager=cfg)
    # incrementa contador via payload
    _ = logger.save_payload('sourceC', {"a": 1}, data_type='json')

    summary = logger.get_execution_summary()
    assert set(['execution_id', 'start_time', 'payloads_saved', 'log_files']).issubset(summary.keys())
    assert summary['payloads_saved'] >= 1

    # finalize não deve lançar
    logger.finalize_execution()
