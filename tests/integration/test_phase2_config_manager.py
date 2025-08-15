"""
Phase 2 Integration — ConfigManager (complementos)
Objetivo: validar merge profundo com defaults e persistência simples em arquivo.
Marcadores: integration
"""

import json
import pytest
from pathlib import Path
from src.config_manager import ConfigManager

pytestmark = pytest.mark.integration


def test_config_manager_deep_merge_with_defaults(tmp_path):
    # Arquivo de config parcial que deve fazer merge com defaults
    cfg = {
        "data_sources": {
            "timeout_seconds": 20,  # override
        },
        "event_filters": {
            "category_detection": {
                "enabled": False  # override
            },
            "excluded_categories": ["Kart"],  # novo
        },
    }
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")

    cm = ConfigManager(config_path=str(cfg_path))

    # Defaults preservados quando não sobrescritos
    assert cm.get("general.language") == "pt-BR"
    assert cm.get("data_sources.rate_limit_delay") == 1.0  # ainda default

    # Overrides aplicados
    assert cm.get("data_sources.timeout_seconds") == 20
    assert cm.get("event_filters.category_detection.enabled") is False

    # Novos campos coexistem
    assert cm.get("event_filters.excluded_categories") == ["Kart"]


def test_config_manager_persistence_roundtrip(tmp_path):
    # ConfigManager em memória com set() e save_config()
    cm = ConfigManager(config_path=None)
    cm.set("general.output_directory", str(tmp_path / "out"))
    cm.set("event_filters.included_categories", ["F1", "WEC"]) 

    out_path = tmp_path / "saved_config.json"
    cm.save_config(path=str(out_path))

    # Lê novamente e compara
    cm2 = ConfigManager(config_path=str(out_path))
    assert cm2.get_output_directory() == str(tmp_path / "out")
    assert cm2.get_included_categories() == ["F1", "WEC"]
