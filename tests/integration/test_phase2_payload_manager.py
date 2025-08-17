"""
Fase 2 — PayloadManager (integração essencial de serialização/rotação)
Marcadores: integration
"""

import os
from time import time
from pathlib import Path

import pytest

from src.utils.payload_manager import PayloadManager

pytestmark = pytest.mark.integration


def test_end_to_end_serializacao_compactacao_limpeza(tmp_path: Path):
    base_dir = tmp_path / "payloads"
    pm = PayloadManager(base_dir=str(base_dir))

    # JSON compactado
    p_json = Path(
        pm.save_payload(
            source="srcA",
            data={"ok": True},
            data_type="json",
            compress=True,
            max_payloads=50,
            max_age_days=3650,
        )
    )
    assert p_json.exists()
    assert p_json.suffixes[-2:] == [".json", ".gz"]

    # HTML sem compressão
    p_html = Path(
        pm.save_payload(
            source="srcA",
            data="<html>ok</html>",
            data_type="html",
            compress=False,
            max_payloads=50,
            max_age_days=3650,
        )
    )
    assert p_html.exists() and p_html.suffix == ".html"

    # Binário compactado
    p_bin = Path(
        pm.save_payload(
            source="srcA",
            data=b"\x00\xff\x10",
            data_type="binary",
            compress=True,
            max_payloads=50,
            max_age_days=3650,
        )
    )
    assert p_bin.exists() and p_bin.suffixes[-2:] == [".binary", ".gz"]

    # Cria 2 antigos para limpeza por idade
    old_files = [
        Path(
            pm.save_payload(
                source="srcA",
                data={"i": i},
                data_type="json",
                compress=False,
                max_payloads=50,
                max_age_days=3650,
            )
        )
        for i in range(2)
    ]
    old_ts = time() - 3 * 24 * 3600
    for f in old_files:
        os.utime(f, (old_ts, old_ts))

    removed_age, errors_age = pm.cleanup_old_payloads("srcA", max_files=50, max_age_days=1)
    assert errors_age == 0
    assert removed_age >= 2

    # Limpeza por quantidade (mantém apenas 2)
    for i in range(6):
        pm.save_payload("srcA", {"k": i}, data_type="json", compress=False, max_payloads=50, max_age_days=3650)
    removed_count, errors_count = pm.cleanup_old_payloads("srcA", max_files=2, max_age_days=3650)
    assert errors_count == 0
    remaining = list((base_dir / "srcA").glob("*"))
    assert len(remaining) <= 2


def test_cleanup_all_e_estatisticas(tmp_path: Path):
    base_dir = tmp_path / "payloads"
    pm = PayloadManager(base_dir=str(base_dir))

    # Popula duas fontes
    for i in range(3):
        pm.save_payload("A", {"i": i}, data_type="json", compress=False, max_payloads=50, max_age_days=3650)
    for i in range(2):
        pm.save_payload("B", {"i": i}, data_type="json", compress=False, max_payloads=50, max_age_days=3650)

    results = pm.cleanup_all_old_payloads(max_files_per_source=1, max_age_days=3650)
    assert set(results.keys()) == {"A", "B"}
    assert results["A"][0] >= 1
    assert results["B"][0] >= 1

    stats = pm.get_payload_stats()
    assert "A" in stats and "B" in stats
    for s in (stats["A"], stats["B"]):
        assert "file_count" in s and s["file_count"] >= 1
        assert "total_size" in s and s["total_size"] >= 0
        assert "oldest_file" in s and "newest_file" in s
        assert "oldest_mtime" in s and "newest_mtime" in s
