"""
Regression tests for Tomada de Tempo event collection.
"""
import logging
import pytest
import requests
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta
from pathlib import Path

# Import the module to test
from sources.tomada_tempo import TomadaTempoSource

class TestTomadaTempoSource:
    """Test cases for TomadaTempoSource."""
    
    @pytest.fixture
    def tomada_source(self, test_config):
        """Create a TomadaTempoSource instance with test config."""
        return TomadaTempoSource(test_config)
    
    @patch('sources.tomada_tempo.requests.get')
    def test_collect_events_success(self, mock_get, tomada_source, test_data_dir):
        """Test successful event collection from Tomada de Tempo."""
        # Mock the response
        mock_response = MagicMock()
        with open(test_data_dir / "tomada_tempo_sample.html", "r") as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Collect events
        events = tomada_source.collect_events()
        
        # Verify results
        assert isinstance(events, list)
        # Check for either 'title' or 'name' as both are used in the implementation
        assert len(events) > 0
        assert all(('title' in event or 'name' in event) and 'start_time' in event for event in events)
    
    @patch('sources.tomada_tempo.requests.get')
    def test_collect_events_http_error(self, mock_get, tomada_source):
        """Test handling of HTTP errors during event collection."""
        # Mock HTTP error
        mock_get.side_effect = Exception("Connection error")
        
        # Test that the error is properly handled
        with pytest.raises(Exception):
            tomada_source.collect_events()
    
    def test_parse_event_date(self, tomada_source):
        """Test date parsing from various formats."""
        # Set a fixed base date for consistent testing
        base_date = datetime(2025, 1, 1)  # Any date will work as we're not testing year handling here
        
        test_cases = [
            ("Sáb, 15/11 - 14:00", datetime(2025, 11, 15, 14, 0)),
            ("Dom, 16/11 - 15:30", datetime(2025, 11, 16, 15, 30)),
            ("14:00", None),  # Handle missing date part
            ("", None),       # Handle empty string
            (None, None),      # Handle None input
        ]
        
        for date_str, expected in test_cases:
            result = tomada_source._parse_event_date(date_str, base_date)
            assert result == expected, f"Failed to parse: {date_str}"
    
    def test_extract_event_info(self, tomada_source):
        """Test extraction of event information from HTML."""
        html = """
        <div class="event">
            <div class="event-time">Sáb, 15/11 - 14:00</div>
            <div class="event-title">F1 GP do Brasil - Qualificação</div>
            <div class="event-category">Fórmula 1</div>
            <div class="event-circuit">Autódromo de Interlagos</div>
            <div class="event-location">São Paulo, Brasil</div>
        </div>
        """
        
        event = tomada_source._extract_event_info(html)
        
        # Check that either 'title' or 'name' is present
        assert 'title' in event or 'name' in event, "Event must have either 'title' or 'name'"
        
        # Get the title/name for assertions
        title = event.get('title') or event.get('name', '')
        
        assert title == "F1 GP do Brasil - Qualificação"
        assert event.get("category") == "formula1"
        assert event.get("circuit") == "Autódromo de Interlagos"
        assert event.get("location") == "São Paulo, Brasil"
        assert "start_time" in event
        
        # end_time should be set either explicitly or calculated from start_time
        assert "end_time" in event

    @patch('sources.base_source.requests.Session')
    def test_retry_mechanism(self, mock_session_class, test_config, caplog):
        """Test retry mechanism on temporary failures."""
        # Create a mock session instance
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Create a mock response that will raise an exception
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.RequestException("Test connection error")
        mock_session.request.return_value = mock_response
        
        # Create a new instance of TomadaTempoSource with the mocked session
        from sources.tomada_tempo import TomadaTempoSource
        source = TomadaTempoSource(test_config)
        
        # Clear any existing log handlers
        if source.logger and hasattr(source.logger, 'handlers'):
            source.logger.handlers.clear()
        
        # Add a test handler to capture logs
        test_handler = logging.StreamHandler()
        test_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        test_handler.setFormatter(formatter)
        
        if source.logger:
            source.logger.addHandler(test_handler)
        
        # Run the method that should trigger the retry logic
        with caplog.at_level(logging.DEBUG):
            result = source.collect_events()
        
        # Verify the result is an empty list (since all requests failed)
        assert result == []
        
        # Verify the request was made multiple times (retry attempts)
        # We expect 4 calls (2 for weekend programming + 2 for general calendar)
        # Each with 1 initial attempt + 1 retry (2 retry_attempts - 1)
        assert mock_session.request.call_count == 4, \
            f"Expected exactly 4 requests (2 attempts for each of 2 URLs), got {mock_session.request.call_count}"
        
        # Get all log messages for debugging
        all_logs = [f"{record.levelname}: {record.message}" for record in caplog.records]
        
        # Check for error messages in debug logs (since that's where they're being logged)
        debug_logs = [record.message for record in caplog.records if record.levelno == logging.DEBUG]
        
        # Verify we have the expected error messages in debug logs
        assert any("Error collecting from weekend programming" in msg for msg in debug_logs), \
            "Missing error log for weekend programming"
        assert any("Error collecting from calendar" in msg for msg in debug_logs), \
            "Missing error log for calendar"
        
        # Check for retry-related log messages
        assert any("attempt 1/2" in msg for msg in debug_logs), "Missing attempt 1 log"
        assert any("attempt 2/2" in msg for msg in debug_logs), "Missing attempt 2 log"
        
        # Verify the number of retry attempts was logged
        assert any("Request failed (attempt 2/2)" in msg for msg in debug_logs), \
            "Missing final retry attempt log"
