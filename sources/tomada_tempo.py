"""
Tomada de Tempo Source for Motorsport Calendar

Primary data source scraper for tomadadetempo.com.br - the most comprehensive
Brazilian motorsport calendar website with complete schedules and streaming info.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from .base_source import BaseSource


class TomadaTempoSource(BaseSource):
    """Primary data source for tomadadetempo.com.br"""
    
    def get_display_name(self) -> str:
        """Get human-readable display name."""
        return "Tomada de Tempo"
    
    def get_base_url(self) -> str:
        """Get base URL for Tomada de Tempo."""
        return "https://www.tomadadetempo.com.br"
    
    def collect_events(self, target_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Collect motorsport events from Tomada de Tempo.
        
        Args:
            target_date: Target date for event collection
            
        Returns:
            List of event dictionaries
        """
        if self.logger:
            self.logger.log_source_start(self.source_display_name)
        
        if self.ui:
            self.ui.show_source_result(self.source_display_name, True, 0, "Starting collection...")
        
        events = []
        
        try:
            # Get current weekend if no target date provided
            if not target_date:
                target_date = self._get_next_weekend()
            
            # Calculate current weekend range (Friday to Sunday) with proper timezone
            import pytz
            tz = pytz.timezone('America/Sao_Paulo')
            
            # Ensure target_date has timezone
            if target_date.tzinfo is None:
                target_date = tz.localize(target_date)
            
            weekend_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            weekend_end = weekend_start + timedelta(days=2, hours=23, minutes=59, seconds=59)
            target_weekend = (weekend_start, weekend_end)
            
            # Collect from different sections
            calendar_events = self._collect_from_calendar(target_date)
            events.extend(calendar_events)
            
            # Collect from specific category pages
            category_events = self._collect_from_categories(target_date)
            events.extend(category_events)
            
            # Filter events for current weekend only
            weekend_events = self.filter_weekend_events(events, target_weekend)
            normalized_events = [self.normalize_event_data(event) for event in weekend_events]
            
            # Validate events
            valid_events = [event for event in normalized_events if self.validate_event_data(event)]
            
            self.stats['events_collected'] = len(valid_events)
            self.stats['last_collection_time'] = datetime.now().isoformat()
            
            if self.logger:
                self.logger.log_source_success(self.source_display_name, len(valid_events))
            
            if self.ui:
                self.ui.show_source_result(self.source_display_name, True, len(valid_events))
            
            return valid_events
            
        except Exception as e:
            error_msg = f"Failed to collect events: {str(e)}"
            self.stats['failed_requests'] += 1
            
            if self.logger:
                self.logger.log_source_error(self.source_display_name, error_msg)
            
            if self.ui:
                self.ui.show_source_result(self.source_display_name, False, 0, error_msg)
            
            return []
    
    def _get_next_weekend(self) -> datetime:
        """Get the current weekend date (Friday of the current week)."""
        today = datetime.now()
        # Calculate days since last Friday
        days_since_friday = (today.weekday() - 4) % 7
        # If today is Friday, Saturday or Sunday, we're in the current weekend
        if today.weekday() >= 4:  # 4=Friday, 5=Saturday, 6=Sunday
            current_friday = today - timedelta(days=days_since_friday)
        else:
            # If today is Monday-Thursday, get the previous Friday
            current_friday = today - timedelta(days=days_since_friday)
        return current_friday
    
    def _collect_from_calendar(self, target_date: datetime) -> List[Dict[str, Any]]:
        """
        Collect events from the main calendar page.
        
        Args:
            target_date: Target date for collection
            
        Returns:
            List of raw event dictionaries
        """
        events = []
        
        try:
            # Try different calendar URL patterns
            calendar_urls = [
                f"{self.get_base_url()}/calendario",
                f"{self.get_base_url()}/programacao",
                f"{self.get_base_url()}/agenda",
                self.get_base_url()  # Main page
            ]
            
            for url in calendar_urls:
                response = self.make_request(url)
                if response:
                    page_events = self._parse_calendar_page(response.text, target_date)
                    events.extend(page_events)
                    if page_events:  # If we found events, no need to try other URLs
                        break
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Error collecting from calendar: {e}")
        
        return events
    
    def _parse_calendar_page(self, html_content: str, target_date: datetime) -> List[Dict[str, Any]]:
        """
        Parse calendar page HTML to extract events.
        
        Args:
            html_content: HTML content of the page
            target_date: Target date for filtering
            
        Returns:
            List of event dictionaries
        """
        events = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for common event patterns
        event_selectors = [
            '.evento',
            '.event',
            '.calendar-event',
            '.programacao-item',
            '.agenda-item',
            'article',
            '.post',
            '.entry'
        ]
        
        for selector in event_selectors:
            event_elements = soup.select(selector)
            if event_elements:
                for element in event_elements:
                    event = self._extract_event_from_element(element, target_date)
                    if event:
                        events.append(event)
                break  # Use first successful selector
        
        # If no structured events found, try text parsing
        if not events:
            events = self._parse_text_content(html_content, target_date)
        
        return events
    
    def _extract_event_from_element(self, element, target_date: datetime) -> Optional[Dict[str, Any]]:
        """
        Extract event information from HTML element.
        
        Args:
            element: BeautifulSoup element
            target_date: Target date for filtering
            
        Returns:
            Event dictionary or None
        """
        try:
            # Extract text content
            text_content = element.get_text(separator=' ', strip=True)
            
            # Look for event patterns
            event_patterns = [
                r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',  # Date patterns
                r'(\d{1,2}:\d{2})',  # Time patterns
                r'(F[1-4]|Formula [1-4]|Fórmula [1-4])',  # Formula categories
                r'(MotoGP|Moto\s*GP|Moto\s*[2-3])',  # Motorcycle categories
                r'(Stock Car|NASCAR|IndyCar)',  # Other categories
                r'(GP|Grand Prix|Grande Prêmio)',  # GP events
                r'(Corrida|Race|Quali|Treino|Practice)'  # Session types
            ]
            
            # Check if this looks like a motorsport event
            motorsport_indicators = 0
            for pattern in event_patterns[2:]:  # Skip date/time patterns
                if re.search(pattern, text_content, re.IGNORECASE):
                    motorsport_indicators += 1
            
            if motorsport_indicators == 0:
                return None
            
            # Extract basic information
            event_name = self._extract_event_name(text_content)
            event_date = self._extract_date(text_content)
            event_time = self._extract_time(text_content)
            category = self._extract_category(text_content)
            location = self._extract_location(text_content)
            
            # Look for streaming links
            streaming_links = self._extract_streaming_links(element)
            
            # Get official URL if available
            official_url = self._extract_official_url(element)
            
            if event_name and event_date:
                return {
                    'name': event_name,
                    'category': category or 'Unknown',
                    'date': event_date,
                    'time': event_time,
                    'location': location,
                    'country': 'Brasil',
                    'session_type': self._extract_session_type(text_content),
                    'streaming_links': streaming_links,
                    'official_url': official_url,
                    'raw_text': text_content
                }
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Error extracting event from element: {e}")
        
        return None
    
    def _extract_event_name(self, text: str) -> Optional[str]:
        """Extract event name from text."""
        # Look for common event name patterns
        patterns = [
            r'GP\s+(?:da\s+|de\s+|do\s+)?([A-Za-z\s]+)',  # GP events
            r'Grande Prêmio\s+(?:da\s+|de\s+|do\s+)?([A-Za-z\s]+)',
            r'([A-Za-z\s]+)\s+(?:Championship|Campeonato)',
            r'([A-Za-z\s]+)\s+(?:Race|Corrida)',
            r'^([A-Za-z\s]+?)(?:\s*-\s*|\s*\|\s*|\s*:\s*)'  # Text before separators
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1):
                name = match.group(1).strip()
                if len(name) > 3:  # Reasonable name length
                    return name
        
        # Fallback: use first meaningful words
        words = text.split()[:5]
        return ' '.join(words) if words else None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text with improved parsing."""
        # Look for dates in DD/MM/YYYY or DD-MM-YYYY format first
        dd_mm_yyyy_pattern = r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})'
        match = re.search(dd_mm_yyyy_pattern, text)
        if match:
            day, month, year = match.groups()
            # Validate date components
            try:
                day_int, month_int, year_int = int(day), int(month), int(year)
                if 1 <= day_int <= 31 and 1 <= month_int <= 12 and year_int >= 2020:
                    return f"{day_int:02d}/{month_int:02d}/{year_int}"
            except ValueError:
                pass
        
        # Look for dates in DD/MM/YY or DD-MM-YY format
        dd_mm_yy_pattern = r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2})'
        match = re.search(dd_mm_yy_pattern, text)
        if match:
            day, month, year = match.groups()
            # Validate date components
            try:
                day_int, month_int, year_int = int(day), int(month), int(year)
                if 1 <= day_int <= 31 and 1 <= month_int <= 12:
                    full_year = 2000 + year_int if year_int < 50 else 1900 + year_int
                    return f"{day_int:02d}/{month_int:02d}/{full_year}"
            except ValueError:
                pass
        
        # Look for dates in YYYY/MM/DD or YYYY-MM-DD format
        yyyy_mm_dd_pattern = r'(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})'
        match = re.search(yyyy_mm_dd_pattern, text)
        if match:
            year, month, day = match.groups()
            # Validate date components
            try:
                year_int, month_int, day_int = int(year), int(month), int(day)
                if 1 <= day_int <= 31 and 1 <= month_int <= 12 and year_int >= 2020:
                    return f"{day_int:02d}/{month_int:02d}/{year_int}"
            except ValueError:
                pass
        
        return None
    
    def _extract_time(self, text: str) -> Optional[str]:
        """Extract time from text."""
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(?:h|hrs?|horas?)?',
            r'(\d{1,2})h(\d{2})',
            r'(\d{1,2}):(\d{2})'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2))
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return f"{hour:02d}:{minute:02d}"
        
        return None
    
    def _extract_category(self, text: str) -> Optional[str]:
        """Extract motorsport category from text."""
        category_patterns = {
            'F1': [r'F[1-]?1|Formula\s*1|Fórmula\s*1'],
            'F2': [r'F[2-]?2|Formula\s*2|Fórmula\s*2'],
            'F3': [r'F[3-]?3|Formula\s*3|Fórmula\s*3'],
            'MotoGP': [r'MotoGP|Moto\s*GP'],
            'Moto2': [r'Moto\s*2'],
            'Moto3': [r'Moto\s*3'],
            'StockCar': [r'Stock\s*Car'],
            'NASCAR': [r'NASCAR'],
            'IndyCar': [r'IndyCar|Indy\s*Car'],
            'WEC': [r'WEC|World\s*Endurance'],
            'WSBK': [r'WSBK|World\s*Superbike|Superbike'],
            'WRC': [r'WRC|World\s*Rally|Rally'],
            'FormulaE': [r'Formula\s*E|Fórmula\s*E|FE']
        }
        
        for category, patterns in category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return category
        
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location/circuit from text."""
        # Common Brazilian circuits and international locations
        locations = [
            'Interlagos', 'Jacarepaguá', 'Goiânia', 'Curitiba', 'Brasília',
            'Cascavel', 'Santa Cruz do Sul', 'Tarumã', 'Velopark',
            'Mônaco', 'Silverstone', 'Spa', 'Monza', 'Suzuka',
            'Catalunya', 'Hungaroring', 'Nürburgring', 'Hockenheim'
        ]
        
        for location in locations:
            if re.search(rf'\b{location}\b', text, re.IGNORECASE):
                return location
        
        # Look for circuit patterns
        circuit_patterns = [
            r'Autódromo\s+([A-Za-z\s]+)',
            r'Circuito\s+([A-Za-z\s]+)',
            r'Circuit\s+([A-Za-z\s]+)',
            r'em\s+([A-Za-z\s]+)',
            r'@\s*([A-Za-z\s]+)'
        ]
        
        for pattern in circuit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1):
                location = match.group(1).strip()
                if len(location) > 2:
                    return location
        
        return None
    
    def _extract_session_type(self, text: str) -> str:
        """Extract session type from text."""
        session_patterns = {
            'qualifying': [r'quali|classificação|classification'],
            'practice': [r'treino|practice|fp\d+|free\s*practice'],
            'sprint': [r'sprint|corrida\s*sprint'],
            'race': [r'corrida|race|gp|grand\s*prix|grande\s*prêmio']
        }
        
        for session_type, patterns in session_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return session_type
        
        return 'race'  # Default to race
    
    def _extract_streaming_links(self, element) -> List[str]:
        """Extract streaming links from element."""
        links = []
        
        # Look for links in the element
        link_elements = element.find_all('a', href=True)
        for link in link_elements:
            href = link['href']
            text = link.get_text(strip=True).lower()
            
            # Check if it's a streaming link
            streaming_indicators = [
                'assista', 'watch', 'stream', 'ao vivo', 'live',
                'sportv', 'globo', 'espn', 'fox', 'youtube',
                'f1tv', 'motogp', 'motorsport'
            ]
            
            if any(indicator in text for indicator in streaming_indicators):
                if href.startswith('http'):
                    links.append(href)
                else:
                    links.append(urljoin(self.get_base_url(), href))
        
        return links
    
    def _extract_official_url(self, element) -> Optional[str]:
        """Extract official event URL from element."""
        # Look for main event link
        main_link = element.find('a', href=True)
        if main_link:
            href = main_link['href']
            if href.startswith('http'):
                return href
            else:
                return urljoin(self.get_base_url(), href)
        
        return None
    
    def _collect_from_categories(self, target_date: datetime) -> List[Dict[str, Any]]:
        """
        Collect events from specific category pages.
        
        Args:
            target_date: Target date for collection
            
        Returns:
            List of raw event dictionaries
        """
        events = []
        
        # Category pages to check
        category_pages = [
            '/formula-1',
            '/f1',
            '/motogp',
            '/stock-car',
            '/nascar',
            '/indycar',
            '/wec',
            '/rally'
        ]
        
        for page in category_pages:
            try:
                url = urljoin(self.get_base_url(), page)
                response = self.make_request(url)
                if response:
                    page_events = self._parse_calendar_page(response.text, target_date)
                    events.extend(page_events)
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"⚠️ Error collecting from category page {page}: {e}")
        
        return events
    
    def _parse_text_content(self, html_content: str, target_date: datetime) -> List[Dict[str, Any]]:
        """
        Parse text content when structured parsing fails.
        
        Args:
            html_content: HTML content
            target_date: Target date
            
        Returns:
            List of events extracted from text
        """
        events = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get all text content
        text_content = soup.get_text(separator='\n', strip=True)
        lines = text_content.split('\n')
        
        current_event = {}
        
        for line in lines:
            if line is not None:
                line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Look for motorsport keywords
            motorsport_keywords = [
                'f1', 'formula', 'fórmula', 'motogp', 'moto', 'stock car',
                'nascar', 'indycar', 'rally', 'corrida', 'race', 'gp',
                'grand prix', 'grande prêmio', 'campeonato', 'championship'
            ]
            
            if any(keyword in line.lower() for keyword in motorsport_keywords):
                # Try to extract event from this line
                event = self._extract_event_from_text_line(line)
                if event:
                    events.append(event)
        
        return events
    
    def _extract_event_from_text_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Extract event from a single text line."""
        try:
            event_name = self._extract_event_name(line)
            event_date = self._extract_date(line)
            event_time = self._extract_time(line)
            category = self._extract_category(line)
            location = self._extract_location(line)
            
            if event_name and (event_date or category):
                return {
                    'name': event_name,
                    'category': category or 'Unknown',
                    'date': event_date,
                    'time': event_time,
                    'location': location,
                    'country': 'Brasil',
                    'session_type': self._extract_session_type(line),
                    'streaming_links': [],
                    'official_url': '',
                    'raw_text': line
                }
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Error extracting from text line: {e}")
        
        return None
