import os
from pathlib import Path

import pytest
 
from utils.payload_manager import PayloadManager


class LoggerStub:
    def __init__(self):
        self.debug_calls = []
        self.error_calls = []

    def debug(self, msg):
        self.debug_calls.append(msg)

    def error(self, msg, exc_info=False):
        self.error_calls.append((msg, exc_info))


def test_save_payload_json_gz_tmp_path(tmp_path: Path):
    base_dir = tmp_path / "payloads"
    logger = LoggerStub()

    pm = PayloadManager(base_dir=str(base_dir), logger=logger)

    saved_path = pm.save_payload(
        source="tomada_tempo",
        data={"ok": True},
        data_type="json",
        compress=True,
        max_payloads=10,
        max_age_days=30,
    )

    p = Path(saved_path)
    assert str(p).startswith(str(base_dir))
    assert p.exists()
    assert p.suffixes[-2:] == [".json", ".gz"]


def test_save_payload_plain_text_no_compress(tmp_path: Path):
    base_dir = tmp_path / "payloads"
    logger = LoggerStub()

    pm = PayloadManager(base_dir=str(base_dir), logger=logger)

    saved_path = pm.save_payload(
        source="tomada_tempo",
        data="<html>ok</html>",
        data_type="html",
        compress=False,
        max_payloads=10,
        max_age_days=30,
    )

    p = Path(saved_path)
    assert p.exists()
    assert p.suffix == ".html"


def test_cleanup_enforces_max_payloads(tmp_path: Path):
    base_dir = tmp_path / "payloads"
    logger = LoggerStub()
    pm = PayloadManager(base_dir=str(base_dir), logger=logger)

    # cria mais que o limite
    for i in range(0, 12):
        pm.save_payload(
            source="tomada_tempo",
            data={"i": i},
            data_type="json",
            compress=False,
            max_payloads=5,
            max_age_days=365,
        )

    files = list((base_dir / "tomada_tempo").glob("*"))
    assert len(files) <= 5
