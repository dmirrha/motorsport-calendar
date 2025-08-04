"""
Regression tests for file management functionality.
"""
import os
import time
from pathlib import Path
import pytest
from datetime import datetime, timedelta

# Import the module to test
from src.file_manager import FileManager

class TestFileManager:
    """Test cases for FileManager."""
    
    @pytest.fixture
    def file_manager(self, test_config, tmp_path):
        """Create a FileManager instance with test config."""
        # Update config with test paths
        test_config.config["general"]["output_directory"] = str(tmp_path / "output")
        test_config.config["logging"]["file_structure"]["debug_directory"] = str(tmp_path / "debug")
        test_config.config["logging"]["file_structure"]["payload_directory"] = str(tmp_path / "payloads")
        
        return FileManager(test_config)
    
    def test_ensure_directories(self, file_manager, tmp_path):
        """Test that required directories are created."""
        # Check that directories exist after initialization
        assert os.path.exists(file_manager.output_dir)
        assert os.path.exists(file_manager.debug_dir)
        assert os.path.exists(file_manager.payload_dir)
    
    def test_cleanup_old_files(self, file_manager, tmp_path):
        """Test cleanup of old files based on retention policy."""
        # Create test files with different modification times
        now = time.time()
        old_file = tmp_path / "debug" / "old_file.log"
        new_file = tmp_path / "debug" / "new_file.log"
        
        # Create the files
        old_file.touch()
        new_file.touch()
        
        # Set modification times (old_file = 2 days ago, new_file = now)
        old_time = now - (2 * 24 * 3600)  # 2 days ago
        os.utime(old_file, (old_time, old_time))
        
        # Configure retention to keep files newer than 1 day
        file_manager.config.config["logging"]["retention"]["delete_older_than_days"] = 1
        
        # Run cleanup
        file_manager.cleanup_old_files()
        
        # Verify old file was deleted, new file was kept
        assert not os.path.exists(old_file)
        assert os.path.exists(new_file)
    
    def test_rotate_logs(self, file_manager, tmp_path):
        """Test log rotation functionality."""
        # Configure log rotation
        file_manager.config.config["logging"]["rotation"]["enabled"] = True
        file_manager.config.config["logging"]["rotation"]["max_size_mb"] = 1  # 1MB
        file_manager.config.config["logging"]["rotation"]["backup_count"] = 2
        
        log_file = tmp_path / "test.log"
        
        # Write enough data to trigger rotation (1.5MB)
        with open(log_file, "w") as f:
            f.write("x" * 1_500_000)  # 1.5MB
        
        # Trigger rotation
        file_manager.rotate_logs(log_file)
        
        # Check that backup was created
        backup_files = list(tmp_path.glob("test.log.*"))
        assert len(backup_files) == 1
        
        # Write more data to trigger another rotation
        with open(log_file, "w") as f:
            f.write("y" * 1_500_000)
        
        file_manager.rotate_logs(log_file)
        
        # Should have 2 backup files now
        backup_files = sorted(tmp_path.glob("test.log.*"))
        assert len(backup_files) == 2
        
        # Write one more time to trigger cleanup of old backups
        with open(log_file, "w") as f:
            f.write("z" * 1_500_000)
        
        file_manager.rotate_logs(log_file)
        
        # Should still have only 2 backups (oldest was deleted)
        backup_files = sorted(tmp_path.glob("test.log.*"))
        assert len(backup_files) == 2
    
    def test_save_payload(self, file_manager, tmp_path):
        """Test saving of payload files."""
        payload = {"key": "value", "timestamp": datetime.now().isoformat()}
        source = "test_source"
        
        # Save payload
        file_manager.save_payload(payload, source, "test_payload")
        
        # Check that file was created in the correct location
        payload_dir = tmp_path / "payloads" / source
        payload_files = list(payload_dir.glob("*.json"))
        assert len(payload_files) == 1
        
        # Check file content
        with open(payload_files[0], "r") as f:
            content = f.read()
            assert "test_payload" in content
    
    def test_cleanup_payloads(self, file_manager, tmp_path):
        """Test cleanup of old payload files."""
        # Create test payloads
        payload_dir = tmp_path / "payloads" / "test_source"
        payload_dir.mkdir(parents=True)
        
        # Create files with different timestamps
        now = time.time()
        for i in range(5):
            file_time = now - (i * 3600)  # 1 hour apart
            file_path = payload_dir / f"payload_{i}.json"
            file_path.touch()
            os.utime(file_path, (file_time, file_time))
        
        # Configure to keep only 3 most recent payloads
        file_manager.config.config["logging"]["retention"]["max_payloads_to_keep"] = 3
        
        # Run cleanup
        file_manager.cleanup_payloads()
        
        # Check that only the 3 most recent files remain
        remaining_files = sorted(payload_dir.glob("*.json"), key=os.path.getmtime)
        assert len(remaining_files) == 3
        
        # The oldest files should have been deleted
        assert "payload_4.json" not in [f.name for f in remaining_files]
        assert "payload_3.json" not in [f.name for f in remaining_files]
        assert "payload_2.json" in [f.name for f in remaining_files]
