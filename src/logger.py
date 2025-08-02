"""
Advanced Logging System for Motorsport Calendar

Provides centralized logging with multiple levels, payload storage,
and automatic log rotation per execution.
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import colorlog


class Logger:
    """Advanced logging system with payload storage and visual formatting."""
    
    def __init__(self, config_manager=None):
        """
        Initialize the logging system.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager
        self.execution_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.loggers: Dict[str, logging.Logger] = {}
        self.payload_counter = 0
        
        # Setup directories
        self._setup_directories()
        
        # Configure loggers
        self._setup_main_logger()
        self._setup_debug_logger()
        self._setup_console_logger()
        
        self.main_logger = self.get_logger('main')
        self.main_logger.info(f"🏁 Motorsport Calendar Logger initialized - Execution ID: {self.execution_id}")
    
    def _setup_directories(self) -> None:
        """Create necessary logging directories."""
        base_dir = Path("logs")
        
        directories = [
            base_dir,
            base_dir / "debug",
            base_dir / "payloads"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _get_log_config(self, key: str, default: Any = None) -> Any:
        """Get logging configuration value."""
        if self.config:
            return self.config.get(f'logging.{key}', default)
        return default
    
    def _setup_main_logger(self) -> None:
        """Setup main application logger."""
        logger = logging.getLogger('motorsport_calendar')
        logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # File handler with rotation
        log_file = Path("logs") / "motorsport_calendar.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self._get_log_config('rotation.max_size_mb', 10) * 1024 * 1024,
            backupCount=self._get_log_config('rotation.backup_count', 5),
            encoding='utf-8'
        )
        
        file_formatter = logging.Formatter(
            self._get_log_config('format.file', 
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s')
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(getattr(logging, self._get_log_config('levels.file', 'DEBUG')))
        
        logger.addHandler(file_handler)
        self.loggers['main'] = logger
    
    def _setup_debug_logger(self) -> None:
        """Setup detailed debug logger for current execution."""
        logger = logging.getLogger('motorsport_debug')
        logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Debug file for current execution
        debug_file = Path("logs") / "debug" / f"{self.execution_id}.log"
        debug_handler = logging.FileHandler(debug_file, encoding='utf-8')
        
        debug_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        debug_handler.setFormatter(debug_formatter)
        debug_handler.setLevel(logging.DEBUG)
        
        logger.addHandler(debug_handler)
        
        # Create symlink to latest log
        latest_link = Path("logs") / "debug" / "latest.log"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        
        try:
            latest_link.symlink_to(f"{self.execution_id}.log")
        except OSError:
            # Fallback for systems that don't support symlinks
            pass
        
        self.loggers['debug'] = logger
    
    def _setup_console_logger(self) -> None:
        """Setup colorized console logger."""
        logger = logging.getLogger('motorsport_console')
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Colorized console handler
        console_handler = colorlog.StreamHandler()
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(getattr(logging, self._get_log_config('levels.console', 'INFO')))
        
        logger.addHandler(console_handler)
        self.loggers['console'] = logger
    
    def get_logger(self, name: str = 'main') -> logging.Logger:
        """
        Get logger instance by name.
        
        Args:
            name: Logger name ('main', 'debug', 'console')
            
        Returns:
            Logger instance
        """
        return self.loggers.get(name, self.loggers['main'])
    
    def log_step(self, step: str, level: str = 'INFO') -> None:
        """
        Log a major execution step.
        
        Args:
            step: Step description
            level: Log level
        """
        message = f"🔄 STEP: {step}"
        
        # Log to all loggers
        log_level = getattr(logging, level.upper())
        for logger in self.loggers.values():
            logger.log(log_level, message)
    
    def log_success(self, message: str) -> None:
        """Log success message."""
        success_msg = f"✅ {message}"
        
        self.loggers['main'].info(success_msg)
        self.loggers['debug'].info(success_msg)
        self.loggers['console'].info(success_msg)
    
    def log_error(self, message: str, exception: Optional[Exception] = None) -> None:
        """
        Log error message with optional exception details.
        
        Args:
            message: Error message
            exception: Optional exception instance
        """
        error_msg = f"❌ {message}"
        
        if exception:
            error_msg += f" - {str(exception)}"
        
        self.loggers['main'].error(error_msg)
        self.loggers['debug'].error(error_msg, exc_info=exception is not None)
        self.loggers['console'].error(error_msg)
    
    def log_warning(self, message: str) -> None:
        """Log warning message."""
        warning_msg = f"⚠️  {message}"
        
        self.loggers['main'].warning(warning_msg)
        self.loggers['debug'].warning(warning_msg)
        self.loggers['console'].warning(warning_msg)
    
    def log_info(self, message: str) -> None:
        """Log info message."""
        self.loggers['main'].info(message)
        self.loggers['debug'].info(message)
        self.loggers['console'].info(message)
    
    def log_debug(self, message: str) -> None:
        """Log debug message."""
        self.loggers['main'].debug(message)
        self.loggers['debug'].debug(message)
    
    def debug(self, message: str) -> None:
        """Alias for log_debug for compatibility."""
        self.log_debug(message)
    
    def info(self, message: str) -> None:
        """Alias for log_info for compatibility."""
        self.log_info(message)
    
    def set_console_level(self, level: str) -> None:
        """Set console logger level dynamically."""
        if 'console' in self.loggers:
            level_obj = getattr(logging, level.upper(), logging.INFO)
            self.loggers['console'].setLevel(level_obj)
            # Also update the handler level
            for handler in self.loggers['console'].handlers:
                handler.setLevel(level_obj)
    
    def save_payload(self, source: str, data: Any, data_type: str = 'json', 
                    include_headers: bool = False, headers: Optional[Dict] = None) -> str:
        """
        Save raw payload data to file.
        
        Args:
            source: Source name (e.g., 'tomada_tempo', 'ergast_api')
            data: Raw data to save
            data_type: Data type ('json', 'html', 'xml', 'text')
            include_headers: Whether to include HTTP headers
            headers: HTTP headers if available
            
        Returns:
            Path to saved file
        """
        self.payload_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate filename
        filename = f"{source}_{timestamp}_{self.payload_counter:03d}.{data_type}"
        filepath = Path("logs") / "payloads" / filename
        
        try:
            # Prepare data for saving
            if data_type == 'json':
                if isinstance(data, (dict, list)):
                    save_data = data
                else:
                    save_data = {"raw_data": str(data)}
                
                # Add metadata
                payload = {
                    "metadata": {
                        "source": source,
                        "timestamp": datetime.now().isoformat(),
                        "execution_id": self.execution_id,
                        "payload_id": self.payload_counter
                    },
                    "data": save_data
                }
                
                # Add headers if provided
                if include_headers and headers:
                    payload["headers"] = dict(headers)
                
                # Save with pretty printing
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False, default=str)
            
            else:
                # Save raw data for other types
                mode = 'w' if data_type in ['html', 'xml', 'text'] else 'wb'
                encoding = 'utf-8' if mode == 'w' else None
                
                with open(filepath, mode, encoding=encoding) as f:
                    if isinstance(data, str) and mode == 'w':
                        f.write(data)
                    elif isinstance(data, bytes) and mode == 'wb':
                        f.write(data)
                    else:
                        f.write(str(data))
            
            self.log_debug(f"💾 Payload saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.log_error(f"Failed to save payload for {source}", e)
            return ""
    
    def log_source_start(self, source: str) -> None:
        """Log start of data source collection."""
        message = f"🌐 Starting data collection from: {source}"
        self.log_info(message)
    
    def log_source_success(self, source: str, event_count: int) -> None:
        """Log successful data collection from source."""
        message = f"✅ {source}: Collected {event_count} events"
        self.log_success(message)
    
    def log_source_error(self, source: str, error: str) -> None:
        """Log error in data source collection."""
        message = f"❌ {source}: {error}"
        self.log_error(message)
    
    def log_category_detection(self, category: str, confidence: float, source: str) -> None:
        """Log category detection result."""
        confidence_icon = "🎯" if confidence > 0.8 else "🔍" if confidence > 0.6 else "❓"
        message = f"{confidence_icon} Category detected: '{category}' (confidence: {confidence:.2f}) from {source}"
        self.log_debug(message)
    
    def log_duplicate_removed(self, event_name: str, sources: List[str]) -> None:
        """Log duplicate event removal."""
        message = f"🔄 Duplicate removed: '{event_name}' (found in: {', '.join(sources)})"
        self.log_debug(message)
    
    def log_weekend_detection(self, start_date: str, end_date: str, event_count: int) -> None:
        """Log weekend detection result."""
        message = f"📅 Weekend detected: {start_date} to {end_date} ({event_count} events)"
        self.log_info(message)
    
    def log_ical_generation(self, filepath: str, event_count: int) -> None:
        """Log iCal file generation."""
        message = f"📋 iCal generated: {filepath} ({event_count} events)"
        self.log_success(message)
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get summary of current execution.
        
        Returns:
            Dictionary with execution statistics
        """
        return {
            "execution_id": self.execution_id,
            "start_time": self.execution_id,
            "payloads_saved": self.payload_counter,
            "log_files": {
                "main": "logs/motorsport_calendar.log",
                "debug": f"logs/debug/{self.execution_id}.log",
                "payloads": f"logs/payloads/ ({self.payload_counter} files)"
            }
        }
    
    def finalize_execution(self) -> None:
        """Finalize logging for current execution."""
        summary = self.get_execution_summary()
        
        self.log_info("🏁 Execution completed")
        self.log_debug(f"📊 Execution Summary: {json.dumps(summary, indent=2)}")
        
        # Close all handlers
        for logger in self.loggers.values():
            for handler in logger.handlers:
                handler.close()
    
    def __del__(self):
        """Cleanup when logger is destroyed."""
        try:
            self.finalize_execution()
        except:
            pass
