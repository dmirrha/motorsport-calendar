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
    def test_fetch_events_success(self, mock_get, tomada_source, test_data_dir):
        """Test successful event fetching from Tomada de Tempo."""
        # Mock the response
        mock_response = MagicMock()
        with open(test_data_dir / "tomada_tempo_sample.html", "r") as f:
            mock_response.text = f.read()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Fetch events
        events = tomada_source.fetch_events()
        
        # Verify results
        assert isinstance(events, list)
        assert len(events) > 0
        assert all('title' in event and 'start_time' in event for event in events)
    
    @patch('sources.tomada_tempo.requests.get')
    def test_fetch_events_http_error(self, mock_get, tomada_source):
        """Test handling of HTTP errors during event fetching."""
        # Mock HTTP error
        mock_get.side_effect = Exception("Connection error")
        
        # Test that the error is properly handled
        events = tomada_source.fetch_events()
        assert events == []
    
    def test_parse_event_date(self, tomada_source):
        """Test date parsing from various formats."""
        test_cases = [
            ("Sáb, 15/11 - 14:00", datetime(2025, 11, 15, 14, 0)),
            ("Dom, 16/11 - 15:30", datetime(2025, 11, 16, 15, 30)),
        ]
        
        for date_str, expected in test_cases:
            result = tomada_source._parse_event_date(date_str)
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
        assert event["title"] == "F1 GP do Brasil - Qualificação"
        assert event["category"] == "formula1"
        assert event["circuit"] == "Autódromo de Interlagos"
        assert event["location"] == "São Paulo, Brasil"
        assert "start_time" in event
        assert "end_time" in event

    def test_retry_mechanism(self, tomada_source):
        """Test retry mechanism on temporary failures."""
        # Mock the session's request method
        with patch.object(tomada_source.session, 'request') as mock_request:
            # Mock first request to fail, second to succeed
            mock_request.side_effect = [
                Exception("Temporary failure"),
                MagicMock(status_code=200, text="<html></html>")
            ]
            
            events = tomada_source.fetch_events()
            assert mock_request.call_count == 2
            assert events == []  # Empty because our mock returns no events
