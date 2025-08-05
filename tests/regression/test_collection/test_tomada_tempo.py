"""
Regression tests for Tomada de Tempo event collection.
"""
import pytest
from unittest.mock import patch, MagicMock
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

    def test_retry_mechanism(self, tomada_source):
        """Test retry mechanism on temporary failures."""
        # Mock the session's request method
        with patch.object(tomada_source, '_make_request_with_retry') as mock_request:
            # Mock first request to fail, second to succeed
            mock_request.side_effect = [
                Exception("Temporary failure"),
                MagicMock(status_code=200, text="<html></html>")
            ]
            
            # The method should raise an exception after all retries
            with pytest.raises(Exception):
                tomada_source.collect_events()
            
            # Verify retry was attempted
            assert mock_request.call_count > 1
