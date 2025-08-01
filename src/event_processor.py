"""
Event Processor for Motorsport Calendar

Handles event normalization, deduplication, weekend detection,
and data quality validation for collected motorsport events.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import defaultdict
import hashlib
from fuzzywuzzy import fuzz
from unidecode import unidecode


class EventProcessor:
    """Processes and normalizes motorsport events from multiple sources."""
    
    def __init__(self, config_manager=None, logger=None, ui_manager=None, category_detector=None):
        """
        Initialize event processor.
        
        Args:
            config_manager: Configuration manager instance
            logger: Logger instance
            ui_manager: UI manager instance
            category_detector: Category detector instance
        """
        self.config = config_manager
        self.logger = logger
        self.ui = ui_manager
        self.category_detector = category_detector
        
        # Deduplication settings
        self.similarity_threshold = 85
        self.time_tolerance_minutes = 30
        self.location_similarity_threshold = 80
        self.category_similarity_threshold = 90
        
        # Weekend detection settings
        self.weekend_start_day = 4  # Friday = 4
        self.weekend_end_day = 6    # Sunday = 6
        self.extend_weekend_hours = 6  # Hours to extend weekend boundaries
        
        # Processing statistics
        self.processing_stats = {
            'events_input': 0,
            'events_normalized': 0,
            'events_deduplicated': 0,
            'events_weekend_filtered': 0,
            'events_validated': 0,
            'duplicates_removed': 0,
            'categories_detected': 0,
            'processing_start_time': None,
            'processing_end_time': None
        }
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load event processing configuration."""
        if not self.config:
            return
        
        dedup_config = self.config.get_deduplication_config()
        
        self.similarity_threshold = dedup_config.get('similarity_threshold', 85)
        self.time_tolerance_minutes = dedup_config.get('time_tolerance_minutes', 30)
        self.location_similarity_threshold = dedup_config.get('location_similarity_threshold', 80)
        self.category_similarity_threshold = dedup_config.get('category_similarity_threshold', 90)
        
        # Weekend settings
        general_config = self.config.get_general_config()
        weekend_config = general_config.get('weekend_detection', {})
        
        self.weekend_start_day = weekend_config.get('start_day', 4)  # Friday
        self.weekend_end_day = weekend_config.get('end_day', 6)      # Sunday
        self.extend_weekend_hours = weekend_config.get('extend_hours', 6)
    
    def process_events(self, raw_events: List[Dict[str, Any]], 
                      target_weekend: Optional[Tuple[datetime, datetime]] = None) -> List[Dict[str, Any]]:
        """
        Process raw events through the complete pipeline.
        
        Args:
            raw_events: List of raw events from data collection
            target_weekend: Optional target weekend tuple (start, end)
            
        Returns:
            List of processed, normalized, and deduplicated events
        """
        if self.logger:
            self.logger.log_step("🔄 Processing collected events")
        
        if self.ui:
            self.ui.show_step("Event Processing", "Normalizing and deduplicating events...")
        
        # Initialize processing statistics
        self.processing_stats['processing_start_time'] = datetime.now().isoformat()
        self.processing_stats['events_input'] = len(raw_events)
        
        if not raw_events:
            if self.logger:
                self.logger.log_warning("No events to process")
            return []
        
        # Step 1: Normalize events
        normalized_events = self._normalize_events(raw_events)
        self.processing_stats['events_normalized'] = len(normalized_events)
        
        # Step 2: Detect and classify categories
        categorized_events = self._detect_categories(normalized_events)
        
        # Step 3: Filter weekend events
        if not target_weekend:
            target_weekend = self._detect_target_weekend(categorized_events)
        
        weekend_events = self._filter_weekend_events(categorized_events, target_weekend)
        self.processing_stats['events_weekend_filtered'] = len(weekend_events)
        
        # Step 4: Deduplicate events
        deduplicated_events = self._deduplicate_events(weekend_events)
        self.processing_stats['events_deduplicated'] = len(deduplicated_events)
        self.processing_stats['duplicates_removed'] = len(weekend_events) - len(deduplicated_events)
        
        # Step 5: Final validation and cleanup
        validated_events = self._validate_events(deduplicated_events)
        self.processing_stats['events_validated'] = len(validated_events)
        
        # Update final statistics
        self.processing_stats['processing_end_time'] = datetime.now().isoformat()
        
        # Log processing summary
        self._log_processing_summary()
        
        return validated_events
    
    def _normalize_events(self, raw_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize event data to consistent format.
        
        Args:
            raw_events: List of raw events
            
        Returns:
            List of normalized events
        """
        if self.logger:
            self.logger.debug("🔧 Normalizing event data...")
        
        normalized_events = []
        
        for event in raw_events:
            try:
                normalized_event = self._normalize_single_event(event)
                if normalized_event:
                    normalized_events.append(normalized_event)
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"⚠️ Failed to normalize event: {e}")
                continue
        
        return normalized_events
    
    def _normalize_single_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Normalize a single event.
        
        Args:
            event: Raw event dictionary
            
        Returns:
            Normalized event dictionary or None if invalid
        """
        # Create normalized event structure
        normalized = {
            'event_id': event.get('event_id', self._generate_event_id(event)),
            'name': self._normalize_name(event.get('name', '')),
            'raw_category': self._normalize_category(event.get('raw_category', '')),
            'detected_category': None,  # Will be filled by category detector
            'date': self._normalize_date(event.get('date')),
            'time': self._normalize_time(event.get('time')),
            'datetime': None,  # Will be computed from date/time
            'timezone': event.get('timezone', 'America/Sao_Paulo'),
            'location': self._normalize_location(event.get('location', '')),
            'country': self._normalize_country(event.get('country', '')),
            'session_type': self._normalize_session_type(event.get('session_type', 'race')),
            'streaming_links': self._normalize_streaming_links(event.get('streaming_links', [])),
            'official_url': event.get('official_url', ''),
            'source': event.get('source', 'unknown'),
            'source_display_name': event.get('source_display_name', 'Unknown Source'),
            'source_priority': event.get('source_priority', 50),
            'collected_at': event.get('collected_at', datetime.now().isoformat()),
            'processed_at': datetime.now().isoformat(),
            'raw_data': event.get('raw_data', event)
        }
        
        # Compute datetime from date and time
        normalized['datetime'] = self._compute_datetime(
            normalized['date'], 
            normalized['time'], 
            normalized['timezone']
        )
        
        # Validate required fields
        if not normalized['name'] or not normalized['datetime']:
            return None
        
        return normalized
    
    def _normalize_name(self, name: str) -> str:
        """Normalize event name."""
        if not name:
            return ""
        
        # Clean up the name
        name = str(name).strip()
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name)
        
        # Common replacements
        replacements = {
            'GP': 'Grand Prix',
            'F-1': 'F1',
            'Formula-1': 'Formula 1',
            'Fórmula-1': 'Formula 1',
            'MotoGP': 'MotoGP',
            'Moto GP': 'MotoGP'
        }
        
        for old, new in replacements.items():
            name = re.sub(rf'\b{re.escape(old)}\b', new, name, flags=re.IGNORECASE)
        
        return name
    
    def _normalize_category(self, category: str) -> str:
        """Normalize category name."""
        if not category:
            return ""
        
        category = str(category).strip()
        
        # Common category normalizations
        category_map = {
            'f1': 'Formula 1',
            'formula1': 'Formula 1',
            'formula-1': 'Formula 1',
            'fórmula1': 'Formula 1',
            'fórmula-1': 'Formula 1',
            'f2': 'Formula 2',
            'f3': 'Formula 3',
            'motogp': 'MotoGP',
            'moto gp': 'MotoGP',
            'moto2': 'Moto2',
            'moto3': 'Moto3',
            'stockcar': 'Stock Car',
            'stock-car': 'Stock Car',
            'nascar': 'NASCAR',
            'indycar': 'IndyCar',
            'indy car': 'IndyCar',
            'wec': 'WEC',
            'wsbk': 'WSBK',
            'wrc': 'WRC',
            'formulae': 'Formula E',
            'formula-e': 'Formula E',
            'fórmula-e': 'Formula E'
        }
        
        category_lower = category.lower()
        return category_map.get(category_lower, category)
    
    def _normalize_date(self, date_value: Any) -> Optional[str]:
        """Normalize date to YYYY-MM-DD format."""
        if not date_value:
            return None
        
        try:
            if isinstance(date_value, datetime):
                return date_value.strftime('%Y-%m-%d')
            
            if isinstance(date_value, str):
                # Try to parse various date formats
                date_patterns = [
                    r'(\d{4})-(\d{1,2})-(\d{1,2})',      # YYYY-MM-DD
                    r'(\d{1,2})/(\d{1,2})/(\d{4})',      # DD/MM/YYYY
                    r'(\d{1,2})-(\d{1,2})-(\d{4})',      # DD-MM-YYYY
                    r'(\d{4})/(\d{1,2})/(\d{1,2})',      # YYYY/MM/DD
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, date_value)
                    if match:
                        if len(match.group(1)) == 4:  # YYYY format
                            year, month, day = match.groups()
                        else:  # DD format
                            day, month, year = match.groups()
                        
                        return f"{year}-{int(month):02d}-{int(day):02d}"
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Failed to normalize date '{date_value}': {e}")
        
        return None
    
    def _normalize_time(self, time_value: Any) -> Optional[str]:
        """Normalize time to HH:MM format."""
        if not time_value:
            return None
        
        try:
            if isinstance(time_value, str):
                # Extract time from string
                time_patterns = [
                    r'(\d{1,2}):(\d{2})',
                    r'(\d{1,2})h(\d{2})',
                    r'(\d{1,2})\.(\d{2})'
                ]
                
                for pattern in time_patterns:
                    match = re.search(pattern, time_value)
                    if match:
                        hour = int(match.group(1))
                        minute = int(match.group(2))
                        
                        if 0 <= hour <= 23 and 0 <= minute <= 59:
                            return f"{hour:02d}:{minute:02d}"
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Failed to normalize time '{time_value}': {e}")
        
        return None
    
    def _compute_datetime(self, date_str: Optional[str], time_str: Optional[str], 
                         timezone_str: str) -> Optional[datetime]:
        """Compute datetime object from date and time strings."""
        if not date_str:
            return None
        
        try:
            import pytz
            from dateutil import parser
            
            # Create datetime string
            if time_str:
                datetime_str = f"{date_str} {time_str}"
            else:
                datetime_str = f"{date_str} 12:00"  # Default to noon
            
            # Parse datetime
            parsed_dt = parser.parse(datetime_str)
            
            # Add timezone
            if parsed_dt.tzinfo is None:
                tz = pytz.timezone(timezone_str)
                parsed_dt = tz.localize(parsed_dt)
            
            return parsed_dt
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Failed to compute datetime: {e}")
            return None
    
    def _normalize_location(self, location: str) -> str:
        """Normalize location/circuit name."""
        if not location:
            return ""
        
        location = str(location).strip()
        
        # Common location normalizations
        location_map = {
            'interlagos': 'Autódromo José Carlos Pace (Interlagos)',
            'jacarepaguá': 'Autódromo Internacional Nelson Piquet',
            'silverstone': 'Silverstone Circuit',
            'monza': 'Autodromo Nazionale di Monza',
            'spa': 'Circuit de Spa-Francorchamps',
            'monaco': 'Circuit de Monaco',
            'suzuka': 'Suzuka International Racing Course'
        }
        
        location_lower = location.lower()
        return location_map.get(location_lower, location)
    
    def _normalize_country(self, country: str) -> str:
        """Normalize country name."""
        if not country:
            return ""
        
        country = str(country).strip()
        
        # Common country normalizations
        country_map = {
            'brasil': 'Brazil',
            'brazil': 'Brazil',
            'br': 'Brazil',
            'uk': 'United Kingdom',
            'gb': 'United Kingdom',
            'usa': 'United States',
            'us': 'United States'
        }
        
        country_lower = country.lower()
        return country_map.get(country_lower, country)
    
    def _normalize_session_type(self, session_type: str) -> str:
        """Normalize session type."""
        if not session_type:
            return "race"
        
        session_type = str(session_type).lower().strip()
        
        session_map = {
            'corrida': 'race',
            'quali': 'qualifying',
            'classificação': 'qualifying',
            'treino': 'practice',
            'practice': 'practice',
            'fp1': 'practice',
            'fp2': 'practice',
            'fp3': 'practice',
            'sprint': 'sprint'
        }
        
        return session_map.get(session_type, session_type)
    
    def _normalize_streaming_links(self, links: List[str]) -> List[str]:
        """Normalize streaming links."""
        if not links:
            return []
        
        normalized_links = []
        for link in links:
            if isinstance(link, str) and link.strip():
                link = link.strip()
                if link.startswith('http'):
                    normalized_links.append(link)
        
        return normalized_links
    
    def _detect_categories(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect and classify event categories.
        
        Args:
            events: List of normalized events
            
        Returns:
            List of events with detected categories
        """
        if not self.category_detector:
            # If no category detector, use raw categories
            for event in events:
                event['detected_category'] = event.get('raw_category', 'Unknown')
            return events
        
        if self.logger:
            self.logger.debug("🏷️ Detecting event categories...")
        
        # Extract category information for batch processing
        category_inputs = []
        for event in events:
            category_inputs.append({
                'name': event.get('name', ''),
                'raw_category': event.get('raw_category', ''),
                'location': event.get('location', ''),
                'source': event.get('source', '')
            })
        
        # Batch detect categories
        detected_categories = self.category_detector.detect_categories_batch(category_inputs)
        
        # Update events with detected categories
        for event, detected in zip(events, detected_categories):
            event['detected_category'] = detected.get('category', 'Unknown')
            event['category_confidence'] = detected.get('confidence', 0.0)
            event['category_source'] = detected.get('source', 'unknown')
        
        # Update statistics
        unique_categories = set(event['detected_category'] for event in events)
        self.processing_stats['categories_detected'] = len(unique_categories)
        
        if self.logger:
            self.logger.debug(f"🏷️ Detected {len(unique_categories)} unique categories")
        
        return events
    
    def _detect_target_weekend(self, events: List[Dict[str, Any]]) -> Tuple[datetime, datetime]:
        """
        Detect target weekend from events.
        
        Args:
            events: List of events
            
        Returns:
            Tuple of (weekend_start, weekend_end)
        """
        if not events:
            # Default to next weekend
            today = datetime.now()
            days_until_friday = (self.weekend_start_day - today.weekday()) % 7
            if days_until_friday == 0 and today.weekday() > self.weekend_end_day:
                days_until_friday = 7
            
            weekend_start = today + timedelta(days=days_until_friday)
            weekend_end = weekend_start + timedelta(days=self.weekend_end_day - self.weekend_start_day)
            
            return weekend_start, weekend_end
        
        # Find the earliest event date
        earliest_date = None
        for event in events:
            event_datetime = event.get('datetime')
            if event_datetime and (earliest_date is None or event_datetime < earliest_date):
                earliest_date = event_datetime
        
        if not earliest_date:
            # Fallback to next weekend
            return self._detect_target_weekend([])
        
        # Find the weekend containing the earliest event
        event_weekday = earliest_date.weekday()
        
        if event_weekday >= self.weekend_start_day:
            # Event is on weekend, use current week
            days_to_friday = earliest_date.weekday() - self.weekend_start_day
            weekend_start = earliest_date - timedelta(days=days_to_friday)
        else:
            # Event is before weekend, find next weekend
            days_until_friday = self.weekend_start_day - event_weekday
            weekend_start = earliest_date + timedelta(days=days_until_friday)
        
        weekend_end = weekend_start + timedelta(days=self.weekend_end_day - self.weekend_start_day)
        
        # Extend boundaries slightly
        weekend_start = weekend_start - timedelta(hours=self.extend_weekend_hours)
        weekend_end = weekend_end + timedelta(hours=self.extend_weekend_hours)
        
        if self.logger:
            self.logger.debug(
                f"🎯 Target weekend: {weekend_start.strftime('%Y-%m-%d %H:%M')} to "
                f"{weekend_end.strftime('%Y-%m-%d %H:%M')}"
            )
        
        return weekend_start, weekend_end
    
    def _filter_weekend_events(self, events: List[Dict[str, Any]], 
                              target_weekend: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
        """
        Filter events to only include those in the target weekend.
        
        Args:
            events: List of events
            target_weekend: Tuple of (start, end) datetime
            
        Returns:
            List of weekend events
        """
        if self.logger:
            self.logger.debug("📅 Filtering weekend events...")
        
        weekend_start, weekend_end = target_weekend
        weekend_events = []
        
        for event in events:
            event_datetime = event.get('datetime')
            if event_datetime and weekend_start <= event_datetime <= weekend_end:
                weekend_events.append(event)
        
        if self.logger:
            self.logger.debug(f"📅 Filtered to {len(weekend_events)} weekend events")
        
        return weekend_events
    
    def _deduplicate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate events using fuzzy matching.
        
        Args:
            events: List of events to deduplicate
            
        Returns:
            List of deduplicated events
        """
        if self.logger:
            self.logger.debug("🔍 Deduplicating events...")
        
        if len(events) <= 1:
            return events
        
        # Group events by similarity
        event_groups = self._group_similar_events(events)
        
        # Select best event from each group
        deduplicated_events = []
        for group in event_groups:
            best_event = self._select_best_event(group)
            deduplicated_events.append(best_event)
        
        if self.logger:
            duplicates_removed = len(events) - len(deduplicated_events)
            self.logger.debug(f"🔍 Removed {duplicates_removed} duplicate events")
        
        return deduplicated_events
    
    def _group_similar_events(self, events: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group similar events together."""
        groups = []
        used_indices = set()
        
        for i, event1 in enumerate(events):
            if i in used_indices:
                continue
            
            # Start new group with this event
            group = [event1]
            used_indices.add(i)
            
            # Find similar events
            for j, event2 in enumerate(events[i+1:], i+1):
                if j in used_indices:
                    continue
                
                if self._are_events_similar(event1, event2):
                    group.append(event2)
                    used_indices.add(j)
            
            groups.append(group)
        
        return groups
    
    def _are_events_similar(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> bool:
        """Check if two events are similar (duplicates)."""
        # Check name similarity
        name1 = unidecode(event1.get('name', '')).lower()
        name2 = unidecode(event2.get('name', '')).lower()
        name_similarity = fuzz.ratio(name1, name2)
        
        if name_similarity < self.similarity_threshold:
            return False
        
        # Check datetime similarity
        dt1 = event1.get('datetime')
        dt2 = event2.get('datetime')
        
        if dt1 and dt2:
            time_diff = abs((dt1 - dt2).total_seconds()) / 60  # minutes
            if time_diff > self.time_tolerance_minutes:
                return False
        
        # Check category similarity
        cat1 = event1.get('detected_category', '').lower()
        cat2 = event2.get('detected_category', '').lower()
        
        if cat1 and cat2:
            cat_similarity = fuzz.ratio(cat1, cat2)
            if cat_similarity < self.category_similarity_threshold:
                return False
        
        # Check location similarity (if available)
        loc1 = event1.get('location', '').lower()
        loc2 = event2.get('location', '').lower()
        
        if loc1 and loc2:
            loc_similarity = fuzz.ratio(loc1, loc2)
            if loc_similarity < self.location_similarity_threshold:
                return False
        
        return True
    
    def _select_best_event(self, event_group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best event from a group of similar events."""
        if len(event_group) == 1:
            return event_group[0]
        
        # Sort by source priority (higher is better)
        sorted_events = sorted(
            event_group,
            key=lambda e: (
                e.get('source_priority', 50),
                len(e.get('streaming_links', [])),
                len(e.get('name', '')),
                bool(e.get('official_url', ''))
            ),
            reverse=True
        )
        
        best_event = sorted_events[0]
        
        # Merge information from other events
        for other_event in sorted_events[1:]:
            # Merge streaming links
            other_links = other_event.get('streaming_links', [])
            best_links = best_event.get('streaming_links', [])
            merged_links = list(set(best_links + other_links))
            best_event['streaming_links'] = merged_links
            
            # Use better official URL if available
            if not best_event.get('official_url') and other_event.get('official_url'):
                best_event['official_url'] = other_event['official_url']
            
            # Use better location if available
            if not best_event.get('location') and other_event.get('location'):
                best_event['location'] = other_event['location']
        
        return best_event
    
    def _validate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate events and remove invalid ones.
        
        Args:
            events: List of events to validate
            
        Returns:
            List of valid events
        """
        if self.logger:
            self.logger.debug("✅ Validating events...")
        
        valid_events = []
        
        for event in events:
            if self._is_event_valid(event):
                valid_events.append(event)
            else:
                if self.logger:
                    self.logger.debug(f"⚠️ Invalid event removed: {event.get('name', 'Unknown')}")
        
        if self.logger:
            invalid_count = len(events) - len(valid_events)
            self.logger.debug(f"✅ Validated {len(valid_events)} events, removed {invalid_count} invalid")
        
        return valid_events
    
    def _is_event_valid(self, event: Dict[str, Any]) -> bool:
        """Check if an event is valid."""
        # Required fields
        required_fields = ['name', 'datetime', 'detected_category']
        
        for field in required_fields:
            if not event.get(field):
                return False
        
        # Check name length
        if len(event['name'].strip()) < 3:
            return False
        
        # Check if datetime is reasonable
        event_datetime = event['datetime']
        now = datetime.now(event_datetime.tzinfo)
        
        # Event should be within reasonable time range (past year to next year)
        if event_datetime < now - timedelta(days=365) or event_datetime > now + timedelta(days=365):
            return False
        
        return True
    
    def _generate_event_id(self, event: Dict[str, Any]) -> str:
        """Generate unique event ID."""
        id_components = [
            str(event.get('name', '')),
            str(event.get('date', '')),
            str(event.get('time', '')),
            str(event.get('location', '')),
            str(event.get('source', ''))
        ]
        
        id_string = '|'.join(id_components).lower()
        return hashlib.md5(id_string.encode()).hexdigest()[:16]
    
    def _log_processing_summary(self) -> None:
        """Log processing summary statistics."""
        if not self.logger:
            return
        
        stats = self.processing_stats
        
        self.logger.log_step(
            f"📊 Processing Summary: "
            f"{stats['events_input']} → {stats['events_validated']} events "
            f"({stats['duplicates_removed']} duplicates removed, "
            f"{stats['categories_detected']} categories detected)"
        )
        
        # Calculate processing time
        if stats['processing_start_time'] and stats['processing_end_time']:
            start_time = datetime.fromisoformat(stats['processing_start_time'])
            end_time = datetime.fromisoformat(stats['processing_end_time'])
            duration = (end_time - start_time).total_seconds()
            
            self.logger.debug(f"⏱️ Processing completed in {duration:.1f} seconds")
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get detailed processing statistics."""
        return self.processing_stats.copy()
    
    def __str__(self) -> str:
        """String representation."""
        return f"EventProcessor(threshold={self.similarity_threshold})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"<EventProcessor(similarity_threshold={self.similarity_threshold}, time_tolerance={self.time_tolerance_minutes}min)>"
