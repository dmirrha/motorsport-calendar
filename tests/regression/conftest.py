"""
Configuration and fixtures for regression tests.
"""
import os
import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import application components
from src.config_manager import ConfigManager
from src.logger import Logger

@pytest.fixture(scope="session")
def test_data_dir():
    """Return the path to the test data directory."""
    return Path(__file__).parent / "test_data"

@pytest.fixture(scope="session")
def sample_events(test_data_dir):
    """Load sample events data for testing."""
    with open(test_data_dir / "sample_events.json", "r") as f:
        return json.load(f)

@pytest.fixture(scope="function")
def temp_output_dir(tmp_path):
    """Create a temporary output directory for tests."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir

@pytest.fixture(scope="function")
def test_config(test_data_dir, tmp_path):
    """Create a test configuration with temporary paths."""
    # Load base test config
    config_path = test_data_dir / "test_config.json"
    config = ConfigManager(config_path)
    
    # Update paths to use temporary directory
    config.config["general"]["output_directory"] = str(tmp_path / "output")
    config.config["logging"]["file_structure"]["main_log"] = str(tmp_path / "test.log")
    config.config["logging"]["file_structure"]["debug_directory"] = str(tmp_path / "debug")
    config.config["logging"]["file_structure"]["payload_directory"] = str(tmp_path / "payloads")
    
    return config

@pytest.fixture(scope="function")
def test_logger(test_config, tmp_path):
    """Create a test logger instance."""
    # Create debug and payload directories
    (tmp_path / "debug").mkdir(exist_ok=True)
    (tmp_path / "payloads").mkdir(exist_ok=True)
    
    return Logger(test_config)

@pytest.fixture(scope="function")
def next_weekend():
    """Return the next weekend's date range (Saturday and Sunday)."""
    today = datetime.now()
    days_until_saturday = (5 - today.weekday()) % 7  # 5 is Saturday
    saturday = today + timedelta(days=days_until_saturday)
    sunday = saturday + timedelta(days=1)
    return saturday.date(), sunday.date()

# Configure pytest to show local variables in tracebacks
def pytest_configure(config):
    config.option.tb_locals = True
