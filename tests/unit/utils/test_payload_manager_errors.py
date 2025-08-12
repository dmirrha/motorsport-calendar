import os
import shutil
from pathlib import Path

import pytest

from utils.payload_manager import PayloadManager


class LoggerStub:
    def __init__(self):
        self.debug_calls = []
        self.error_calls = []
        self.warning_calls = []

    def debug(self, msg):
        self.debug_calls.append(str(msg))

    def error(self, msg, exc_info=False):
        self.error_calls.append((str(msg), exc_info))

    def warning(self, msg):
        self.warning_calls.append(str(msg))


def test_init_directory_creation_failure(monkeypatch, tmp_path: Path):
    logger = LoggerStub()

    def raise_mkdir(self, parents=False, exist_ok=False):
        raise OSError("cannot create")

    # Força falha na criação do diretório base
    monkeypatch.setattr(Path, "mkdir", raise_mkdir)

    with pytest.raises(RuntimeError) as ei:
        PayloadManager(base_dir=str(tmp_path / "payloads"), logger=logger)

    assert "LOGGER_INIT_FAILED" in str(ei.value)
    assert any("Falha ao criar diretório" in msg for msg, _ in logger.error_calls)


def test_save_payload_unsupported_type_raises(tmp_path: Path):
    pm = PayloadManager(base_dir=str(tmp_path / "payloads"), logger=LoggerStub())

    # A função encapsula o ValueError e relança como IOError/OSError
    with pytest.raises(IOError) as ei:
        pm.save_payload(
            source="src",
            data={"a": 1},
            data_type="csv",  # não suportado
            compress=False,
            max_payloads=10,
            max_age_days=30,
        )

    msg = str(ei.value)
    assert "OUTPUT_WRITE_ERROR" in msg
    assert "OUTPUT_FORMAT_ERROR" in msg


def test_save_payload_write_error_converted_to_ioerror(monkeypatch, tmp_path: Path):
    logger = LoggerStub()
    pm = PayloadManager(base_dir=str(tmp_path / "payloads"), logger=logger)

    def boom(*args, **kwargs):
        raise RuntimeError("write failed")

    monkeypatch.setattr(pm, "_write_data", boom)

    with pytest.raises(IOError) as ei:
        pm.save_payload(
            source="src",
            data={"a": 1},
            data_type="json",
            compress=False,
            max_payloads=10,
            max_age_days=30,
        )

    assert "OUTPUT_WRITE_ERROR" in str(ei.value)
    assert any("Falha ao salvar payload" in msg for msg, _ in logger.error_calls)


def test_cleanup_old_payloads_missing_source_returns_zero(tmp_path: Path):
    pm = PayloadManager(base_dir=str(tmp_path / "payloads"), logger=LoggerStub())
    removed, errors = pm.cleanup_old_payloads("unknown_src", max_files=10, max_age_days=1)
    assert (removed, errors) == (0, 0)


def test_cleanup_old_payloads_unlink_errors_logged(monkeypatch, tmp_path: Path):
    logger = LoggerStub()
    pm = PayloadManager(base_dir=str(tmp_path / "payloads"), logger=logger)

    # cria 3 arquivos recentes
    for i in range(3):
        pm.save_payload(
            source="src",
            data={"i": i},
            data_type="json",
            compress=False,
            max_payloads=100,
            max_age_days=3650,
        )

    # Força erro ao tentar remover excedentes
    def raise_unlink(self):
        raise OSError("cannot unlink")

    monkeypatch.setattr(Path, "unlink", raise_unlink)

    removed, errors = pm.cleanup_old_payloads("src", max_files=1, max_age_days=3650)
    assert removed == 0
    assert errors >= 1
    assert any("LOG_RETENTION_CLEANUP_FAILED" in msg for msg in logger.warning_calls)


def test_get_payload_stats_when_base_dir_missing_returns_empty(tmp_path: Path):
    base_dir = tmp_path / "payloads"
    pm = PayloadManager(base_dir=str(base_dir), logger=LoggerStub())

    # Remove o diretório base para acionar o early-return
    shutil.rmtree(base_dir)

    stats = pm.get_payload_stats()
    assert stats == {}
