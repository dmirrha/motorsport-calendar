# Ajuste de path para permitir imports como `from sources...` e pacotes em `src/`
from pathlib import Path
import sys
import os
import time

import pytest

ROOT = Path(__file__).resolve().parent.parent  # raiz do repositório
SRC = ROOT / "src"

# Inserir raiz do repo (para `sources/`, etc.)
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

# Inserir `src/` se existir (para `motorsport_calendar`, etc.)
src_str = str(SRC)
if SRC.exists() and src_str not in sys.path:
    sys.path.insert(0, src_str)


@pytest.fixture(autouse=True, scope="session")
def _tz_america_sao_paulo():
    """Define TZ padrão para America/Sao_Paulo para garantir determinismo nos testes.

    Restaura o valor anterior ao final da sessão de testes.
    """
    prev_tz = os.environ.get("TZ")
    os.environ["TZ"] = "America/Sao_Paulo"
    if hasattr(time, "tzset"):
        time.tzset()
    try:
        yield
    finally:
        if prev_tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = prev_tz
        if hasattr(time, "tzset"):
            time.tzset()
