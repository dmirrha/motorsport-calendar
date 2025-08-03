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
    
    def generate_calendar(self, events: List[Dict[str, Any]], 
                         output_filename: Optional[str] = None) -> str:
        """
        Generate iCal file from events.
        
        Args:
            events: List of processed events
            output_filename: Optional custom output filename
            
        Returns:
            Path to generated iCal file
        """
        if self.logger:
            self.logger.log_step("📅 Generating iCal file")
        
        if self.ui:
            self.ui.show_step("iCal Generation", "Creating calendar file...")
        
        # Initialize generation statistics
        self.generation_stats['generation_start_time'] = datetime.now().isoformat()
        self.generation_stats['events_processed'] = len(events)
        
        if not events:
            if self.logger:
                self.logger.log_warning("No events to add to calendar")
            return ""
        
        # Create calendar
        calendar = self._create_calendar()
        
        # Add events to calendar
        events_added = 0
        events_skipped = 0
        
        for event in events:
            try:
                ical_event = self._create_ical_event(event)
                if ical_event:
                    calendar.add_component(ical_event)
                    events_added += 1
                else:
                    events_skipped += 1
            except Exception as e:
                events_skipped += 1
                if self.logger:
                    self.logger.debug(f"⚠️ Failed to add event '{event.get('name', 'Unknown')}': {e}")
        
        # Update statistics
        self.generation_stats['events_added'] = events_added
        self.generation_stats['events_skipped'] = events_skipped
        
        # Generate output filename
        if not output_filename:
            output_filename = self._generate_filename(events)
        
        # Ensure output directory exists
        os.makedirs(self.output_directory, exist_ok=True)
        
        # Archive old iCal files before generating new one
        self._archive_old_ical_files()
        
        # Write calendar to file
        output_path = os.path.join(self.output_directory, output_filename)
        
        try:
            with open(output_path, 'wb') as f:
                f.write(calendar.to_ical())
            
            self.generation_stats['files_generated'] = 1
            self.generation_stats['output_files'].append(output_path)
            self.generation_stats['generation_end_time'] = datetime.now().isoformat()
            
            # Log success
            self._log_generation_summary(output_path)
            
            if self.ui:
                self.ui.show_step_result("iCal Generation", True, f"Generated: {output_filename}")
            
            return output_path
            
        except Exception as e:
            error_msg = f"Failed to write iCal file: {str(e)}"
            
            if self.logger:
                self.logger.log_error(error_msg)
            
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
            ical_event = Event()
            
            # Required properties
            event_datetime = event.get('datetime')
            if not event_datetime:
                return None
            
            # Event ID
            event_id = event.get('event_id', str(uuid.uuid4())[:16])
            ical_event.add('uid', f"{event_id}@motorsport-calendar")
            
            # Basic event info
            event_name = event.get('name', 'Motorsport Event')
            category = event.get('detected_category', 'Unknown')
            session_type = event.get('session_type', 'race').title()
            
            # Create title
            title = f"{category} - {event_name}"
            if session_type and session_type.lower() != 'race':
                title += f" ({session_type})"
            
            ical_event.add('summary', title)
            
            # Date and time
            ical_event.add('dtstart', event_datetime)
            
            # Calculate end time
            duration = timedelta(minutes=self._get_event_duration(event))
            end_datetime = event_datetime + duration
            ical_event.add('dtend', end_datetime)
            
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
                self.logger.debug(f"⚠️ Failed to create iCal event: {e}")
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
        
        # Basic event info
        category = event.get('detected_category', 'Unknown')
        session_type = event.get('session_type', 'race').title()
        
        description_parts.append(f"🏁 {category} {session_type}")
        
        # Location information
        location = event.get('location')
        country = event.get('country')
        
        if location or country:
            location_info = []
            if location:
                location_info.append(location)
            if country and country != location:
                location_info.append(country)
            
            if location_info:
                description_parts.append(f"📍 {' - '.join(location_info)}")
        
        # Streaming links
        if self.include_streaming_links:
            streaming_links = event.get('streaming_links', [])
            if streaming_links:
                description_parts.append("\n🔴 Streaming:")
                for link in streaming_links[:3]:  # Limit to 3 links
                    description_parts.append(f"• {link}")
        
        # Official URL
        official_url = event.get('official_url')
        if official_url:
            description_parts.append(f"\n🔗 More info: {official_url}")
        
        # Source information
        if self.include_source_info:
            source_display_name = event.get('source_display_name')
            if source_display_name:
                description_parts.append(f"\n📊 Source: {source_display_name}")
        
        # Additional metadata
        confidence = event.get('category_confidence')
        if confidence and confidence < 0.8:
            description_parts.append(f"\n⚠️ Category detection confidence: {confidence:.0%}")
        
        return '\n'.join(description_parts)
    
    def _create_event_location(self, event: Dict[str, Any]) -> Optional[str]:
        """Create event location string."""
        location_parts = []
        
        location = event.get('location')
        country = event.get('country')
        
        if location:
            location_parts.append(location)
        
        if country and country != location:
            location_parts.append(country)
        
        return ', '.join(location_parts) if location_parts else None
    
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
    
    def _add_reminders(self, ical_event: Event) -> None:
        """Add reminder alarms to event."""
        if not self.reminder_minutes:
            return
        
        from icalendar import Alarm
        
        for minutes in self.reminder_minutes:
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('description', 'Motorsport Event Reminder')
            alarm.add('trigger', timedelta(minutes=-minutes))
            
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
                    self.logger.debug(f"📦 Archived old iCal: {filename} → history/{archived_filename}")
                    
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"⚠️ Failed to archive {filename}: {e}")
        
        if moved_count > 0 and self.logger:
            self.logger.debug(f"📦 Archived {moved_count} old iCal file(s) to history/")
    
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
                    self.logger.debug(f"✅ Calendar validation passed: {events_count} events")
                else:
                    self.logger.debug(f"❌ Calendar validation failed: {len(validation_results['errors'])} errors")
            
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
            
            self.logger.debug(f"⏱️ iCal generation completed in {duration:.1f} seconds")
    
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
