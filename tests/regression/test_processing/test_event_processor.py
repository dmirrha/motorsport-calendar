"""
Regression tests for event processing functionality.
"""
import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time

# Import the module to test
from src.motorsport_calendar.event_processor import EventProcessor

class TestEventProcessor:
    """Test cases for EventProcessor."""
    
    @pytest.fixture
    def processor(self, test_config):
        """Create an EventProcessor instance with test config."""
        return EventProcessor(test_config)
    
    @pytest.fixture
    def sample_events(self):
        """Sample events for testing."""
        return [
            {
                "title": "F1 GP do Brasil - Treino Livre 1",
                "start_time": "2025-11-15T10:30:00-03:00",
                "end_time": "2025-11-15T11:30:00-03:00",
                "category": "formula1",
                "circuit": "Autódromo de Interlagos",
                "location": "São Paulo, Brasil",
                "metadata": {"session_type": "practice"}
            },
            {
                "title": "F1 GP do Brasil - Qualificação",
                "start_time": "2025-11-15T14:00:00-03:00",
                "end_time": "2025-11-15T15:00:00-03:00",
                "category": "formula1",
                "circuit": "Autódromo de Interlagos",
                "location": "São Paulo, Brasil",
                "metadata": {"session_type": "qualifying"}
            },
            {
                "title": "F1 GP do Brasil - Corrida",
                "start_time": "2025-11-16T14:00:00-03:00",
                "end_time": "2025-11-16T16:00:00-03:00",
                "category": "formula1",
                "circuit": "Autódromo de Interlagos",
                "location": "São Paulo, Brasil",
                "metadata": {"session_type": "race"}
            }
        ]
    
    def test_filter_events_by_category(self, processor, sample_events):
        """Test filtering events by category."""
        # Filter for formula1 events
        filtered = processor.filter_events_by_category(sample_events, ["formula1"])
        assert len(filtered) == 3
        
        # Filter for non-existent category
        filtered = processor.filter_events_by_category(sample_events, ["indycar"])
        assert len(filtered) == 0
    
    @freeze_time("2025-11-14T12:00:00-03:00")  # Friday before the race weekend
    def test_filter_weekend_events(self, processor, sample_events):
        """Test filtering events for the current weekend."""
        # Should include all events from the weekend
        filtered = processor.filter_weekend_events(sample_events)
        assert len(filtered) == 3
        
        # Add an event from a different weekend
        next_week_event = {
            "title": "F1 GP de Abu Dhabi - Treino Livre 1",
            "start_time": "2025-12-05T10:30:00+04:00",
            "end_time": "2025-12-05T11:30:00+04:00",
            "category": "formula1",
            "metadata": {"session_type": "practice"}
        }
        all_events = sample_events + [next_week_event]
        
        filtered = processor.filter_weekend_events(all_events)
        assert len(filtered) == 3  # Should only include Brazil weekend events
    
    def test_apply_timezone(self, processor, sample_events):
        """Test timezone conversion for events."""
        # Convert to UTC
        converted = processor.apply_timezone(sample_events, "UTC")
        
        # Check that times were converted correctly (-3h from São Paulo to UTC)
        assert converted[0]["start_time"].endswith("13:30:00+00:00")  # 10:30-03:00 -> 13:30Z
        
        # Check that original timezone is preserved in metadata
        assert converted[0]["metadata"]["original_timezone"] == "America/Sao_Paulo"
    
    def test_detect_duplicates(self, processor, sample_events):
        """Test detection of duplicate events."""
        # Create a duplicate event
        duplicate = sample_events[0].copy()
        events_with_duplicate = sample_events + [duplicate]
        
        # Should detect and remove the duplicate
        deduplicated = processor.deduplicate_events(events_with_duplicate)
        assert len(deduplicated) == len(sample_events)
    
    def test_apply_silent_periods(self, processor, sample_events):
        """Test application of silent periods to events."""
        # Add a silent period during the race
        silent_periods = [
            {
                "start": "2025-11-16T15:00:00-03:00",
                "end": "2025-11-16T15:30:00-03:00",
                "reason": "Commercial break"
            }
        ]
        
        # Apply silent periods
        processed = processor.apply_silent_periods(sample_events, silent_periods)
        
        # Check that the race event was split
        race_events = [e for e in processed if e["title"] == "F1 GP do Brasil - Corrida"]
        assert len(race_events) == 2  # Should be split into two events
        
        # Check that the silent period is properly marked
        assert any("silent_period" in e["metadata"] for e in race_events)
