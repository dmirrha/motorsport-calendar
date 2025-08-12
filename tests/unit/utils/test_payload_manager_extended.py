import os
from pathlib import Path
from time import time

import pytest

from utils.payload_manager import PayloadManager


class LoggerStub:
    def __init__(self):
        self.debug_calls = []
        self.error_calls = []
        self.warning_calls = []

    def debug(self, msg):
        self.debug_calls.append(msg)

    def error(self, msg, exc_info=False):
        self.error_calls.append((msg, exc_info))

    def warning(self, msg):
        self.warning_calls.append(msg)


def test_save_payload_binary_gzip(tmp_path: Path):
    base_dir = tmp_path / "payloads"
    pm = PayloadManager(base_dir=str(base_dir), logger=LoggerStub())

    saved = pm.save_payload(
        source="bin_src",
        data=b"\x00\xff\x10",
        data_type="binary",
        compress=True,
        max_payloads=10,
        max_age_days=30,
    )
    p = Path(saved)
    assert p.exists()
    # Extensão para binary + gzip
    assert p.suffixes[-2:] == [".binary", ".gz"]


def test_cleanup_old_payloads_by_age(tmp_path: Path):
    base_dir = tmp_path / "payloads"
    pm = PayloadManager(base_dir=str(base_dir), logger=LoggerStub())

    # Cria 3 arquivos e marca 2 como antigos (mtime muito no passado)
    for i in range(3):
        pm.save_payload(
            source="age_src",
            data={"i": i},
            data_type="json",
            compress=False,
            max_payloads=50,
            max_age_days=3650,
        )

    src_dir = base_dir / "age_src"
    files = sorted(src_dir.glob("*"))
    assert len(files) == 3

    # Ajusta mtime dos dois primeiros para 2 dias atrás
    old_ts = time() - 2 * 24 * 3600
    os.utime(files[0], (old_ts, old_ts))
    os.utime(files[1], (old_ts, old_ts))

    removed, errors = pm.cleanup_old_payloads("age_src", max_files=50, max_age_days=1)
    assert errors == 0
    assert removed >= 2  # pelo menos os dois antigos


def test_cleanup_all_old_payloads_limits_per_source(tmp_path: Path):
    base_dir = tmp_path / "payloads"
    pm = PayloadManager(base_dir=str(base_dir), logger=LoggerStub())

    # Fonte A com 3 arquivos
    for i in range(3):
        pm.save_payload("A", {"i": i}, data_type="json", compress=False, max_payloads=100, max_age_days=3650)
    # Fonte B com 2 arquivos
    for i in range(2):
        pm.save_payload("B", {"i": i}, data_type="json", compress=False, max_payloads=100, max_age_days=3650)

    results = pm.cleanup_all_old_payloads(max_files_per_source=1, max_age_days=3650)
    assert set(results.keys()) == {"A", "B"}
    # Deve ter removido (3-1)=2 de A e (2-1)=1 de B, tolerando diferenças se timestamps iguais
    assert results["A"][0] >= 1
    assert results["B"][0] >= 1


def test_get_payload_stats_returns_expected_fields(tmp_path: Path):
    base_dir = tmp_path / "payloads"
    pm = PayloadManager(base_dir=str(base_dir), logger=LoggerStub())

    pm.save_payload("stat_src", {"i": 0}, data_type="json", compress=False, max_payloads=100, max_age_days=3650)
    pm.save_payload("stat_src", {"i": 1}, data_type="json", compress=False, max_payloads=100, max_age_days=3650)

    stats = pm.get_payload_stats()
    assert "stat_src" in stats
    s = stats["stat_src"]
    assert s["file_count"] >= 2
    assert s["total_size"] >= 0
    assert "oldest_file" in s and "newest_file" in s
    assert "oldest_mtime" in s and "newest_mtime" in s
