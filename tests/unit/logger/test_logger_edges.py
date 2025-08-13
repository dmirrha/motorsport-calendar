import gc
import logging
import os
from pathlib import Path as PathReal

import pytest

from src import logger as logger_module
from src.logger import Logger as AppLogger


class DummyLogger:
    def __init__(self):
        self.messages = []

    def debug(self, msg):
        self.messages.append(("DEBUG", msg))

    def error(self, msg, exc_info=False):
        self.messages.append(("ERROR", msg))


class ListHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


class CfgWithErrors:
    """Config que provoca exceção dentro de _get_log_config para cobrir o except."""

    def get(self, key, default=None):  # faz hasattr(self, 'get') ser True
        raise ValueError("boom in get")

    def get_ical_config(self):
        return {}


class FakeConfig:
    def __init__(self, base_logs_dir: str, retention_enabled: bool = True):
        self._map = {
            'logging.directory': base_logs_dir,
            'logging.levels.console': 'INFO',
            'logging.rotation.max_size_mb': 1,
            'logging.rotation.backup_count': 2,
            'logging.retention.enabled': retention_enabled,
        }
        self._ical = {
            'logging': {
                'retention': {
                    'enabled': True,
                    'max_days': 1,
                    'max_logs_to_keep': 3,
                    'delete_older_than_days': 1,
                }
            }
        }

    def get(self, key: str, default=None):
        return self._map.get(key, default)

    def get_ical_config(self):
        return self._ical


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


def test_setup_directories_with_internal_logger_and_no_cleanup(cwd_tmp, monkeypatch):
    cfg = FakeConfig(str(cwd_tmp / 'logs'), retention_enabled=True)
    app = AppLogger(config_manager=cfg)
    # Força uso do ramo com self.logger presente (linhas 247, 254, 261)
    app.logger = DummyLogger()
    # Evita executar limpeza real
    monkeypatch.setattr(logger_module.Logger, "_cleanup_old_logs", lambda self: None)
    app._setup_directories()


def test_domain_helpers_and_get_logger_fallback(cwd_tmp):
    cfg = FakeConfig(str(cwd_tmp / 'logs'), retention_enabled=False)
    app = AppLogger(config_manager=cfg)
    h_main, h_debug, h_console = _attach_spy_handlers(app)

    # get_logger fallback
    assert app.get_logger('nonexistent') is app.get_logger('main')

    # helpers
    app.log_source_start('SRC')
    app.log_source_success('SRC', 3)
    app.log_source_error('SRC', 'oops')
    app.log_weekend_detection('2025-01-01', '2025-01-03', 7)
    app.log_ical_generation('out.ics', 10)

    # category detection thresholds: 🎯 (>0.8), 🔍 (>0.6), ❓ (else)
    app.log_category_detection('CatA', 0.9, 'SRC')
    app.log_category_detection('CatB', 0.7, 'SRC')
    app.log_category_detection('CatC', 0.5, 'SRC')

    # duplicates
    app.log_duplicate_removed('EventX', ['A', 'B'])

    # assertions
    msgs_main = [r.getMessage() for r in h_main.records]
    msgs_debug = [r.getMessage() for r in h_debug.records]
    assert any('Starting data collection' in m for m in msgs_main)
    assert any('iCal generated' in m for m in msgs_main)
    assert any('Category detected' in m and '🎯' in m for m in msgs_debug)
    assert any('Category detected' in m and '🔍' in m for m in msgs_debug)
    assert any('Category detected' in m and '❓' in m for m in msgs_debug)
    assert any('Duplicate removed' in m for m in msgs_debug)


def test_cleanup_files_removes_excess(cwd_tmp):
    p = cwd_tmp / 'keepdir'
    p.mkdir(parents=True, exist_ok=True)
    files = [p / f'f{i}.log' for i in range(3)]
    for f in files:
        f.write_text('x')
    app = AppLogger(config_manager=FakeConfig(str(cwd_tmp / 'logs'), retention_enabled=False))

    # remove além do limite (mantém 2, remove o restante na ordem fornecida)
    app._cleanup_files(files, max_to_keep=2)
    assert files[0].exists()
    assert files[1].exists()
    assert not files[2].exists()


def test_cleanup_old_files_removes_by_age_and_empty_dirs(cwd_tmp):
    base = cwd_tmp / 'payloads'
    oldf = base / 'old.log'
    newf = base / 'new.log'
    (base / 'subempty').mkdir(parents=True, exist_ok=True)
    base.mkdir(parents=True, exist_ok=True)
    oldf.write_text('old')
    newf.write_text('new')
    # deixa oldf bem antigo
    os.utime(oldf, (1, 1))

    app = AppLogger(config_manager=FakeConfig(str(cwd_tmp / 'logs'), retention_enabled=False))
    # max_age_days = 1 -> deve apagar oldf
    app._cleanup_old_files(str(base), '*.log', max_age_days=1)
    assert not oldf.exists() and newf.exists()
    # subempty deve ser removido se vazio
    assert not (base / 'subempty').exists()


def test_get_log_config_exception_branch(cwd_tmp):
    app = AppLogger(config_manager=CfgWithErrors())
    # Deve cair no except e retornar default
    assert app._get_log_config('any.key', default=123) == 123


