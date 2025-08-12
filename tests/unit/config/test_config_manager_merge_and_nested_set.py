import json
from pathlib import Path

from config_manager import ConfigManager


def test_deep_merge_from_file_overrides_defaults(tmp_path: Path):
    # Cria um arquivo de config com overrides aninhados
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    cfg_path = cfg_dir / "config.json"

    file_cfg = {
        "general": {
            "timezone": "UTC",
            "output_directory": str(tmp_path / "out")
        },
        "data_sources": {
            "priority_order": ["tomada_tempo", "another_source"],
            "retry_attempts": 5
        },
        "event_filters": {
            "category_detection": {
                "enabled": False,
                "confidence_threshold": 0.9
            },
            "excluded_categories": ["Karting"]
        },
        "ical_parameters": {
            "default_duration_minutes": 90
        }
    }
    cfg_path.write_text(json.dumps(file_cfg), encoding="utf-8")

    cm = ConfigManager(config_path=str(cfg_path))

    # Verifica merge: chaves default preservadas, overrides aplicados
    assert cm.get("general.timezone") == "UTC"
    assert cm.get("general.language") == "pt-BR"  # veio do default
    assert cm.get("data_sources.retry_attempts") == 5
    assert cm.get("data_sources.rate_limit_delay") == 1.0  # default preservado
    assert cm.get("event_filters.category_detection.enabled") is False
    assert cm.get("event_filters.category_detection.confidence_threshold") == 0.9
    assert cm.get("event_filters.excluded_categories") == ["Karting"]
    assert cm.get("ical_parameters.default_duration_minutes") == 90


def test_set_nested_paths_create_intermediate_nodes(tmp_path: Path):
    cm = ConfigManager()  # defaults

    # Caminho multi-nível inexistente deve criar nós intermediários
    cm.set("streaming_providers.mappings.F1.BR", ["BandSports"]) 
    cm.set("streaming_providers.mappings.F1.US", ["ESPN+"])

    providers = cm.get("streaming_providers.mappings")
    assert "F1" in providers
    assert providers["F1"]["BR"] == ["BandSports"]
    assert providers["F1"]["US"] == ["ESPN+"]
