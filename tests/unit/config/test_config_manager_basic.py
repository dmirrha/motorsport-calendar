from pathlib import Path
import json

from config_manager import ConfigManager


def test_defaults_and_get_set_dot_notation(tmp_path: Path):
    cm = ConfigManager()  # usa defaults

    # Defaults
    assert cm.get("general.timezone") == "America/Sao_Paulo"
    assert cm.get("event_filters.category_detection.enabled") is True

    # get inexistente com default
    assert cm.get("does.not.exist", default=123) == 123

    # set/get com dot notation
    cm.set("general.language", "en-US")
    assert cm.get("general.language") == "en-US"


def test_validate_config_with_custom_output_dir(tmp_path: Path):
    cm = ConfigManager()
    out_dir = tmp_path / "out"
    cm.set("general.output_directory", str(out_dir))

    issues = cm.validate_config()
    assert issues == []  # tudo ok com defaults e diretório criável
    assert out_dir.exists()


def test_get_streaming_providers_structure():
    cm = ConfigManager()
    # Sem configurações de streaming por default → dict vazio
    providers = cm.get_streaming_providers()
    assert isinstance(providers, dict)
    assert providers == {}


def test_save_config_creates_directory_and_file(tmp_path: Path):
    cfg_path = tmp_path / "cfg" / "config.json"
    cm = ConfigManager(config_path=str(cfg_path))

    # modifica algo e salva
    cm.set("general.log_level", "DEBUG")
    cm.save_config()

    assert cfg_path.exists()
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    assert "general" in data
    assert data["general"]["log_level"] == "DEBUG"
