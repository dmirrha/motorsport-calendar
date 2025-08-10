import os
import pytest


@pytest.mark.unit
def test_env_var_set_and_delete(monkeypatch):
    # garante que não exista
    monkeypatch.delenv("MC_TMP_VAR", raising=False)
    assert "MC_TMP_VAR" not in os.environ

    # define
    monkeypatch.setenv("MC_TMP_VAR", "123")
    assert os.environ.get("MC_TMP_VAR") == "123"

    # remove
    monkeypatch.delenv("MC_TMP_VAR", raising=False)
    assert "MC_TMP_VAR" not in os.environ
