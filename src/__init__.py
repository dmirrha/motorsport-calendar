"""
Motorsport Calendar - Core Modules

This package contains the core modules for the Motorsport Calendar application.
"""

__version__ = "0.6.2"
__author__ = "Daniel Mirrha"
__email__ = "dmirrha@gmail.com"

# Core modules
from .config_manager import ConfigManager
from .logger import Logger
from .ui_manager import UIManager
from .category_detector import CategoryDetector
from .data_collector import DataCollector
from .event_processor import EventProcessor
from .ical_generator import ICalGenerator

__all__ = [
    "ConfigManager",
    "Logger", 
    "UIManager",
    "CategoryDetector",
    "DataCollector",
    "EventProcessor",
    "ICalGenerator"
]
