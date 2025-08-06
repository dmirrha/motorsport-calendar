"""
Regression tests for iCal generation functionality.
"""
import os
import tempfile
from datetime import datetime, timedelta
import pytest
from icalendar import Calendar

# Import the module to test
from motorsport_calendar.ical_generator import ICalGenerator

class TestICalGenerator:
    """Test cases for ICalGenerator."""
    
    @pytest.fixture
    def ical_generator(self, test_config, tmp_path):
        """Create an ICalGenerator instance with test config and debug logging."""
        # Enable debug logging for tests
        from motorsport_calendar.logger import Logger
        from motorsport_calendar.config_manager import ConfigManager
        
        # Create a minimal config for the logger
        logger_config = {
            "general": {
                "timezone": "America/Sao_Paulo",
                "output_directory": str(tmp_path)
            },
            "logging": {
                "directory": str(tmp_path / "logs"),
                "levels": {
                    "file": "DEBUG",
                    "console": "DEBUG"
                },
                "rotation": {
                    "enabled": False
                }
            }
        }
        
        # Create a config manager with our test config
        config_manager = ConfigManager()
        config_manager.config = logger_config
        
        # Initialize logger with the config manager
        logger = Logger(config_manager)
        
        # Create ICalGenerator with debug logging
        ical_gen = ICalGenerator(test_config)
        ical_gen.logger = logger
        
        # Log test config
        logger.log_info("Starting iCal generator test with config:")
        logger.log_info(f"Output directory: {test_config.get('general', 'output_directory')}")
        
        return ical_gen
    
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
        print(f"\n{'='*80}")
        print(f"Starting test_generate_ical with output file: {output_file}")
        print(f"Sample events: {sample_events}")
        
        # Generate the calendar
        result = ical_generator.generate_ical(sample_events, output_file)
        print(f"generate_ical returned: {result}")
        
        # Verify file was created
        assert os.path.exists(output_file), f"Output file {output_file} was not created"
        print(f"Output file exists: {os.path.exists(output_file)}")
        
        # Read and parse the generated iCal file
        with open(output_file, 'rb') as f:
            ical_content = f.read()
            print(f"\nGenerated iCal content (first 500 chars):\n{ical_content[:500].decode('utf-8', errors='replace')}...")
            cal = Calendar.from_ical(ical_content)
        
        # Verify calendar properties
        print("\nVerifying calendar properties...")
        assert cal is not None, "Failed to parse iCal content"
        print(f"Calendar properties: {dict(cal.items())}")
        
        assert cal.get('X-WR-CALNAME') == "Test Motorsport Events", \
            f"Unexpected calendar name: {cal.get('X-WR-CALNAME')}"
        assert cal.get('X-WR-CALDESC') == "Test calendar for regression testing", \
            f"Unexpected calendar description: {cal.get('X-WR-CALDESC')}"
        
        # Verify events
        events = [comp for comp in cal.walk() if comp.name == 'VEVENT']
        print(f"\nFound {len(events)} events in calendar (expected {len(sample_events)})")
        
        # Debug: Print all components in the calendar
        print("\nAll components in calendar:")
        for i, comp in enumerate(cal.walk()):
            print(f"{i}. {comp.name}: {dict(comp.items())}")
        
        assert len(events) == len(sample_events), \
            f"Expected {len(sample_events)} events, found {len(events)}"
        
        # Verify first event details
        if events:
            event = events[0]
            print(f"\nFirst event details: {dict(event.items())}")
            
            summary = str(event.get('summary', ''))
            description = str(event.get('description', ''))
            location = str(event.get('location', ''))
            
            print(f"Summary: {summary}")
            print(f"Description: {description}")
            print(f"Location: {location}")
            
            assert "F1 GP do Brasil - Treino Livre 1" in summary, \
                f"Unexpected event summary: {summary}"
            assert "Treino Livre" in description, \
                f"Expected 'Treino Livre' in description: {description}"
            assert "https://example.com/stream1" in description, \
                f"Expected streaming link in description: {description}"
            assert "Autódromo de Interlagos" in location, \
                f"Expected location 'Autódromo de Interlagos' in: {location}"
        else:
            print("\nNo events found in the generated calendar")
    
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
        assert dt_start.dt.hour == 10  # Should be 10:30 AM in São Paulo time
        assert "America/Sao_Paulo" in str(dt_start.params.get('TZID'))
    
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
