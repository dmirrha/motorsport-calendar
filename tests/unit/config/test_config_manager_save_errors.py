from pathlib import Path
import builtins
import pytest

from config_manager import ConfigManager


def test_save_config_raises_when_directory_creation_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    cfg_path = tmp_path / "cfg" / "config.json"
    cm = ConfigManager(config_path=str(cfg_path))

    parent_dir = cfg_path.parent

    orig_mkdir = Path.mkdir

    def fake_mkdir(self, parents=False, exist_ok=False):
        if str(self) == str(parent_dir):
            raise OSError("cannot create parent dir")
        return orig_mkdir(self, parents=parents, exist_ok=exist_ok)

    monkeypatch.setattr(Path, "mkdir", fake_mkdir)

    cm.set("general.log_level", "DEBUG")
    with pytest.raises(Exception):
        cm.save_config()


def test_save_config_raises_when_open_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    cfg_path = tmp_path / "cfg" / "config.json"
    cm = ConfigManager(config_path=str(cfg_path))

    # Deixa mkdir funcionar, mas open falhar apenas para este caminho
    real_open = builtins.open

    def fake_open(file, mode="r", *args, **kwargs):
        if str(file) == str(cfg_path) and "w" in mode:
            raise OSError("cannot open for writing")
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)

    cm.set("general.log_level", "DEBUG")
    with pytest.raises(Exception):
        cm.save_config()
