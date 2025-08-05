"""
iCal Generator for Motorsport Calendar

Generates iCal (.ics) files from processed motorsport events
with configurable parameters and Google Calendar compatibility.
"""

import os
import uuid
import shutil
import glob
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from icalendar import Calendar, Event, vText
import pytz


class ICalGenerator:
    """Generates iCal files from motorsport events."""
    
    def __init__(self, config_manager=None, logger=None, ui_manager=None):
        """
        Initialize iCal generator.
        
        Args:
            config_manager: Configuration manager instance
            logger: Logger instance
            ui_manager: UI manager instance
        """
        self.config = config_manager
        self.logger = logger
        self.ui = ui_manager
        
        # Default iCal settings
        self.calendar_name = "Motorsport Events"
        self.calendar_description = "Weekend motorsport events calendar"
        self.timezone = "America/Sao_Paulo"
        self.default_duration_minutes = 120
        self.reminder_minutes = [30, 60]
        self.include_streaming_links = True
        self.include_source_info = True
        
        # Output settings
        self.output_directory = "output"
        self.filename_template = "motorsport_events_{date}.ics"
        
        # Generation statistics
        self.generation_stats = {
            'events_processed': 0,
            'events_added': 0,
            'events_skipped': 0,
            'files_generated': 0,
            'generation_start_time': None,
            'generation_end_time': None,
            'output_files': []
        }
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load iCal generation configuration."""
        if not self.config:
            return
        
        ical_config = self.config.get_ical_config()
        
        # Calendar settings
        self.calendar_name = ical_config.get('calendar_name', self.calendar_name)
        self.calendar_description = ical_config.get('calendar_description', self.calendar_description)
        self.timezone = ical_config.get('timezone', self.timezone)
        self.default_duration_minutes = ical_config.get('default_duration_minutes', self.default_duration_minutes)
        
        # Reminder settings
        reminders_config = ical_config.get('reminders', [])
        if isinstance(reminders_config, list) and reminders_config:
            # Extract minutes from reminder objects
            self.reminder_minutes = [reminder.get('minutes', 60) for reminder in reminders_config]
        else:
            self.reminder_minutes = []
        
        # Content settings
        self.include_streaming_links = ical_config.get('include_streaming_links', True)
        self.include_source_info = ical_config.get('include_source_info', True)
        
        # Output settings
        output_config = ical_config.get('output', {})
        self.output_directory = output_config.get('directory', self.output_directory)
        self.filename_template = output_config.get('filename_template', self.filename_template)
    
    # Alias for backward compatibility with tests
    def generate_ical(self, events, output_file):
        """
        Alias for generate_calendar to maintain backward compatibility with tests.
        
        Args:
            events: List of events to include in the calendar
            output_file: Path to output file
            
        Returns:
            Path to generated iCal file
        """
        if isinstance(output_file, (str, Path)):
            output_file = Path(output_file)
            # Ensure the output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate the calendar file
        output_path = self.generate_calendar(events, output_file.name if output_file else None)
        
        # If no output path was generated (no events), return empty string
        if not output_path:
            return ""
            
        # If the output file was specified with a different directory, copy the file there
        if output_file and str(output_file.parent) != os.path.dirname(output_path):
            shutil.copy2(output_path, output_file)
            return str(output_file)
            
        return output_path
        
    def generate_ical(self, events: List[Dict[str, Any]], output_filename: Optional[str] = None) -> str:
        """
        Generate iCal file from events.
        
        Args:
            events: List of processed events
            output_filename: Optional custom output filename
            
        Returns:
            Path to generated iCal file or empty string if no events
        """
        if self.logger:
            self.logger.log_info(f"Generating calendar with {len(events)} events")
            self.logger.log_debug(f"Output filename: {output_filename}")
        
        if self.ui:
            self.ui.show_step("iCal Generation", "Creating calendar file...")
        
        # Initialize generation statistics
        self.generation_stats['generation_start_time'] = datetime.now().isoformat()
        self.generation_stats['events_processed'] = len(events)
        
        # Create calendar
        calendar = self._create_calendar()
        
        # Initialize counters
        events_added = 0
        events_skipped = 0
        
        # If no events, log a warning but still create an empty calendar
        if not events:
            if self.logger:
                self.logger.log_warning("No events to add to calendar")
        else:
            if self.logger:
                self.logger.log_debug(f"Processing {len(events)} events...")
                
            # Add events to calendar
            if self.logger:
                self.logger.log_debug(f"Starting to process {len(events)} events...")
                self.logger.log_debug(f"First event data: {events[0] if events else 'No events'}")
                
            for idx, event in enumerate(events, 1):
                try:
                    event_title = event.get('title', event.get('name', 'Untitled'))
                    if self.logger:
                        self.logger.log_debug("\n" + "="*80)
                        self.logger.log_debug(f"🔍 Processing event {idx}/{len(events)}: {event_title}")
                        self.logger.log_debug("📋 Full event data:")
                        for key, value in event.items():
                            self.logger.log_debug(f"   {key}: {value} (type: {type(value)})")
                    
                    # Create the iCal event
                    ical_event = self._create_ical_event(event)
                    
                    if ical_event:
                        try:
                            # Add the event to the calendar
                            calendar.add_component(ical_event)
                            events_added += 1
                            
                            if self.logger:
                                self.logger.log_debug("✅ Successfully added event to calendar")
                                self.logger.log_debug(f"Event UID: {ical_event.get('uid')}")
                                self.logger.log_debug(f"Event SUMMARY: {ical_event.get('summary')}")
                                self.logger.log_debug(f"Event DTSTART: {ical_event.get('dtstart').dt}")
                                self.logger.log_debug(f"Event DTEND: {ical_event.get('dtend').dt}")
                                
                                # Verify the event was added to the calendar
                                event_components = [c for c in calendar.walk('VEVENT')]
                                self.logger.log_debug(f"✅ Calendar now has {len(event_components)} event(s)")
                                
                                # Log the first event in the calendar for verification
                                if event_components:
                                    first_event = event_components[0]
                                    self.logger.log_debug("📅 First event in calendar:")
                                    self.logger.log_debug(f"   UID: {first_event.get('uid')}")
                                    self.logger.log_debug(f"   SUMMARY: {first_event.get('summary')}")
                                    self.logger.log_debug(f"   DTSTART: {first_event.get('dtstart').dt}")
                                    self.logger.log_debug(f"   DTEND: {first_event.get('dtend').dt}")
                                    
                        except Exception as e:
                            events_skipped += 1
                            if self.logger:
                                self.logger.log_error(f"❌ Failed to add event to calendar: {str(e)}")
                                import traceback
                                self.logger.log_debug(f"Traceback: {traceback.format_exc()}")
                    else:
                        events_skipped += 1
                        if self.logger:
                            self.logger.log_warning(f"⚠️ Failed to create iCal event for: {event_title}")
                            self.logger.log_debug(f"Event data that caused the failure: {event}")
                            self.logger.log_debug(f"Event data that failed: {event}")
                            
                            # Log the exact reason why _create_ical_event returned None
                            try:
                                # Try to create the event again with more detailed logging
                                self.logger.log_debug("\n=== DEBUGGING EVENT CREATION FAILURE ===")
                                self._create_ical_event(event)  # This will log more details
                                self.logger.log_debug("=== END DEBUGGING ===\n")
                            except Exception as debug_e:
                                self.logger.log_error(f"❌ Error during debug creation: {str(debug_e)}")
            
                except Exception as e:
                    events_skipped += 1
                    if self.logger:
                        self.logger.log_error(f"❌ Error processing event: {str(e)}")
                    import traceback
                    self.logger.log_debug(f"Traceback: {traceback.format_exc()}")
        
        # Log final statistics
        if self.logger:
            self.logger.log_info(f"Calendar generation complete. Events: {events_added} added, {events_skipped} skipped")
            
            # Log final calendar components
            all_components = [c.name for c in calendar.subcomponents]
            self.logger.log_debug(f"Final calendar components: {all_components}")
            
            # Log all VEVENT components
            event_components = [c for c in calendar.walk('VEVENT')]
            self.logger.log_debug(f"Total VEVENT components: {len(event_components)}")
            for i, evt in enumerate(event_components, 1):
                self.logger.log_debug(f"  Event {i}: UID={evt.get('uid')}, SUMMARY={evt.get('summary')}")
        
        # Update statistics
        self.generation_stats['events_added'] = events_added
        self.generation_stats['events_skipped'] = events_skipped
        self.generation_stats['events_processed'] = len(events)
        
        # Write calendar to file
        output_path = os.path.join(self.output_directory, output_filename)
        
        try:
            if self.logger:
                self.logger.log_debug(f"Writing calendar to file: {output_path}")
                
            ical_content = calendar.to_ical()
            
            if self.logger:
                self.logger.log_debug(f"Generated iCal content (first 500 chars): {str(ical_content)[:500]}...")
            
            with open(output_path, 'wb') as f:
                f.write(ical_content)
            
            if self.logger:
                self.logger.log_info(f"Successfully wrote calendar to {output_path}")
                
                # Verify the file was written correctly
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    self.logger.log_debug(f"Output file exists, size: {file_size} bytes")
                    
                    # Read back the file to verify content
                    with open(output_path, 'rb') as f:
                        content = f.read()
                        self.logger.log_debug(f"Read back {len(content)} bytes from output file")
                        
                    # Try to parse the generated file
                    try:
                        with open(output_path, 'rb') as f:
                            parsed_cal = Calendar.from_ical(f.read())
                            if parsed_cal:
                                parsed_events = [c for c in parsed_cal.walk('VEVENT')]
                                self.logger.log_info(f"Successfully parsed generated iCal file. Found {len(parsed_events)} events.")
                            else:
                                self.logger.log_error("Failed to parse generated iCal file: Calendar is None")
                    except Exception as e:
                        self.logger.log_error(f"Error parsing generated iCal file: {str(e)}")
                else:
                    self.logger.log_error("Output file was not created")
            
            self.generation_stats['files_generated'] = 1
            self.generation_stats['output_files'].append(output_path)
            self.generation_stats['generation_end_time'] = datetime.now().isoformat()
            
            # Log generation summary
            self._log_generation_summary(output_path)
            
            if self.ui:
                self.ui.show_step_result("iCal Generation", True, f"Generated: {output_filename}")
            
            return output_path
            
        except Exception as e:
            error_msg = f"Failed to write iCal file: {str(e)}"
            
            if self.logger:
                self.logger.log_error(error_msg)
                import traceback
                self.logger.log_debug(f"Traceback: {traceback.format_exc()}")
            
            if self.ui:
                self.ui.show_step_result("iCal Generation", False, error_msg)
            
            return ""
    
    def _create_calendar(self) -> Calendar:
        """Create base calendar object."""
        calendar = Calendar()
        
        # Required properties
        calendar.add('prodid', '-//Motorsport Calendar Generator//EN')
        calendar.add('version', '2.0')
        calendar.add('calscale', 'GREGORIAN')
        calendar.add('method', 'PUBLISH')
        
        # Calendar metadata
        calendar.add('x-wr-calname', self.calendar_name)
        calendar.add('x-wr-caldesc', self.calendar_description)
        calendar.add('x-wr-timezone', self.timezone)
        
        # Color (for Google Calendar)
        calendar.add('x-apple-calendar-color', '#FF6B35')  # Orange color for motorsport
        
        return calendar
    
    def _create_ical_event(self, event: Dict[str, Any]) -> Optional[Event]:
        """
        Create iCal event from event data.
        
        Args:
            event: Event dictionary
            
        Returns:
            iCal Event object or None if failed
        """
        try:
            if self.logger:
                self.logger.log_debug("\n" + "="*80)
                self.logger.log_debug(f"🔍 Processing event: {event.get('title', 'Untitled')}")
                self.logger.log_debug(f"📋 Full event data: {event}")
                self.logger.log_debug(f"📋 Event type: {type(event)}")
                self.logger.log_debug(f"📋 Event keys: {list(event.keys())}")
                
                # Log specific fields we'll be using
                for field in ['title', 'start_time', 'end_time', 'category', 'circuit', 'location', 'datetime', 'metadata']:
                    if field in event:
                        self.logger.log_debug(f"📋 {field}: {event[field]} (type: {type(event[field])})")
                    else:
                        self.logger.log_warning(f"⚠️ Missing field in event: {field}")
                        
                # Log the raw event JSON for debugging
                import json
                self.logger.log_debug("📋 Raw event JSON:" + json.dumps(event, default=str, indent=2))
                
                # Log timezone information
                if 'start_time' in event or 'end_time' in event:
                    self.logger.log_debug("⏰ Timezone Info:")
                    if 'start_time' in event:
                        dt = event['start_time']
                        self.logger.log_debug(f"  - Start time: {dt} (type: {type(dt)})")
                        if hasattr(dt, 'tzinfo'):
                            self.logger.log_debug(f"  - Start timezone: {dt.tzinfo}")
                    if 'end_time' in event:
                        dt = event['end_time']
                        self.logger.log_debug(f"  - End time: {dt} (type: {type(dt)})")
                        if hasattr(dt, 'tzinfo'):
                            self.logger.log_debug(f"  - End timezone: {dt.tzinfo}")
            
            # Create a new iCal event
            ical_event = Event()
            if self.logger:
                self.logger.log_debug("✅ Created new iCal Event object")
            
            # Required properties - handle both 'datetime' and 'start_time'/'end_time' formats
            event_datetime = event.get('datetime')
            end_datetime = None
            
            if self.logger:
                self.logger.log_debug(f"🔍 Looking for datetime/start_time in event. Available keys: {list(event.keys())}")
            
            if not event_datetime and 'start_time' in event:
                event_datetime = event['start_time']
                if self.logger:
                    self.logger.log_debug(f"⏰ Using start_time: {event_datetime} (type: {type(event_datetime)})")
                if 'end_time' in event:
                    end_datetime = event['end_time']
                    if self.logger:
                        self.logger.log_debug(f"⏰ Using end_time: {end_datetime} (type: {type(end_datetime)})")
            
            if not event_datetime:
                error_msg = "❌ No datetime or start_time found in event"
                if self.logger:
                    self.logger.log_error(error_msg)
                    self.logger.log_debug(f"Event data that caused the error: {event}")
                return None
                
            # Log the final datetime values we'll be using
            if self.logger:
                self.logger.log_debug("\n" + "="*80)
                self.logger.log_debug("📅 FINAL DATETIME VALUES")
                self.logger.log_debug("="*80)
                self.logger.log_debug(f"  - event_datetime: {event_datetime} (type: {type(event_datetime)})")
                self.logger.log_debug(f"  - end_datetime: {end_datetime} (type: {type(end_datetime) if end_datetime else 'None'})")
                
                # Log the full event data for debugging
                self.logger.log_debug("\n🔍 FULL EVENT DATA")
                self.logger.log_debug("-"*80)
                for key, value in event.items():
                    self.logger.log_debug(f"   {key}: {value} (type: {type(value)})")
                    
                    # Special handling for datetime objects
                    if key in ['start_time', 'end_time', 'datetime'] and hasattr(value, 'strftime'):
                        self.logger.log_debug(f"   {key}_isoformat: {value.isoformat()}")
                        self.logger.log_debug(f"   {key}_tzinfo: {getattr(value, 'tzinfo', 'None')}")
                
                # Log the timezone being used
                self.logger.log_debug("\n⏰ TIMEZONE INFO")
                self.logger.log_debug("-"*80)
                self.logger.log_debug(f"  Using timezone: {self.timezone}")
                
                # Log the calendar object
                self.logger.log_debug("\n📅 CALENDAR INFO")
                self.logger.log_debug("-"*80)
                self.logger.log_debug(f"  Calendar name: {self.calendar_name}")
                self.logger.log_debug(f"  Calendar description: {self.calendar_description}")
                
                # Log event metadata
                self.logger.log_debug("\n📝 EVENT METADATA")
                self.logger.log_debug("-"*80)
                self.logger.log_debug(f"  Title: {event.get('title', 'N/A')}")
                self.logger.log_debug(f"  Location: {event.get('location', 'N/A')}")
                self.logger.log_debug(f"  Description: {event.get('description', 'N/A')}")
                
                # Log datetime info
                self.logger.log_debug("\n🕒 DATETIME INFO")
                self.logger.log_debug("-"*80)
                if 'start_time' in event:
                    dt = event['start_time']
                    self.logger.log_debug(f"  - Start time: {dt} (type: {type(dt)})")
                    if hasattr(dt, 'tzinfo'):
                        self.logger.log_debug(f"  - Start timezone: {dt.tzinfo}")
                if 'end_time' in event:
                    dt = event['end_time']
                    self.logger.log_debug(f"  - End time: {dt} (type: {type(dt)})")
                    if hasattr(dt, 'tzinfo'):
                        self.logger.log_debug(f"  - End timezone: {dt.tzinfo}")
                
                # Log the event creation status
                self.logger.log_debug("\n✅ EVENT CREATION STATUS")
                self.logger.log_debug("-"*80)
                self.logger.log_debug(f"  Event will be created: {bool(event_datetime)}")
                if not event_datetime:
                    self.logger.log_error("❌ No valid datetime found for event")
                    self.logger.log_debug(f"  Event keys: {list(event.keys())}")
                    if 'start_time' in event:
                        self.logger.log_debug(f"  start_time exists but is: {event['start_time']} (type: {type(event['start_time'])})")
                    if 'datetime' in event:
                        self.logger.log_debug(f"  datetime exists but is: {event['datetime']} (type: {type(event['datetime'])})")
            
            # Convert string dates to datetime objects if needed
            from dateutil import parser
            if isinstance(event_datetime, str):
                try:
                    event_datetime = parser.parse(event_datetime)
                    if self.logger:
                        self.logger.log_debug(f"Converted string date to datetime: {event_datetime}")
                except (ValueError, TypeError) as e:
                    if self.logger:
                        self.logger.log_error(f"Failed to parse event datetime: {e}")
                    return None
            
            if end_datetime and isinstance(end_datetime, str):
                try:
                    end_datetime = parser.parse(end_datetime)
                    if self.logger:
                        self.logger.log_debug(f"Converted string end date to datetime: {end_datetime}")
                except (ValueError, TypeError) as e:
                    if self.logger:
                        self.logger.log_warning(f"Failed to parse end datetime, using start + 1 hour: {e}")
                    end_datetime = event_datetime + timedelta(hours=1)
            
            # If we still don't have a valid datetime, try to get it from the event dict
            if not event_datetime and 'start_time' in event:
                if isinstance(event['start_time'], str):
                    try:
                        event_datetime = parser.parse(event['start_time'])
                        if self.logger:
                            self.logger.log_debug(f"Extracted datetime from start_time string: {event_datetime}")
                    except (ValueError, TypeError) as e:
                        if self.logger:
                            self.logger.log_error(f"❌ Failed to parse end_time: {e}")
                        return None
                elif isinstance(end_datetime, datetime):
                    # Ensure end_datetime is timezone-aware
                    if end_datetime.tzinfo is None:
                        end_datetime = end_datetime.replace(tzinfo=pytz.UTC)
                        if self.logger:
                            self.logger.log_debug(f"🔄 Added timezone to end_time: {end_datetime}")
            
            # Event ID
            event_id = event.get('event_id', str(uuid.uuid4())[:16])
            ical_event.add('uid', f"{event_id}@motorsport-calendar")
            
            # Basic event info
            event_name = event.get('name') or event.get('title', 'Motorsport Event')
            category = event.get('category') or event.get('detected_category', 'Unknown')
            session_type = event.get('session_type', 'race').title()
            
            # Create title - use event name directly if available, otherwise format from components
            if 'title' in event:
                title = event['title']
            else:
                title = f"{category} - {event_name}"
                if session_type and session_type.lower() != 'race':
                    title += f" ({session_type})"
            
            ical_event.add('summary', title)
            
            if self.logger:
                self.logger.log_debug(f"📝 Set event title: {title}")
                self.logger.log_debug(f"📝 Event ID: {event_id}")
                self.logger.log_debug(f"📝 Category: {category}, Session Type: {session_type}")
            
            # Date and time
            if self.logger:
                self.logger.log_debug(f"⏰ Setting event start time: {event_datetime}")
                self.logger.log_debug(f"⏰ Setting event end time: {end_datetime if end_datetime else 'None (will calculate from duration)'}")
            
            ical_event.add('dtstart', event_datetime)
            
            # Set end time - use provided end_time or calculate from duration
            if end_datetime:
                ical_event.add('dtend', end_datetime)
            else:
                duration_minutes = self._get_event_duration(event)
                duration = timedelta(minutes=duration_minutes)
                end_datetime = event_datetime + duration
                ical_event.add('dtend', end_datetime)
                
                if self.logger:
                    self.logger.log_debug(f"⏰ Calculated duration: {duration_minutes} minutes")
                    self.logger.log_debug(f"⏰ Calculated end time: {end_datetime}")
            
            if self.logger:
                self.logger.log_debug(f"✅ Successfully set event times: {event_datetime} to {end_datetime}")
            
            # Timestamps
            now = datetime.now(pytz.UTC)
            ical_event.add('dtstamp', now)
            ical_event.add('created', now)
            ical_event.add('last-modified', now)
            
            # Description
            description = self._create_event_description(event)
            if description:
                ical_event.add('description', description)
            
            # Location
            location = self._create_event_location(event)
            if location:
                ical_event.add('location', location)
            
            # Categories
            categories = [category]
            if session_type and session_type.lower() != 'race':
                categories.append(session_type)
            ical_event.add('categories', categories)
            
            # Priority (based on category)
            priority = self._get_event_priority(category)
            ical_event.add('priority', priority)
            
            # Status
            ical_event.add('status', 'CONFIRMED')
            
            # Transparency (show as busy)
            ical_event.add('transp', 'OPAQUE')
            
            # Add reminders
            self._add_reminders(ical_event)
            
            # Custom properties
            ical_event.add('x-motorsport-category', category)
            ical_event.add('x-motorsport-session', session_type)
            
            if event.get('source'):
                ical_event.add('x-motorsport-source', event['source'])
            
            return ical_event
            
        except Exception as e:
            if self.logger:
                self.logger.log_debug(f"⚠️ Failed to create iCal event: {e}")
            return None
    
    def _get_event_duration(self, event: Dict[str, Any]) -> int:
        """Get event duration in minutes."""
        session_type = event.get('session_type', 'race').lower()
        category = event.get('detected_category', '').lower()
        
        # Duration by session type and category
        duration_map = {
            'race': {
                'formula 1': 120,
                'f1': 120,
                'motogp': 90,
                'moto2': 75,
                'moto3': 60,
                'stock car': 90,
                'nascar': 180,
                'indycar': 150,
                'wec': 360,  # 6 hours for endurance
                'default': 120
            },
            'qualifying': {
                'formula 1': 60,
                'f1': 60,
                'motogp': 45,
                'default': 45
            },
            'practice': {
                'default': 90
            },
            'sprint': {
                'default': 60
            }
        }
        
        session_durations = duration_map.get(session_type, duration_map['race'])
        
        if category in session_durations:
            return session_durations[category]
        else:
            return session_durations.get('default', self.default_duration_minutes)
    
    def _create_event_description(self, event: Dict[str, Any]) -> str:
        """Create event description with links and information."""
        description_parts = []
        
        # Add title/description
        if event.get('title'):
            description_parts.append(f"🏁 {event['title']}")
        elif event.get('description'):
            description_parts.append(f"🏁 {event['description']}")
        else:
            description_parts.append("🏁 Unknown Race")
        
        # Add circuit and location
        if event.get('circuit'):
            description_parts.append(f"\n🏟️ {event['circuit']}")
            
        if event.get('location'):
            description_parts.append(f"\n📍 {event['location']}")
            
        # Get metadata
        metadata = event.get('metadata', {})
        
        # Add session type from metadata if available
        if 'session_type' in metadata:
            session_type = metadata['session_type'].capitalize()
            description_parts.append(f"\n\n📋 {session_type}")
        
        # Add streaming links
        if event.get('streaming_links'):
            description_parts.append("\n\n📺 Streaming:")
            for link in event['streaming_links']:
                description_parts.append(f"\n• {link}")
        
        # Add additional metadata
        if metadata:
            description_parts.append("\n\n📊 Detalhes:")
            if 'round' in metadata and 'season' in metadata:
                description_parts.append(f"\n• Rodada: {metadata['round']} da temporada {metadata['season']}")
            if 'laps' in metadata:
                description_parts.append(f"\n• Voltas: {metadata['laps']}")
            if 'distance' in metadata:
                description_parts.append(f"\n• Distância: {metadata['distance']}")
            
            # Add any remaining metadata that wasn't explicitly handled
            handled_keys = {'session_type', 'round', 'season', 'laps', 'distance'}
            for key, value in metadata.items():
                if key not in handled_keys and isinstance(value, (str, int, float, bool)):
                    description_parts.append(f"\n• {key.replace('_', ' ').title()}: {value}")
        
        return "".join(description_parts)
    
    def _create_event_location(self, event: Dict[str, Any]) -> Optional[str]:
        """Create event location string.
        
        Priority order for location:
        1. Circuit name (if available)
        2. Location from event
        3. Country from event
        """
        # First try to get circuit name
        if event.get('circuit'):
            return event['circuit']
            
        # Fall back to location
        location = event.get('location')
        country = event.get('country')
        
        # If we have both location and country, combine them
        if location and country and location != country:
            return f"{location}, {country}"
            
        # Return whichever one we have (or None if neither exists)
        return location or country
    
    def _get_event_priority(self, category: str) -> int:
        """Get event priority based on category (1=highest, 9=lowest)."""
        category_lower = category.lower()
        
        priority_map = {
            'formula 1': 1,
            'f1': 1,
            'motogp': 2,
            'formula 2': 3,
            'f2': 3,
            'moto2': 3,
            'formula 3': 4,
            'f3': 4,
            'moto3': 4,
            'stock car': 3,
            'nascar': 4,
            'indycar': 4,
            'wec': 4,
            'wsbk': 5,
            'wrc': 5,
            'formula e': 5
        }
        
        return priority_map.get(category_lower, 5)  # Default priority
    
    def _add_reminders(self, ical_event: Event, event_data: Dict[str, Any]) -> None:
        """
        Add reminders to an iCal event.
        
        Args:
            ical_event: iCal event to add reminders to
            event_data: Event data containing reminder information
        """
        if not self.reminder_minutes:
            return
            
        for minutes in self.reminder_minutes:
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('trigger', timedelta(minutes=-minutes))
            alarm.add('description', f"Reminder: {event_data.get('title', 'Event')}")
            ical_event.add_component(alarm)
    
    def _archive_old_ical_files(self) -> None:
        """Archive old iCal files to history subfolder."""
        if not os.path.exists(self.output_directory):
            return
        
        # Create history directory
        history_dir = os.path.join(self.output_directory, 'history')
        os.makedirs(history_dir, exist_ok=True)
        
        # Find all .ics files in output directory (excluding history folder)
        ics_pattern = os.path.join(self.output_directory, '*.ics')
        existing_files = glob.glob(ics_pattern)
        
        if not existing_files:
            return
        
        # Sort files by modification time (newest first)
        existing_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Move all files to history folder with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        moved_count = 0
        
        for file_path in existing_files:
            try:
                filename = os.path.basename(file_path)
                # Add timestamp to filename to avoid conflicts
                name, ext = os.path.splitext(filename)
                archived_filename = f"{name}_{timestamp}{ext}"
                archived_path = os.path.join(history_dir, archived_filename)
                
                # Move file to history
                shutil.move(file_path, archived_path)
                moved_count += 1
                
                if self.logger:
                    self.logger.log_debug(f"📦 Archived old iCal: {filename} → history/{archived_filename}")
                    
            except Exception as e:
                if self.logger:
                    self.logger.log_debug(f"⚠️ Failed to archive {filename}: {e}")
        
        if moved_count > 0 and self.logger:
            self.logger.log_debug(f"📦 Archived {moved_count} old iCal file(s) to history/")
    
    def _generate_filename(self, events: List[Dict[str, Any]]) -> str:
        """Generate output filename based on events."""
        # Use the first event's date for filename
        if events:
            first_event = events[0]
            event_date = first_event.get('date', datetime.now().strftime('%Y%m%d'))
            
            # Convert date format if needed
            if isinstance(event_date, str) and '-' in event_date:
                event_date = event_date.replace('-', '')
                
            return self.filename_template.format(date=event_date)
        
        # Fallback to current date
        return self.filename_template.format(date=datetime.now().strftime('%Y%m%d'))
        
    def generate_multiple_calendars(self, events: List[Dict[str, Any]], 
                                  group_by: str = 'category') -> List[str]:
        """
        Generate multiple iCal files grouped by specified criteria.
        
        Args:
            events: List of events
            group_by: Grouping criteria ('category', 'date', 'source')
            
        Returns:
            List of generated file paths
        """
        if self.logger:
            self.logger.log_step(f"📅 Generating multiple iCal files grouped by {group_by}")
        
        # Group events
        event_groups = self._group_events(events, group_by)
        
        generated_files = []
        
        for group_name, group_events in event_groups.items():
            # Create filename for this group
            safe_group_name = self._sanitize_filename(group_name)
            filename = f"motorsport_{group_by}_{safe_group_name}_{datetime.now().strftime('%Y%m%d')}.ics"
            
            # Generate calendar for this group
            output_path = self.generate_calendar(group_events, filename)
            if output_path:
                generated_files.append(output_path)
        
        return generated_files
    
    def _group_events(self, events: List[Dict[str, Any]], group_by: str) -> Dict[str, List[Dict[str, Any]]]:
        """Group events by specified criteria."""
        groups = {}
        
        for event in events:
            if group_by == 'category':
                key = event.get('detected_category', 'Unknown')
            elif group_by == 'date':
                event_datetime = event.get('datetime')
                key = event_datetime.strftime('%Y-%m-%d') if event_datetime else 'Unknown'
            elif group_by == 'source':
                key = event.get('source_display_name', 'Unknown')
            else:
                key = 'All Events'
            
            if key not in groups:
                groups[key] = []
            groups[key].append(event)
        
        return groups
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        import re
        
        # Replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove extra spaces and convert to lowercase
        filename = re.sub(r'\s+', '_', filename.strip()).lower()
        
        # Limit length
        if len(filename) > 50:
            filename = filename[:50]
        
        return filename
    
    def validate_calendar(self, calendar_path: str) -> Dict[str, Any]:
        """
        Validate generated iCal file.
        
        Args:
            calendar_path: Path to iCal file
            
        Returns:
            Validation results dictionary
        """
        validation_results = {
            'valid': False,
            'events_count': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            with open(calendar_path, 'rb') as f:
                calendar_data = f.read()
            
            # Parse calendar
            calendar = Calendar.from_ical(calendar_data)
            
            events_count = 0
            for component in calendar.walk():
                if component.name == "VEVENT":
                    events_count += 1
                    
                    # Validate required properties
                    required_props = ['uid', 'dtstart', 'summary']
                    for prop in required_props:
                        if prop not in component:
                            validation_results['errors'].append(
                                f"Event missing required property: {prop}"
                            )
            
            validation_results['events_count'] = events_count
            validation_results['valid'] = len(validation_results['errors']) == 0
            
            if self.logger:
                if validation_results['valid']:
                    self.logger.log_debug(f"✅ Calendar validation passed: {events_count} events")
                else:
                    self.logger.log_debug(f"❌ Calendar validation failed: {len(validation_results['errors'])} errors")
            
        except Exception as e:
            validation_results['errors'].append(f"Failed to parse calendar: {str(e)}")
        
        return validation_results
    
    def _log_generation_summary(self, output_path: str) -> None:
        """Log generation summary."""
        if not self.logger:
            return
        
        stats = self.generation_stats
        
        self.logger.log_success(
            f"📅 iCal file generated: {os.path.basename(output_path)} "
            f"({stats['events_added']} events added, {stats['events_skipped']} skipped)"
        )
        
        # Calculate generation time
        if stats['generation_start_time'] and stats['generation_end_time']:
            start_time = datetime.fromisoformat(stats['generation_start_time'])
            end_time = datetime.fromisoformat(stats['generation_end_time'])
            duration = (end_time - start_time).total_seconds()
            
            self.logger.log_debug(f"⏱️ iCal generation completed in {duration:.1f} seconds")
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get detailed generation statistics."""
        return self.generation_stats.copy()
    
    def cleanup(self) -> None:
        """Clean up temporary resources."""
        pass
    
    def __str__(self) -> str:
        """String representation."""
        return f"ICalGenerator(calendar='{self.calendar_name}')"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"<ICalGenerator(output_dir='{self.output_directory}', timezone='{self.timezone}')>"
