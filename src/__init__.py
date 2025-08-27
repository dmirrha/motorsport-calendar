"""
Motorsport Calendar - Core Modules

Este pacote contém os módulos centrais do Motorsport Calendar. Para evitar
imports pesados e colisões de dependências em tempo de import (ex.: icalendar
→ dateutil.rrule), os submódulos são importados sob demanda via __getattr__.
"""

from __future__ import annotations

import importlib
from typing import Any

__version__ = "0.6.10"
__author__ = "Daniel Mirrha"
__email__ = "dmirrha@gmail.com"

_MODULE_MAP = {
    "ConfigManager": ".config_manager",
    "Logger": ".logger",
    "UIManager": ".ui_manager",
    "CategoryDetector": ".category_detector",
    "DataCollector": ".data_collector",
    "EventProcessor": ".event_processor",
    "ICalGenerator": ".ical_generator",
}

__all__ = list(_MODULE_MAP.keys())

def __getattr__(name: str) -> Any:
    module_path = _MODULE_MAP.get(name)
    if module_path is None:
        raise AttributeError(f"module 'src' has no attribute '{name}'")
    mod = importlib.import_module(module_path, __name__)
    try:
        return getattr(mod, name)
    except AttributeError as exc:
        raise AttributeError(f"attribute '{name}' not found in '{module_path}'") from exc
