"""
Motorsport Calendar - Core Modules

This package contains the core modules for the Motorsport Calendar application.
"""

__version__ = "1.0.0"
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

# Main application class
class MotorsportCalendar:
    """Main application class for Motorsport Calendar."""
    
    def __init__(self, config_path=None):
        """
        Initialize the application with optional config path.
        
        Args:
            config_path: Path to the configuration file. If provided, it will be loaded.
        """
        self.config_manager = ConfigManager(config_path=config_path)
        
        # Initialize components
        self.logger = Logger(self.config_manager)
        self.ui_manager = UIManager(self.config_manager, self.logger)
        self.category_detector = CategoryDetector(self.config_manager, self.logger)
        self.data_collector = DataCollector(self.config_manager, self.logger, self.category_detector)
        self.event_processor = EventProcessor(self.config_manager, self.logger)
        self.ical_generator = ICalGenerator(self.config_manager, self.logger, self.ui_manager)

__all__ = [
    'MotorsportCalendar',
    "ConfigManager",
    "Logger", 
    "UIManager",
    "CategoryDetector",
    "DataCollector",
    "EventProcessor",
    "ICalGenerator"
]