def test_setup_main_logger_rotation_failure(cwd_tmp, monkeypatch):
    logs_dir = cwd_tmp / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    existing = logs_dir / 'motorsport_calendar.log'
    existing.write_text('old')

    # Patching rename para levantar erro durante a rotação
    PClass = type(existing)
    original_rename = PClass.rename

    def boom_rename(self, *args, **kwargs):
        raise OSError('no-rename')

    monkeypatch.setattr(PClass, 'rename', boom_rename)
    try:
        _ = AppLogger(config_manager=FakeConfig(str(logs_dir), retention_enabled=False))
    finally:
        # restaura para evitar afetar outros testes
        monkeypatch.setattr(PClass, 'rename', original_rename)


def test_setup_debug_logger_unlink_and_symlink_failure(cwd_tmp, monkeypatch):
    cfg = FakeConfig(str(cwd_tmp / 'logs'), retention_enabled=False)
    app = AppLogger(config_manager=cfg)
    # cria latest.log para entrar no caminho unlink
    latest = PathReal('logs') / 'debug' / 'latest.log'
    latest.write_text('x')

    # força symlink_to a falhar para cobrir o except OSError
    PClass = type(latest)

    def boom_symlink(self, *args, **kwargs):
        raise OSError('nosymlink')

    monkeypatch.setattr(PClass, 'symlink_to', boom_symlink)
    # Reconfigura apenas o debug logger
    app._setup_debug_logger()
    # se chegamos aqui sem exception, caminhos foram exercitados
    assert app.get_logger('debug') is not None


def test_log_step_and_aliases(cwd_tmp):
    cfg = FakeConfig(str(cwd_tmp / 'logs'), retention_enabled=False)
    app = AppLogger(config_manager=cfg)
    h_main, h_debug, h_console = _attach_spy_handlers(app)

    app.log_step('Collect', level='WARNING')
    app.debug('dbg')
    app.info('inf')

    msgs_main = [r.getMessage() for r in h_main.records]
    msgs_console = [r.getMessage() for r in h_console.records]
    assert any('STEP: Collect' in m for m in msgs_main)
    assert any('dbg' in m for m in msgs_main)
    assert any('inf' in m for m in msgs_console)


def test_save_payload_raw_data_and_headers_and_bytes(cwd_tmp):
    cfg = FakeConfig(str(cwd_tmp / 'logs'), retention_enabled=False)
    app = AppLogger(config_manager=cfg)

    # json com tipo não dict/list -> cobre ramo raw_data
    out1 = app.save_payload('S', 123, data_type='json')
    assert out1 and PathReal(out1).exists()
    content1 = PathReal(out1).read_text(encoding='utf-8')
    assert 'raw_data' in content1

    # json com headers incluídos
    out2 = app.save_payload('S', {'a': 1}, data_type='json', include_headers=True, headers={'H': 'V'})
    content2 = PathReal(out2).read_text(encoding='utf-8')
    assert 'headers' in content2 and 'H' in content2

    # xml é salvo em modo texto ('w') no logger
    out3 = app.save_payload('S', '<x/>', data_type='xml')
    assert PathReal(out3).read_text(encoding='utf-8') == '<x/>'


def test_destructor_handles_exception(cwd_tmp, monkeypatch):
    cfg = FakeConfig(str(cwd_tmp / 'logs'), retention_enabled=False)
    app = AppLogger(config_manager=cfg)

    def boom_finalize(self):
        raise RuntimeError('finalize error')

    monkeypatch.setattr(logger_module.Logger, 'finalize_execution', boom_finalize)
    # força o coletor a chamar __del__
    del app
    gc.collect()


def test_get_log_config_with_none_config_hits_default(cwd_tmp):
    # Instancia com config None para cobrir retorno default imediato
    app = AppLogger(config_manager=None)
    assert app._get_log_config('anything', default=42) == 42


def test_save_payload_text_with_object_and_binary_custom_type(cwd_tmp):
    cfg = FakeConfig(str(cwd_tmp / 'logs'), retention_enabled=False)
    app = AppLogger(config_manager=cfg)

    # data_type 'text' com objeto não string -> cai no f.write(str(data))
    class X:
        def __str__(self):
            return 'OBJ'

    p1 = app.save_payload('S', X(), data_type='text')
    assert PathReal(p1).read_text(encoding='utf-8') == 'OBJ'

    # data_type custom não mapeado -> modo 'wb' e bytes branch
    p2 = app.save_payload('S', b'\x01\x02', data_type='bin')
    assert PathReal(p2).read_bytes() == b'\x01\x02'


def test_cleanup_files_removes_directories_via_rmtree(cwd_tmp):
    # Cria diretórios para serem removidos além do limite
    base = cwd_tmp / 'to_clean'
    dirs = [base / d for d in ['d0', 'd1', 'd2']]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    app = AppLogger(config_manager=FakeConfig(str(cwd_tmp / 'logs'), retention_enabled=False))
    app._cleanup_files(dirs, max_to_keep=1)
    assert dirs[0].exists() and not dirs[1].exists() and not dirs[2].exists()


def test_setup_directories_handles_mkdir_error(cwd_tmp, monkeypatch):
    cfg = FakeConfig(str(cwd_tmp / 'logs'), retention_enabled=False)
    app = AppLogger(config_manager=cfg)

    # Monkeypatch Path.mkdir para falhar apenas para rotated_logs
    import pathlib
    orig_mkdir = pathlib.Path.mkdir

    def patched_mkdir(self, *args, **kwargs):
        if str(self).endswith('rotated_logs'):
            raise OSError('mkdir fail')
        return orig_mkdir(self, *args, **kwargs)

    monkeypatch.setattr(pathlib.Path, 'mkdir', patched_mkdir)

    # Chama novamente para passar pelo ramo de erro
    app._setup_directories()
