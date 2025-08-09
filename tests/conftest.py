# Ajuste de path para permitir imports como `from sources...` e pacotes em `src/`
from pathlib import Path
import sys

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
