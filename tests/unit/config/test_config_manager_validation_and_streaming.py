from pathlib import Path
import pytest

from config_manager import ConfigManager


def test_validate_config_invalid_timezone():
    cm = ConfigManager()
    cm.set("general.timezone", "Invalid/Zone")

    issues = cm.validate_config()
    assert any("Invalid timezone: Invalid/Zone" in msg for msg in issues)


def test_validate_config_output_dir_inaccessible(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    cm = ConfigManager()
    out_dir = tmp_path / "blocked"
    cm.set("general.output_directory", str(out_dir))

    orig_mkdir = Path.mkdir

    def fake_mkdir(self, parents=False, exist_ok=False):
        if str(self) == str(out_dir):
            raise PermissionError("denied")
        return orig_mkdir(self, parents=parents, exist_ok=exist_ok)

    monkeypatch.setattr(Path, "mkdir", fake_mkdir)

    issues = cm.validate_config()
    assert any("Cannot create output directory" in msg and str(out_dir) in msg for msg in issues)


def test_validate_config_missing_sections():
    cm = ConfigManager()
    # remove uma seção requerida para acionar erro de validação
    if "data_sources" in cm.config:
        del cm.config["data_sources"]

    issues = cm.validate_config()
    assert any("Missing required section: data_sources" in msg for msg in issues)


def test_get_streaming_providers_by_region(tmp_path: Path):
    cm = ConfigManager()

    cm.set("streaming_providers.region", "US")
    cm.set(
        "streaming_providers.mappings",
        {
            "F1": {"US": ["ESPN"], "BR": ["BandSports"]},
            "WEC": {"US": ["Max"], "BR": []},
        },
    )

    us = cm.get_streaming_providers()
    assert us == {"F1": ["ESPN"], "WEC": ["Max"]}

    br = cm.get_streaming_providers("BR")
    assert br == {"F1": ["BandSports"], "WEC": []}
