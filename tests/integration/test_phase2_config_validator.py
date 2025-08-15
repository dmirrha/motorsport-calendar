import os
from pathlib import Path

import pytest

from src.utils.config_validator import (
    validate_logging_config,
    validate_payload_settings,
    ConfigValidationError,
)
from src.utils.error_codes import ErrorCode

pytestmark = pytest.mark.integration


def test_validate_logging_config_normalizes_levels_and_creates_dirs(tmp_path):
    cfg = {
        "levels": {"console": "info", "file": "debug", "debug_file": "warning"},
        "file_structure": {
            # A implementação trata todos os caminhos como diretórios
            "main_log": str(tmp_path / "main_log"),
            "debug_directory": str(tmp_path / "debug"),
            "payload_directory": str(tmp_path / "payloads"),
        },
        "retention": {"max_logs_to_keep": "3", "max_payloads_to_keep": 2, "delete_older_than_days": 1},
        "rotation": {"max_size_mb": "5", "backup_count": 1},
    }

    merged = validate_logging_config(cfg)

    assert merged["levels"]["console"] == "INFO"
    assert merged["levels"]["file"] == "DEBUG"
    assert merged["levels"]["debug_file"] == "WARNING"

    for key in ["main_log", "debug_directory", "payload_directory"]:
        p = Path(merged["file_structure"][key])
        assert p.exists()
        assert os.access(p, os.W_OK)

    # Coerções numéricas mínimas
    assert merged["retention"]["max_logs_to_keep"] >= 1
    assert merged["rotation"]["backup_count"] >= 1


def test_validate_logging_config_invalid_level_raises():
    bad = {"levels": {"console": "INVALID"}, "file_structure": {"main_log": "logs/main_log"}}
    with pytest.raises(ConfigValidationError) as exc:
        validate_logging_config(bad)
    err = exc.value
    assert err.error_code == ErrorCode.CONFIG_VALIDATION_ERROR
    assert err.field == "levels.console"


def test_validate_payload_settings_bool_and_numeric_coercion():
    settings = {
        "save_raw": 0,  # False
        "pretty_print": 1,  # True
        "include_headers": True,
        "separate_by_source": False,
        "compress": 0,  # False
        "max_files_per_source": "7",
        "max_age_days": 2,
    }

    merged = validate_payload_settings(settings)

    assert merged["save_raw"] is False
    assert merged["compress"] is False
    assert merged["pretty_print"] is True
    assert merged["include_headers"] is True
    assert merged["separate_by_source"] is False
    assert merged["max_files_per_source"] == 7
    assert merged["max_age_days"] == 2
