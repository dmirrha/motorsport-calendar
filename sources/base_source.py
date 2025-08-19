"""
Base Source Class for Motorsport Calendar

Abstract base class that defines the interface and common functionality
for all data sources (APIs, web scrapers, etc.).
"""

import time
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from urllib.parse import urljoin, urlparse
import random


class BaseSource(ABC):
    """Abstract base class for all motorsport data sources."""
    
    def __init__(self, config_manager=None, logger=None, ui_manager=None):
        """
        Initialize base source.
        
        Args:
            config_manager: Configuration manager instance
            logger: Logger instance
            ui_manager: UI manager instance
        """
        self.config = config_manager
        # Não utilizar logger padrão do logging aqui: manter None quando não fornecido
        # para que chamadas a métodos específicos (ex.: save_payload, log_source_error)
        # sejam condicionais e não causem AttributeError.
        self.logger = logger
        self.ui = ui_manager
        
        # Source identification
        self.source_name = self.__class__.__name__.replace('Source', '').lower()
        self.source_display_name = self.get_display_name()
        
        # Configuration
        self.timeout = 10
        self.retry_attempts = 3
        self.rate_limit_delay = 1.0
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        
        # Load configuration
        self._load_config()
        
        # Session for connection pooling
        self.session = requests.Session()
        self._setup_session()
        
        # Statistics
        self.stats = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'events_collected': 0,
            'last_collection_time': None,
            'errors': []
        }
    
    def _load_config(self) -> None:
        """Load source-specific configuration."""
        if not self.config:
            return
        
        data_sources_config = self.config.get_data_sources_config()
        
        self.timeout = data_sources_config.get('timeout_seconds', 10)
        self.retry_attempts = data_sources_config.get('retry_attempts', 3)
        self.rate_limit_delay = data_sources_config.get('rate_limit_delay', 1.0)
        
        custom_user_agents = data_sources_config.get('user_agents', [])
        if custom_user_agents:
            self.user_agents = custom_user_agents
    
    def _setup_session(self) -> None:
        """Setup HTTP session with headers and adapters."""
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Set timeout for all requests
        adapter = requests.adapters.HTTPAdapter(
            max_retries=requests.adapters.Retry(
                total=self.retry_attempts,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    @abstractmethod
    def get_display_name(self) -> str:
        """
        Get human-readable display name for this source.
        
        Returns:
            Display name string
        """
        pass
    
    @abstractmethod
    def get_base_url(self) -> str:
        """
        Get base URL for this source.
        
        Returns:
            Base URL string
        """
        pass
    
    @abstractmethod
    def collect_events(self, target_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Collect motorsport events from this source.
        
        Args:
            target_date: Target date for event collection (optional)
            
        Returns:
            List of event dictionaries
        """
        pass
    
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            url: URL to request
            method: HTTP method
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object or None if failed
        """
        self.stats['requests_made'] += 1
        
        # Rate limiting
        if self.stats['requests_made'] > 1:
            time.sleep(self.rate_limit_delay)
        
        # Rotate user agent occasionally
        if self.stats['requests_made'] % 10 == 0:
            self.session.headers['User-Agent'] = random.choice(self.user_agents)
        
        for attempt in range(self.retry_attempts):
            try:
                if self.logger:
                    self.logger.debug(f"🌐 {self.source_display_name}: Making request to {url} (attempt {attempt + 1})")
                
                # Set timeout if not provided
                if 'timeout' not in kwargs:
                    kwargs['timeout'] = self.timeout
                
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                
                self.stats['successful_requests'] += 1
                
                # Save payload if logger supports it
                if getattr(self.logger, "save_payload", None):
                    self.logger.save_payload(
                        source=self.source_name,
                        data=response.text,
                        data_type='html',
                        include_headers=True,
                        headers=response.headers
                    )
                
                return response
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Request failed (attempt {attempt + 1}/{self.retry_attempts}): {str(e)}"
                
                if self.logger:
                    self.logger.debug(f"⚠️ {self.source_display_name}: {error_msg}")
                
                self.stats['errors'].append({
                    'timestamp': datetime.now().isoformat(),
                    'url': url,
                    'attempt': attempt + 1,
                    'error': str(e)
                })
                
                if attempt < self.retry_attempts - 1:
                    # Exponential backoff
                    wait_time = (2 ** attempt) * self.rate_limit_delay
                    time.sleep(wait_time)
                else:
                    # Final attempt failed
                    self.stats['failed_requests'] += 1
                    if getattr(self.logger, "log_source_error", None):
                        self.logger.log_source_error(self.source_display_name, error_msg)
                    return None
        
        return None
    
    def parse_date_time(self, date_str: str, time_str: str = "", 
                       timezone_str: str = "America/Sao_Paulo") -> Optional[datetime]:
        """
        Parse date and time strings into datetime object with Brazilian format support.
        
        Args:
            date_str: Date string (supports DD/MM/YYYY, DD-MM-YYYY, YYYY/MM/DD formats)
            time_str: Time string (optional)
            timezone_str: Timezone string
            
        Returns:
            Parsed datetime object or None if failed
        """
        try:
            import pytz
            from datetime import datetime as dt
            
            # First try to parse with explicit Brazilian formats
            date_formats = [
                '%d/%m/%Y',    # DD/MM/YYYY
                '%d-%m-%Y',    # DD-MM-YYYY
                '%d/%m/%y',    # DD/MM/YY 
                '%d-%m-%y',    # DD-MM-YY
                '%Y/%m/%d',    # YYYY/MM/DD
                '%Y-%m-%d',    # YYYY-MM-DD
            ]
            
            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = dt.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            
            if not parsed_date:
                # Fallback to dateutil parser with dayfirst=True for Brazilian format
                from dateutil import parser
                parsed_date = parser.parse(date_str, dayfirst=True)
            
            # Add time if provided
            if time_str:
                time_formats = ['%H:%M', '%H:%M:%S']
                parsed_time = None
                for time_fmt in time_formats:
                    try:
                        time_obj = dt.strptime(time_str, time_fmt).time()
                        parsed_date = dt.combine(parsed_date.date(), time_obj)
                        break
                    except ValueError:
                        continue
            
            # Add timezone if not present
            if parsed_date.tzinfo is None:
                tz = pytz.timezone(timezone_str)
                parsed_date = tz.localize(parsed_date)
            
            return parsed_date
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Failed to parse datetime '{date_str} {time_str}': {e}")
            return None
    
    def normalize_event_data(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw event data to standard format.
        
        Args:
            raw_event: Raw event data from source
            
        Returns:
            Normalized event dictionary
        """
        normalized = {
            'event_id': self._generate_event_id(raw_event),
            'name': (raw_event.get('name') or '').strip(),
            'category': (raw_event.get('category') or '').strip(),
            'raw_category': (raw_event.get('category') or '').strip(),
            'date': raw_event.get('date'),
            'time': raw_event.get('time'),
            'timezone': raw_event.get('timezone', 'America/Sao_Paulo'),
            'location': (raw_event.get('location') or '').strip(),
            'country': (raw_event.get('country') or '').strip(),
            'session_type': raw_event.get('session_type', 'race').lower(),
            'streaming_links': raw_event.get('streaming_links', []),
            'official_url': raw_event.get('official_url', ''),
            'source': self.source_name,
            'source_display_name': self.source_display_name,
            'collected_at': datetime.now().isoformat(),
            'raw_text': raw_event.get('raw_text'),
            'raw_data': raw_event  # Keep original data for debugging
        }
        
        # Clean up empty values
        for key, value in normalized.items():
            if isinstance(value, str) and value and not value.strip():
                normalized[key] = None
        
        return normalized
    
    def _generate_event_id(self, event_data: Dict[str, Any]) -> str:
        """
        Generate unique event ID based on event data.
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            Unique event ID string
        """
        import hashlib
        
        # Create ID from key event attributes
        id_components = [
            str(event_data.get('name', '')),
            str(event_data.get('date', '')),
            str(event_data.get('time', '')),
            str(event_data.get('location', '')),
            self.source_name
        ]
        
        id_string = '|'.join(id_components).lower()
        return hashlib.md5(id_string.encode()).hexdigest()[:16]
    
    def filter_weekend_events(self, events: List[Dict[str, Any]], 
                            target_weekend: Optional[Tuple[datetime, datetime]] = None) -> List[Dict[str, Any]]:
        """
        Filter events to only include weekend events.
        
        Args:
            events: List of events
            target_weekend: Optional tuple of (start_date, end_date)
            
        Returns:
            Filtered list of weekend events
        """
        if not events:
            return []
        
        weekend_events = []
        
        for event in events:
            event_date = event.get('date')
            if not event_date:
                continue
            
            try:
                if isinstance(event_date, str):
                    event_dt = self.parse_date_time(event_date)
                elif isinstance(event_date, datetime):
                    event_dt = event_date
                else:
                    continue
                
                if not event_dt:
                    continue
                
                # Check if event is in target weekend
                if target_weekend:
                    start_date, end_date = target_weekend
                    if start_date <= event_dt <= end_date:
                        weekend_events.append(event)
                else:
                    # Check if event is on weekend (Friday to Sunday)
                    weekday = event_dt.weekday()  # 0=Monday, 6=Sunday
                    if weekday >= 4:  # Friday=4, Saturday=5, Sunday=6
                        weekend_events.append(event)
                        
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"⚠️ Error filtering event date: {e}")
                continue
        
        return weekend_events
    
    def get_streaming_links(self, category: str, region: str = "BR") -> List[str]:
        """
        Get streaming links for a category and region.
        
        Args:
            category: Event category
            region: Region code
            
        Returns:
            List of streaming provider names/URLs
        """
        if not self.config:
            return []
        
        streaming_providers = self.config.get_streaming_providers(region)
        return streaming_providers.get(category, [])
    
    def validate_event_data(self, event: Dict[str, Any]) -> bool:
        """
        Validate event data completeness.
        
        Args:
            event: Event dictionary
            
        Returns:
            True if event data is valid
        """
        required_fields = ['name', 'date']
        
        for field in required_fields:
            if not event.get(field):
                if self.logger:
                    self.logger.debug(f"⚠️ Event missing required field '{field}': {event}")
                return False
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get collection statistics for this source.
        
        Returns:
            Statistics dictionary
        """
        success_rate = 0.0
        if self.stats['requests_made'] > 0:
            success_rate = self.stats['successful_requests'] / self.stats['requests_made']
        
        return {
            'source_name': self.source_display_name,
            'requests_made': self.stats['requests_made'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'success_rate': success_rate,
            'events_collected': self.stats['events_collected'],
            'last_collection_time': self.stats['last_collection_time'],
            'error_count': len(self.stats['errors']),
            'recent_errors': self.stats['errors'][-5:] if self.stats['errors'] else []
        }
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if hasattr(self, 'session'):
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.source_display_name} ({self.source_name})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"<{self.__class__.__name__}(name='{self.source_name}', url='{self.get_base_url()}')>"
