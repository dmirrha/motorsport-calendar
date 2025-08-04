"""
Regression tests for iCal generation functionality.
"""
import os
import tempfile
from datetime import datetime, timedelta
import pytest
from icalendar import Calendar

# Import the module to test
from src.ical_generator import ICalGenerator

class TestICalGenerator:
    """Test cases for ICalGenerator."""
    
    @pytest.fixture
    def ical_generator(self, test_config):
        """Create an ICalGenerator instance with test config."""
        return ICalGenerator(test_config)
    
    @pytest.fixture
    def sample_events(self):
        """Sample events for testing iCal generation."""
        return [
            {
                "title": "F1 GP do Brasil - Treino Livre 1",
                "start_time": "2025-11-15T10:30:00-03:00",
                "end_time": "2025-11-15T11:30:00-03:00",
                "category": "formula1",
                "circuit": "Autódromo de Interlagos",
                "location": "São Paulo, Brasil",
                "description": "Primeiro treino livre do GP do Brasil de Fórmula 1",
                "streaming_links": ["https://example.com/stream1"],
                "metadata": {
                    "series": "Fórmula 1",
                    "session_type": "practice",
                    "round": 21,
                    "season": 2025
                }
            },
            {
                "title": "F1 GP do Brasil - Corrida",
                "start_time": "2025-11-16T14:00:00-03:00",
                "end_time": "2025-11-16T16:00:00-03:00",
                "category": "formula1",
                "circuit": "Autódromo de Interlagos",
                "location": "São Paulo, Brasil",
                "description": "Corrida do GP do Brasil de Fórmula 1",
                "streaming_links": ["https://example.com/stream1"],
                "metadata": {
                    "series": "Fórmula 1",
                    "session_type": "race",
                    "round": 21,
                    "season": 2025,
                    "laps": 71,
                    "distance": "305.909 km"
                }
            }
        ]
    
    def test_generate_ical(self, ical_generator, sample_events, temp_output_dir):
        """Test iCal file generation."""
        # Generate iCal file
        output_file = temp_output_dir / "test_calendar.ics"
        ical_generator.generate_ical(sample_events, output_file)
        
        # Verify file was created
        assert os.path.exists(output_file)
        
        # Parse the generated iCal file
        with open(output_file, 'rb') as f:
            cal = Calendar.from_ical(f.read())
        
        # Verify calendar properties
        assert cal.get('X-WR-CALNAME') == "Test Motorsport Events"
        assert cal.get('X-WR-CALDESC') == "Test calendar for regression testing"
        
        # Verify events
        events = [comp for comp in cal.walk() if comp.name == 'VEVENT']
        assert len(events) == len(sample_events)
        
        # Verify first event details
        event = events[0]
        assert str(event.get('summary')) == "F1 GP do Brasil - Treino Livre 1"
        assert "Treino Livre" in str(event.get('description'))
        assert "https://example.com/stream1" in str(event.get('description'))
        assert "Autódromo de Interlagos" in str(event.get('location'))
    
    def test_event_timezone_handling(self, ical_generator, sample_events, temp_output_dir):
        """Test that timezones are correctly handled in iCal generation."""
        output_file = temp_output_dir / "timezone_test.ics"
        ical_generator.generate_ical(sample_events, output_file)
        
        # Parse the generated iCal file
        with open(output_file, 'rb') as f:
            cal = Calendar.from_ical(f.read())
        
        # Check that timezone information is preserved
        event = [comp for comp in cal.walk() if comp.name == 'VEVENT'][0]
        dt_start = event.get('dtstart')
        assert dtstart.dt.hour == 10  # Should be 10:30 AM in São Paulo time
        assert "America/Sao_Paulo" in str(dtstart.params.get('TZID'))
    
    def test_reminders(self, ical_generator, sample_events, temp_output_dir):
        """Test that reminders are correctly added to events."""
        output_file = temp_output_dir / "reminder_test.ics"
        ical_generator.generate_ical(sample_events, output_file)
        
        # Parse the generated iCal file
        with open(output_file, 'rb') as f:
            cal = Calendar.from_ical(f.read())
        
        # Check that reminders are set (60 minutes before)
        event = [comp for comp in cal.walk() if comp.name == 'VEVENT'][0]
        has_reminder = False
        
        for component in event.walk():
            if component.name == 'VALARM':
                has_reminder = True
                assert component.get('TRIGGER;VALUE=DURATION').dt == timedelta(minutes=-60)
                break
                
        assert has_reminder, "No reminder found in the event"
    
    def test_empty_events(self, ical_generator, temp_output_dir):
        """Test behavior with empty event list."""
        output_file = temp_output_dir / "empty_calendar.ics"
        ical_generator.generate_ical([], output_file)
        
        # Should still create a valid iCal file, just with no events
        assert os.path.exists(output_file)
        
        with open(output_file, 'rb') as f:
            cal = Calendar.from_ical(f.read())
        
        # Should have no events
        events = [comp for comp in cal.walk() if comp.name == 'VEVENT']
        assert len(events) == 0
