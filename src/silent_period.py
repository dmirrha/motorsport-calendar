"""
Silent Period Manager for Motorsport Calendar

Handles configuration and validation of silent periods during which
events are filtered from the iCal output but still logged for monitoring.
"""

import re
from datetime import datetime, time, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pytz


class SilentPeriod:
    """Manages silent periods for event filtering."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        """
        Initialize silent period manager.
        
        Args:
            config: Silent period configuration dictionary
            logger: Logger instance for debugging
        """
        self.logger = logger
        self.enabled = config.get('enabled', False)
        self.name = config.get('name', 'Unnamed Period')
        self.start_time = self._parse_time(config.get('start_time', '00:00'))
        self.end_time = self._parse_time(config.get('end_time', '23:59'))
        self.days_of_week = self._parse_days_of_week(config.get('days_of_week', []))
        
        # Validate configuration
        self._validate_config()
    
    def _parse_time(self, time_str: str) -> time:
        """
        Parse time string to time object.
        
        Args:
            time_str: Time string in HH:MM format
            
        Returns:
            time object
            
        Raises:
            ValueError: If time format is invalid
        """
        if not isinstance(time_str, str):
            raise ValueError(f"Time must be a string, got {type(time_str)}")
        
        # Match HH:MM format
        time_pattern = r'^(\d{1,2}):(\d{2})$'
        match = re.match(time_pattern, time_str.strip())
        
        if not match:
            raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM")
        
        hour, minute = int(match.group(1)), int(match.group(2))
        
        if hour > 23 or minute > 59:
            raise ValueError(f"Invalid time values: {hour}:{minute:02d}")
        
        return time(hour, minute)
    
    def _parse_days_of_week(self, days: List[str]) -> List[int]:
        """
        Parse days of week to weekday numbers.
        
        Args:
            days: List of day names (monday, tuesday, etc.)
            
        Returns:
            List of weekday numbers (0=Monday, 6=Sunday)
        """
        day_mapping = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        weekdays = []
        for day in days:
            day_lower = day.lower().strip()
            if day_lower in day_mapping:
                weekdays.append(day_mapping[day_lower])
            else:
                if self.logger:
                    self.logger.debug(f"⚠️ Invalid day of week: {day}")
        
        return sorted(weekdays)
    
    def _validate_config(self) -> None:
        """Validate silent period configuration."""
        if not self.enabled:
            return
        
        if not self.name:
            raise ValueError("Silent period name cannot be empty")
        
        if not self.days_of_week:
            raise ValueError("At least one day of week must be specified")
        
        # Log configuration for debugging
        if self.logger:
            self.logger.debug(f"🔇 Silent period '{self.name}' configured: "
                            f"{self.start_time}-{self.end_time} on days {self.days_of_week}")
    
    def is_event_in_silent_period(self, event_datetime: datetime) -> bool:
        """
        Check if an event occurs during this silent period.
        
        Args:
            event_datetime: Event datetime to check
            
        Returns:
            True if event is in silent period, False otherwise
        """
        if not self.enabled:
            return False
        
        # Check if event day matches configured days
        event_weekday = event_datetime.weekday()
        if event_weekday not in self.days_of_week:
            return False
        
        # Get event time
        event_time = event_datetime.time()
        
        # Handle periods that cross midnight
        if self.start_time <= self.end_time:
            # Normal period (e.g., 09:00 to 17:00)
            return self.start_time <= event_time <= self.end_time
        else:
            # Period crossing midnight (e.g., 22:00 to 06:00)
            return event_time >= self.start_time or event_time <= self.end_time
    
    def get_description(self) -> str:
        """Get human-readable description of the silent period."""
        if not self.enabled:
            return f"Silent period '{self.name}' (disabled)"
        
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        active_days = [day_names[day] for day in self.days_of_week]
        
        return (f"Silent period '{self.name}': "
                f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')} "
                f"on {', '.join(active_days)}")
    
    def __str__(self) -> str:
        """String representation."""
        return self.get_description()
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"<SilentPeriod(name='{self.name}', enabled={self.enabled}, "
                f"time={self.start_time}-{self.end_time}, days={self.days_of_week})>")


class SilentPeriodManager:
    """Manages multiple silent periods and event filtering."""
    
    def __init__(self, config_manager=None, logger=None):
        """
        Initialize silent period manager.
        
        Args:
            config_manager: Configuration manager instance
            logger: Logger instance
        """
        self.config = config_manager
        self.logger = logger
        self.silent_periods: List[SilentPeriod] = []
        
        # Statistics
        self.stats = {
            'events_checked': 0,
            'events_filtered': 0,
            'periods_active': 0
        }
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load silent periods configuration."""
        if not self.config:
            return
        
        try:
            # Get silent periods configuration
            general_config = self.config.get_general_config()
            silent_config = general_config.get('silent_periods', [])
            
            if not isinstance(silent_config, list):
                if self.logger:
                    self.logger.debug("⚠️ Silent periods config must be a list")
                return
            
            # Create silent period objects
            for period_config in silent_config:
                try:
                    period = SilentPeriod(period_config, self.logger)
                    self.silent_periods.append(period)
                    
                    if period.enabled:
                        self.stats['periods_active'] += 1
                        
                except Exception as e:
                    if self.logger:
                        self.logger.debug(f"⚠️ Invalid silent period config: {e}")
            
            if self.logger and self.silent_periods:
                enabled_count = sum(1 for p in self.silent_periods if p.enabled)
                self.logger.debug(f"🔇 Loaded {len(self.silent_periods)} silent periods "
                                f"({enabled_count} enabled)")
                
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Error loading silent periods config: {e}")
    
    def filter_events(self, events: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filter events based on silent periods.
        
        Args:
            events: List of events to filter
            
        Returns:
            Tuple of (allowed_events, filtered_events)
        """
        if not self.silent_periods or not any(p.enabled for p in self.silent_periods):
            # No active silent periods
            return events, []
        
        allowed_events = []
        filtered_events = []
        
        for event in events:
            self.stats['events_checked'] += 1
            
            # Get event datetime
            event_datetime = event.get('datetime')
            if not event_datetime:
                # No datetime, allow event
                allowed_events.append(event)
                continue
            
            # Check if event is in any silent period
            is_filtered = False
            matching_period = None
            
            for period in self.silent_periods:
                if period.is_event_in_silent_period(event_datetime):
                    is_filtered = True
                    matching_period = period
                    break
            
            if is_filtered:
                # Add metadata about why it was filtered
                filtered_event = event.copy()
                filtered_event['silent_period'] = matching_period.name
                filtered_event['filter_reason'] = f"Event occurs during silent period '{matching_period.name}'"
                
                filtered_events.append(filtered_event)
                self.stats['events_filtered'] += 1
                
                if self.logger:
                    self.logger.info(f"🔇 Event filtered by silent period '{matching_period.name}': "
                                   f"{event.get('name', 'Unknown')} at "
                                   f"{event_datetime.strftime('%Y-%m-%d %H:%M')}")
            else:
                allowed_events.append(event)
        
        return allowed_events, filtered_events
    
    def log_filtering_summary(self, filtered_events: List[Dict[str, Any]]) -> None:
        """
        Log summary of filtered events.
        
        Args:
            filtered_events: List of events that were filtered
        """
        if not self.logger:
            return
        
        if not filtered_events:
            self.logger.debug("🔇 No events filtered by silent periods")
            return
        
        # Group by silent period
        period_counts = {}
        for event in filtered_events:
            period_name = event.get('silent_period', 'Unknown')
            period_counts[period_name] = period_counts.get(period_name, 0) + 1
        
        # Log summary
        total_filtered = len(filtered_events)
        self.logger.info(f"🔇 Silent periods filtered {total_filtered} events:")
        
        for period_name, count in period_counts.items():
            self.logger.info(f"  • {period_name}: {count} events")
        
        # Log individual filtered events at debug level
        for event in filtered_events:
            event_time = event.get('datetime', 'Unknown time')
            if isinstance(event_time, datetime):
                event_time = event_time.strftime('%Y-%m-%d %H:%M')
            
            self.logger.debug(f"    - {event.get('name', 'Unknown')} at {event_time}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get filtering statistics."""
        return self.stats.copy()
    
    def get_active_periods(self) -> List[SilentPeriod]:
        """Get list of active (enabled) silent periods."""
        return [p for p in self.silent_periods if p.enabled]
    
    def __str__(self) -> str:
        """String representation."""
        active_count = len(self.get_active_periods())
        return f"SilentPeriodManager({active_count} active periods)"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"<SilentPeriodManager(periods={len(self.silent_periods)}, active={len(self.get_active_periods())})>"
