"""
Unit tests for Silent Period functionality.

Tests the SilentPeriod and SilentPeriodManager classes to ensure
proper filtering of events during configured silent periods.
"""

import unittest
from datetime import datetime, time
from unittest.mock import Mock, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from silent_period import SilentPeriod, SilentPeriodManager


class TestSilentPeriod(unittest.TestCase):
    """Test cases for SilentPeriod class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = Mock()
    
    def test_silent_period_initialization(self):
        """Test silent period initialization with valid config."""
        config = {
            'enabled': True,
            'name': 'Test Period',
            'start_time': '22:00',
            'end_time': '06:00',
            'days_of_week': ['monday', 'tuesday', 'wednesday']
        }
        
        period = SilentPeriod(config, self.logger)
        
        self.assertTrue(period.enabled)
        self.assertEqual(period.name, 'Test Period')
        self.assertEqual(period.start_time, time(22, 0))
        self.assertEqual(period.end_time, time(6, 0))
        self.assertEqual(period.days_of_week, [0, 1, 2])  # Monday=0, Tuesday=1, Wednesday=2
    
    def test_silent_period_disabled(self):
        """Test disabled silent period."""
        config = {
            'enabled': False,
            'name': 'Disabled Period',
            'start_time': '22:00',
            'end_time': '06:00',
            'days_of_week': ['monday']
        }
        
        period = SilentPeriod(config, self.logger)
        
        # Should not filter any events when disabled
        test_datetime = datetime(2025, 8, 4, 23, 0)  # Monday 23:00
        self.assertFalse(period.is_event_in_silent_period(test_datetime))
    
    def test_time_parsing_valid(self):
        """Test valid time string parsing."""
        config = {
            'enabled': True,
            'name': 'Test',
            'start_time': '09:30',
            'end_time': '17:45',
            'days_of_week': ['monday']
        }
        
        period = SilentPeriod(config, self.logger)
        
        self.assertEqual(period.start_time, time(9, 30))
        self.assertEqual(period.end_time, time(17, 45))
    
    def test_time_parsing_invalid(self):
        """Test invalid time string parsing."""
        config = {
            'enabled': True,
            'name': 'Test',
            'start_time': '25:00',  # Invalid hour
            'end_time': '06:00',
            'days_of_week': ['monday']
        }
        
        with self.assertRaises(ValueError):
            SilentPeriod(config, self.logger)
    
    def test_days_of_week_parsing(self):
        """Test days of week parsing."""
        config = {
            'enabled': True,
            'name': 'Test',
            'start_time': '22:00',
            'end_time': '06:00',
            'days_of_week': ['friday', 'saturday', 'sunday', 'invalid_day']
        }
        
        period = SilentPeriod(config, self.logger)
        
        # Should parse valid days and ignore invalid ones
        self.assertEqual(period.days_of_week, [4, 5, 6])  # Friday=4, Saturday=5, Sunday=6
    
    def test_event_in_normal_period(self):
        """Test event filtering in normal period (not crossing midnight)."""
        config = {
            'enabled': True,
            'name': 'Work Hours',
            'start_time': '09:00',
            'end_time': '17:00',
            'days_of_week': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        }
        
        period = SilentPeriod(config, self.logger)
        
        # Test event during work hours on Monday
        monday_work = datetime(2025, 8, 4, 14, 30)  # Monday 14:30
        self.assertTrue(period.is_event_in_silent_period(monday_work))
        
        # Test event outside work hours on Monday
        monday_evening = datetime(2025, 8, 4, 19, 30)  # Monday 19:30
        self.assertFalse(period.is_event_in_silent_period(monday_evening))
        
        # Test event during work hours on Saturday (not in days_of_week)
        saturday_work = datetime(2025, 8, 9, 14, 30)  # Saturday 14:30
        self.assertFalse(period.is_event_in_silent_period(saturday_work))
    
    def test_event_in_midnight_crossing_period(self):
        """Test event filtering in period crossing midnight."""
        config = {
            'enabled': True,
            'name': 'Night Hours',
            'start_time': '22:00',
            'end_time': '06:00',
            'days_of_week': ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday']
        }
        
        period = SilentPeriod(config, self.logger)
        
        # Test event late at night (after start_time)
        monday_late = datetime(2025, 8, 4, 23, 30)  # Monday 23:30
        self.assertTrue(period.is_event_in_silent_period(monday_late))
        
        # Test event early morning (before end_time)
        monday_early = datetime(2025, 8, 4, 5, 30)  # Monday 05:30
        self.assertTrue(period.is_event_in_silent_period(monday_early))
        
        # Test event during day (between end_time and start_time)
        monday_day = datetime(2025, 8, 4, 14, 30)  # Monday 14:30
        self.assertFalse(period.is_event_in_silent_period(monday_day))
    
    def test_get_description(self):
        """Test human-readable description generation."""
        config = {
            'enabled': True,
            'name': 'Test Period',
            'start_time': '22:00',
            'end_time': '06:00',
            'days_of_week': ['friday', 'saturday', 'sunday']
        }
        
        period = SilentPeriod(config, self.logger)
        description = period.get_description()
        
        self.assertIn('Test Period', description)
        self.assertIn('22:00-06:00', description)
        self.assertIn('Fri, Sat, Sun', description)


class TestSilentPeriodManager(unittest.TestCase):
    """Test cases for SilentPeriodManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = Mock()
        self.config_manager = Mock()
    
    def test_manager_initialization_no_config(self):
        """Test manager initialization without configuration."""
        manager = SilentPeriodManager(None, self.logger)
        
        self.assertEqual(len(manager.silent_periods), 0)
        self.assertEqual(manager.stats['periods_active'], 0)
    
    def test_manager_initialization_with_config(self):
        """Test manager initialization with configuration."""
        # Mock configuration
        self.config_manager.get_general_config.return_value = {
            'silent_periods': [
                {
                    'enabled': True,
                    'name': 'Night',
                    'start_time': '22:00',
                    'end_time': '06:00',
                    'days_of_week': ['monday', 'tuesday']
                },
                {
                    'enabled': False,
                    'name': 'Weekend',
                    'start_time': '00:00',
                    'end_time': '23:59',
                    'days_of_week': ['saturday', 'sunday']
                }
            ]
        }
        
        manager = SilentPeriodManager(self.config_manager, self.logger)
        
        self.assertEqual(len(manager.silent_periods), 2)
        self.assertEqual(manager.stats['periods_active'], 1)  # Only one enabled
    
    def test_filter_events_no_periods(self):
        """Test event filtering with no silent periods."""
        manager = SilentPeriodManager(None, self.logger)
        
        events = [
            {'name': 'Event 1', 'datetime': datetime(2025, 8, 4, 14, 30)},
            {'name': 'Event 2', 'datetime': datetime(2025, 8, 4, 20, 30)}
        ]
        
        allowed, filtered = manager.filter_events(events)
        
        self.assertEqual(len(allowed), 2)
        self.assertEqual(len(filtered), 0)
    
    def test_filter_events_with_periods(self):
        """Test event filtering with active silent periods."""
        # Mock configuration
        self.config_manager.get_general_config.return_value = {
            'silent_periods': [
                {
                    'enabled': True,
                    'name': 'Night',
                    'start_time': '22:00',
                    'end_time': '06:00',
                    'days_of_week': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
                }
            ]
        }
        
        manager = SilentPeriodManager(self.config_manager, self.logger)
        
        events = [
            {'name': 'Day Event', 'datetime': datetime(2025, 8, 4, 14, 30)},  # Monday 14:30
            {'name': 'Night Event', 'datetime': datetime(2025, 8, 4, 23, 30)},  # Monday 23:30
            {'name': 'Weekend Event', 'datetime': datetime(2025, 8, 9, 23, 30)}  # Saturday 23:30
        ]
        
        allowed, filtered = manager.filter_events(events)
        
        self.assertEqual(len(allowed), 2)  # Day Event and Weekend Event
        self.assertEqual(len(filtered), 1)  # Night Event
        self.assertEqual(filtered[0]['name'], 'Night Event')
        self.assertEqual(filtered[0]['silent_period'], 'Night')
    
    def test_filter_events_no_datetime(self):
        """Test event filtering for events without datetime."""
        # Mock configuration
        self.config_manager.get_general_config.return_value = {
            'silent_periods': [
                {
                    'enabled': True,
                    'name': 'Night',
                    'start_time': '22:00',
                    'end_time': '06:00',
                    'days_of_week': ['monday']
                }
            ]
        }
        
        manager = SilentPeriodManager(self.config_manager, self.logger)
        
        events = [
            {'name': 'Event without datetime'},
            {'name': 'Event with None datetime', 'datetime': None}
        ]
        
        allowed, filtered = manager.filter_events(events)
        
        # Events without datetime should be allowed
        self.assertEqual(len(allowed), 2)
        self.assertEqual(len(filtered), 0)
    
    def test_get_active_periods(self):
        """Test getting active periods."""
        # Mock configuration
        self.config_manager.get_general_config.return_value = {
            'silent_periods': [
                {
                    'enabled': True,
                    'name': 'Active Period',
                    'start_time': '22:00',
                    'end_time': '06:00',
                    'days_of_week': ['monday']
                },
                {
                    'enabled': False,
                    'name': 'Inactive Period',
                    'start_time': '00:00',
                    'end_time': '23:59',
                    'days_of_week': ['sunday']
                }
            ]
        }
        
        manager = SilentPeriodManager(self.config_manager, self.logger)
        active_periods = manager.get_active_periods()
        
        self.assertEqual(len(active_periods), 1)
        self.assertEqual(active_periods[0].name, 'Active Period')
    
    def test_statistics(self):
        """Test statistics collection."""
        # Mock configuration
        self.config_manager.get_general_config.return_value = {
            'silent_periods': [
                {
                    'enabled': True,
                    'name': 'Night',
                    'start_time': '22:00',
                    'end_time': '06:00',
                    'days_of_week': ['monday']
                }
            ]
        }
        
        manager = SilentPeriodManager(self.config_manager, self.logger)
        
        events = [
            {'name': 'Day Event', 'datetime': datetime(2025, 8, 4, 14, 30)},  # Monday 14:30
            {'name': 'Night Event', 'datetime': datetime(2025, 8, 4, 23, 30)}  # Monday 23:30
        ]
        
        manager.filter_events(events)
        stats = manager.get_statistics()
        
        self.assertEqual(stats['events_checked'], 2)
        self.assertEqual(stats['events_filtered'], 1)


if __name__ == '__main__':
    unittest.main()
