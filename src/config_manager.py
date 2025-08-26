"""
Configuration Manager for Motorsport Calendar

Handles loading, validation, and access to configuration settings.
Supports JSON configuration files with validation and default values.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
try:
    from .utils.config_validator import (
        validate_data_sources_config,
        ConfigValidationError,
        validate_ai_config,
    )
except Exception:
    try:
        from src.utils.config_validator import (
            validate_data_sources_config,
            ConfigValidationError,
            validate_ai_config,
        )
    except Exception:
        from utils.config_validator import (
            validate_data_sources_config,
            ConfigValidationError,
            validate_ai_config,
        )


class ConfigManager:
    """Manages application configuration with validation and defaults."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. Defaults to 'config/config.json'
        """
        self.config_path = config_path or "config/config.json"
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self._defaults = {
            "general": {
                "timezone": "America/Sao_Paulo",
                "language": "pt-BR",
                "log_level": "INFO",
                "output_directory": "./output"
            },
            "data_sources": {
                "priority_order": ["tomada_tempo"],
                "timeout_seconds": 10,
                "retry_attempts": 3,
                "retry_failed_sources": True,
                "max_retries": 1,
                "retry_backoff_seconds": 0.5,
                "rate_limit_delay": 1.0
            },
            "event_filters": {
                "category_detection": {
                    "enabled": True,
                    "learning_mode": True,
                    "confidence_threshold": 0.7
                },
                "included_categories": ["*"],
                "excluded_categories": []
            },
            "ical_parameters": {
                "calendar_name": "Motorsport Events",
                "timezone": "America/Sao_Paulo",
                "default_duration_minutes": 120,
                "enforce_sort": True
            }
        }
        
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file with fallback to defaults."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                
                # Merge with defaults
                self.config = self._deep_merge(self._defaults, file_config)
                self.logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self.logger.warning(f"Config file {self.config_path} not found, using defaults")
                self.config = self._defaults.copy()
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            self.config = self._defaults.copy()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self.config = self._defaults.copy()
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to configuration key (e.g., 'general.timezone')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to configuration key
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_general_config(self) -> Dict[str, Any]:
        """Get general configuration."""
        return self.get('general', {})
    
    def get_data_sources_config(self) -> Dict[str, Any]:
        """Get data sources configuration."""
        return self.get('data_sources', {})
    
    def get_deduplication_config(self) -> Dict[str, Any]:
        """Get deduplication configuration."""
        return self.get('deduplication', {
            'similarity_threshold': 85,
            'time_tolerance_minutes': 30,
            'location_similarity_threshold': 80,
            'category_similarity_threshold': 90
        })
    
    def get_priority_sources(self) -> List[str]:
        """Get prioritized list of data sources."""
        return self.get('data_sources.priority_order', [])
    
    def get_excluded_sources(self) -> List[str]:
        """Get list of excluded data sources."""
        return self.get('data_sources.excluded_sources', [])
    
    def get_event_filters(self) -> Dict[str, Any]:
        """Get event filtering configuration."""
        return self.get('event_filters', {})
    
    def get_included_categories(self) -> List[str]:
        """Get list of included categories."""
        return self.get('event_filters.included_categories', ['*'])
    
    def get_excluded_categories(self) -> List[str]:
        """Get list of excluded categories."""
        return self.get('event_filters.excluded_categories', [])
    
    def get_ical_config(self) -> Dict[str, Any]:
        """Get iCal generation configuration."""
        return self.get('ical_parameters', {})
    
    def get_timezone(self) -> str:
        """Get configured timezone."""
        return self.get('general.timezone', 'America/Sao_Paulo')
    
    def get_output_directory(self) -> str:
        """Get output directory path."""
        return self.get('general.output_directory', './output')
    
    def get_log_level(self) -> str:
        """Get logging level."""
        return self.get('general.log_level', 'INFO')
    
    def is_category_detection_enabled(self) -> bool:
        """Check if dynamic category detection is enabled."""
        return self.get('event_filters.category_detection.enabled', True)
    
    def get_category_confidence_threshold(self) -> float:
        """Get minimum confidence threshold for category detection."""
        return self.get('event_filters.category_detection.confidence_threshold', 0.7)
    
    def is_learning_mode_enabled(self) -> bool:
        """Check if category learning mode is enabled."""
        return self.get('event_filters.category_detection.learning_mode', True)
    
    def get_streaming_providers(self, region: str = None) -> Dict[str, Any]:
        """
        Get streaming providers configuration.
        
        Args:
            region: Region code (e.g., 'BR', 'US'). Uses config default if None.
            
        Returns:
            Streaming providers configuration
        """
        if region is None:
            region = self.get('streaming_providers.region', 'BR')
        
        providers = self.get('streaming_providers.mappings', {})
        return {category: providers.get(category, {}).get(region, []) 
                for category in providers.keys()}
    
    def save_config(self, path: Optional[str] = None) -> None:
        """
        Save current configuration to file.
        
        Args:
            path: Path to save configuration. Uses current config_path if None.
        """
        save_path = path or self.config_path
        
        try:
            # Ensure directory exists
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration saved to {save_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving config to {save_path}: {e}")
            raise
    
    def validate_config(self) -> List[str]:
        """
        Validate configuration and return list of issues.
        
        Returns:
            List of validation error messages
        """
        issues = []
        
        # Check required sections
        required_sections = ['general', 'data_sources', 'event_filters', 'ical_parameters']
        for section in required_sections:
            if section not in self.config:
                issues.append(f"Missing required section: {section}")
        
        # Validate timezone
        timezone = self.get_timezone()
        try:
            import pytz
            pytz.timezone(timezone)
        except:
            issues.append(f"Invalid timezone: {timezone}")
        
        # Validate output directory
        output_dir = self.get_output_directory()
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create output directory {output_dir}: {e}")

        # Validate and normalize data_sources (including retry keys)
        try:
            normalized_ds = validate_data_sources_config(self.config.get('data_sources', {}))
            self.config['data_sources'] = normalized_ds
        except ConfigValidationError as e:
            issues.append(f"data_sources invalid: {e}")

        # Validate and normalize AI section
        try:
            normalized_ai = validate_ai_config(self.config.get('ai', {}))
            self.config['ai'] = normalized_ai
        except ConfigValidationError as e:
            issues.append(f"ai invalid: {e}")
        
        # Validate priority sources
        priority_sources = self.get_priority_sources()
        if not priority_sources:
            issues.append("No data sources configured in priority_order")
        
        # Validate iCal parameters
        enforce_sort = self.get('ical_parameters.enforce_sort', True)
        if not isinstance(enforce_sort, bool):
            issues.append("ical_parameters.enforce_sort must be boolean")
        
        return issues
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"ConfigManager(config_path='{self.config_path}', sections={list(self.config.keys())})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()
