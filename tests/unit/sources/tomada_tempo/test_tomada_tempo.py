#!/usr/bin/env python3
"""
Tests for TomadaTempoSource
"""

import unittest
from datetime import datetime, timedelta

from sources.tomada_tempo import TomadaTempoSource

class TestTomadaTempoSource(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.source = TomadaTempoSource()
    
    def test_extract_date(self):
        """Test date extraction from text."""
        # Test DD/MM/YYYY format
        date_str = self.source._extract_date("Corrida de Fórmula 1 em 01/08/2025")
        self.assertEqual(date_str, "01/08/2025")
        
        # Test DD-MM-YYYY format
        date_str = self.source._extract_date("Evento em 02-08-2025")
        self.assertEqual(date_str, "02/08/2025")
        
        # Test DD/MM/YY format
        date_str = self.source._extract_date("Corrida em 03/08/25")
        self.assertEqual(date_str, "03/08/2025")
    
    def test_extract_time(self):
        """Test time extraction from text."""
        # Test HH:MM format
        time_str = self.source._extract_time("Corrida às 16:30")
        self.assertEqual(time_str, "16:30")
        
        # Test HHhMM format
        time_str = self.source._extract_time("Evento às 19h00")
        self.assertEqual(time_str, "19:00")
    
    def test_get_next_weekend(self):
        """Test calculation of next weekend dates."""
        # Test when today is Wednesday (weekday 2)
        # Next Friday should be in 2 days
        next_friday = self.source._get_next_weekend()
        today = datetime.now()
        expected_friday = today + timedelta(days=(4 - today.weekday()) % 7)
        self.assertEqual(next_friday.weekday(), 4)  # Friday
    
    def test_filter_weekend_events(self):
        """Test filtering of weekend events."""
        # Create test events
        events = [
            {
                'name': 'F1 Test Event',
                'date': '01/08/2025',
                'time': '16:30',
                'category': 'F1',
                'location': 'Interlagos'
            },
            {
                'name': 'NASCAR Test Event',
                'date': '02/08/2025',
                'time': '14:00',
                'category': 'NASCAR',
                'location': 'Tarumã'
            },
            {
                'name': 'MotoGP Test Event',
                'date': '10/08/2025',  # This date is not in the current weekend
                'time': '15:00',
                'category': 'MotoGP',
                'location': 'Mônaco'
            }
        ]
        
        # Filter events for current weekend (01/08/2025 is a Friday)
        # Calculate current weekend range to exclude future events
        import pytz
        from datetime import timedelta
        
        tz = pytz.timezone('America/Sao_Paulo')
        # Use fixed Friday (01/08/2025) to make the test deterministic
        from datetime import datetime as _dt
        target_date = tz.localize(_dt.strptime('01/08/2025', '%d/%m/%Y'))
        
        # Ensure target_date has timezone
        if target_date.tzinfo is None:
            target_date = tz.localize(target_date)
        
        weekend_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        weekend_end = weekend_start + timedelta(days=2, hours=23, minutes=59, seconds=59)
        target_weekend = (weekend_start, weekend_end)
        
        weekend_events = self.source.filter_weekend_events(events, target_weekend)
        
        # Should only include events from the current weekend (01/08 and 02/08), excluding 10/08
        self.assertEqual(len(weekend_events), 2)
        self.assertEqual(weekend_events[0]['name'], 'F1 Test Event')
        self.assertEqual(weekend_events[1]['name'], 'NASCAR Test Event')
    
    def test_timezone_handling(self):
        """Test timezone handling in date parsing."""
        # Test with America/Sao_Paulo timezone
        date_time = self.source.parse_date_time('01/08/2025', '16:30', 'America/Sao_Paulo')
        self.assertIsNotNone(date_time)

if __name__ == '__main__':
    unittest.main()
