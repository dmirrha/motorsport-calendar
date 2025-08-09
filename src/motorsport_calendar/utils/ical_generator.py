"""
iCal Generator Utilities

Provides a simplified interface for generating iCal files from motorsport events.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from icalendar import Calendar, Event
import pytz

def generate_ical(events: List[Dict[str, Any]], 
                output_path: str, 
                calendar_name: str = "Motorsport Calendar",
                timezone: str = "UTC") -> str:
    """
    Generate an iCal file from a list of events.
    
    Args:
        events: List of event dictionaries
        output_path: Path where the .ics file will be saved
        calendar_name: Name of the calendar
        timezone: Timezone for the calendar events
        
    Returns:
        Path to the generated .ics file
    """
    # Create a new calendar
    cal = Calendar()
    cal.add('prodid', '-//Motorsport Calendar//')
    cal.add('version', '2.0')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', calendar_name)
    cal.add('x-wr-timezone', timezone)
    
    # Add events to the calendar
    for event in events:
        cal_event = Event()
        
        # Required fields
        cal_event.add('summary', event.get('title', 'No Title'))
        cal_event.add('dtstart', _parse_datetime(event.get('start_time'), timezone))
        
        # Optional fields with defaults
        if 'end_time' in event:
            cal_event.add('dtend', _parse_datetime(event['end_time'], timezone))
        
        if 'description' in event:
            cal_event.add('description', event['description'])
            
        if 'location' in event:
            cal_event.add('location', event['location'])
            
        # Add UID if not present
        if 'uid' not in event:
            cal_event.add('uid', f"{event.get('start_time', '')}@{calendar_name}.motorsport")
        
        cal.add_component(cal_event)
    
    # Ensure output directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to file
    with open(output_path, 'wb') as f:
        f.write(cal.to_ical())
    
    return str(output_path)

def _parse_datetime(dt_str: str, timezone: str) -> datetime:
    """Parse a datetime string with timezone support."""
    if not dt_str:
        raise ValueError("Datetime string cannot be empty")
    
    # Try parsing with timezone first
    try:
        # If it already has timezone info
        if 'T' in dt_str and ('+' in dt_str or '-' in dt_str[-6:]):
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        # If it's a naive datetime, apply the specified timezone
        else:
            dt = datetime.fromisoformat(dt_str)
            tz = pytz.timezone(timezone)
            dt = tz.localize(dt)
    except ValueError as e:
        raise ValueError(f"Failed to parse datetime: {dt_str}") from e
    
    return dt
