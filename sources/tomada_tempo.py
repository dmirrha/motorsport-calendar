"""
Tomada de Tempo Source for Motorsport Calendar

Primary data source scraper for tomadadetempo.com.br - the most comprehensive
Brazilian motorsport calendar website with complete schedules and streaming info.
"""

import re
import time
import random
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from bs4 import BeautifulSoup, Tag
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
        
    def _make_request_with_retry(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        Make an HTTP request with retry logic.
        
        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional arguments for requests.request()
            
        Returns:
            Response object or None if all retries fail
        """
        max_retries = self.retry_attempts or 3
        retry_delays = [1, 3, 5]  # seconds
        
        for attempt in range(max_retries):
            try:
                # Add random user agent
                headers = kwargs.get('headers', {})
                if 'User-Agent' not in headers:
                    headers['User-Agent'] = random.choice(self.user_agents)
                kwargs['headers'] = headers
                
                # Make the request
                response = requests.request(method, url, timeout=self.timeout, **kwargs)
                response.raise_for_status()
                return response
                
            except (requests.RequestException, ConnectionError) as e:
                if attempt == max_retries - 1:  # Last attempt
                    if self.logger:
                        self.logger.error(f"Request failed after {max_retries} attempts: {str(e)}")
                    return None
                
                # Calculate delay with exponential backoff
                delay = retry_delays[attempt] if attempt < len(retry_delays) else retry_delays[-1]
                if self.logger:
                    self.logger.warning(
                        f"Request failed (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {delay}s... Error: {str(e)}"
                    )
                
                time.sleep(delay + random.uniform(0, 1))  # Add jitter
        
        return None
        
    def _parse_event_date(self, date_str: str, reference_date: Optional[datetime] = None) -> Optional[datetime]:
        """
        Parse date string from Tomada de Tempo format to datetime.
        
        Args:
            date_str: Date string in formats like "Sáb, 15/11 - 14:00" or "14:30"
            reference_date: Reference date to use when only time is provided
            
        Returns:
            datetime object or None if parsing fails
        """
        if not date_str or not date_str.strip():
            return None
            
        date_str = date_str.strip()
        
        # Try to parse full format: "Sáb, 15/11 - 14:00"
        try:
            # Remove day of week if present
            if ',' in date_str:
                date_str = date_str.split(',', 1)[1].strip()
            
            # Split date and time
            if '-' in date_str:
                date_part, time_part = date_str.split('-', 1)
                date_part = date_part.strip()
                time_part = time_part.strip()
                
                # Parse date (assuming current year if not specified)
                day, month = map(int, date_part.split('/'))
                hour, minute = map(int, time_part.split(':'))
                
                # Use reference date or current date
                ref_date = reference_date or datetime.now()
                year = ref_date.year
                
                # Handle year transition (e.g., if it's December and we're parsing January)
                if month == 1 and ref_date.month == 12:
                    year += 1
                
                return datetime(year, month, day, hour, minute)
                
            # Try to parse time only format: "14:30"
            elif ':' in date_str and reference_date is not None:
                hour, minute = map(int, date_str.split(':'))
                return reference_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
        except (ValueError, IndexError) as e:
            if self.logger:
                self.logger.warning(f"Failed to parse date string '{date_str}': {str(e)}")
            
        return None
    
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
            
            # NEW APPROACH: Find and access the specific weekend programming link
            weekend_programming_events = self._collect_from_weekend_programming(target_date)
            events.extend(weekend_programming_events)
            
            # Only use fallback methods if we didn't find the weekend programming page
            if not events:
                if self.logger:
                    self.logger.debug("🔍 Weekend programming link not found, falling back to alternative methods")
                
                # Collect from main calendar page
                calendar_events = self._collect_from_calendar(target_date)
                events.extend(calendar_events)
                
                # Only use category pages as last resort
                if not events:
                    if self.logger:
                        self.logger.debug("📋 Using category pages as last resort")
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
    
    def _collect_from_weekend_programming(self, target_date: datetime) -> List[Dict[str, Any]]:
        """
        Find and collect events from the specific weekend programming page.
        
        Args:
            target_date: Target date for collection
            
        Returns:
            List of raw event dictionaries from the weekend programming page
        """
        events = []
        
        try:
            # Get the main page first
            response = self.make_request(self.get_base_url())
            if not response:
                if self.logger:
                    self.logger.debug("⚠️ Failed to load main page for weekend programming link search")
                return events
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Format target date for link matching
            weekend_date_formats = [
                target_date.strftime("%d/%m/%Y"),  # 01/08/2025
                target_date.strftime("%d/%m"),     # 01/08
                target_date.strftime("%d de %B"),  # 01 de agosto
                target_date.strftime("%d-%m-%Y"),  # 01-08-2025
            ]
            
            # Look for links containing "PROGRAMAÇÃO DA TV E INTERNET" and weekend date
            programming_link = None
            programming_text = None
            
            # Search in all links on the page
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                link_text = link.get_text(strip=True)
                link_href = link.get('href', '')
                
                # Check if link contains the programming text
                if "PROGRAMAÇÃO DA TV E INTERNET" in link_text.upper():
                    # Check if it contains any of the weekend date formats
                    for date_format in weekend_date_formats:
                        if date_format in link_text:
                            programming_link = urljoin(self.get_base_url(), link_href)
                            programming_text = link_text
                            if self.logger:
                                self.logger.debug(f"🎯 Found weekend programming link: {programming_text} -> {programming_link}")
                            break
                    
                    if programming_link:
                        break
            
            # If no exact date match, look for any "PROGRAMAÇÃO DA TV E INTERNET" link
            if not programming_link:
                for link in all_links:
                    link_text = link.get_text(strip=True)
                    link_href = link.get('href', '')
                    
                    if "PROGRAMAÇÃO DA TV E INTERNET" in link_text.upper():
                        programming_link = urljoin(self.get_base_url(), link_href)
                        programming_text = link_text
                        if self.logger:
                            self.logger.debug(f"📺 Found general programming link: {programming_text} -> {programming_link}")
                        break
            
            # Access the programming page if found
            if programming_link:
                if self.logger:
                    self.logger.debug(f"🌐 Accessing weekend programming page: {programming_link}")
                
                programming_response = self.make_request(programming_link)
                if programming_response:
                    # Parse the programming page
                    programming_events = self._parse_calendar_page(
                        programming_response.text, 
                        target_date, 
                        programming_response.url
                    )
                    events.extend(programming_events)
                    
                    if self.logger:
                        self.logger.debug(f"✅ Extracted {len(programming_events)} events from weekend programming page")
                else:
                    if self.logger:
                        self.logger.debug("⚠️ Failed to load weekend programming page")
            else:
                if self.logger:
                    self.logger.debug("🔍 No weekend programming link found on main page")
                    
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Error collecting from weekend programming: {e}")
        
        return events

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
            # Make request to calendar page
            response = self.make_request(self.get_base_url())
            if response:
                events = self._parse_calendar_page(response.text, target_date, response.url)
                
        except Exception as e:
            error_msg = f"Failed to collect from calendar: {e}"
            if self.logger:
                self.logger.debug(f"⚠️ Error collecting from calendar: {e}")
        
        return events
    
    def _parse_calendar_page(self, html_content: str, target_date: datetime, page_url: str = None) -> List[Dict[str, Any]]:
        """
        Parse calendar page HTML to extract events.
        
        Args:
            html_content: HTML content of the page
            target_date: Target date for filtering
            page_url: URL of the page being parsed
            
        Returns:
            List of event dictionaries
        """
        events = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract programming context (weekend dates) from page title or URL
            programming_context = self._extract_programming_context(soup, page_url)
            
            # FIRST: Try to parse the specific weekend programming structure
            weekend_events = self._parse_weekend_programming_structure(soup, target_date, programming_context)
            if weekend_events:
                events.extend(weekend_events)
                if self.logger:
                    self.logger.debug(f"✅ Extracted {len(weekend_events)} events from weekend programming structure")
            
            # FALLBACK: If no weekend programming found, try common selectors
            if not events:
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
                            event = self._extract_event_from_element(element, target_date, programming_context)
                            if event:
                                events.append(event)
                        break  # Use first successful selector
            
            # LAST RESORT: If no structured events found, try text parsing
            if not events:
                events = self._parse_text_content(html_content, target_date, programming_context)
                
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Error parsing calendar page: {e}")
        
        return events
    
    def _parse_weekend_programming_structure(self, soup, target_date: datetime, programming_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Parse the specific weekend programming structure with h5 headers and ul/li lists.
        
        Args:
            soup: BeautifulSoup object of the page
            target_date: Target date for filtering
            programming_context: Programming context information
            
        Returns:
            List of event dictionaries
        """
        events = []
        
        try:
            # Look for the programming section header
            programming_header = soup.find('h5', string=lambda text: text and 'HORÁRIOS, PROGRAMAÇÃO E ONDE ASSISTIR' in text.upper())
            
            if not programming_header:
                # Try alternative header patterns
                programming_header = soup.find('h5', string=lambda text: text and 'PROGRAMAÇÃO' in text.upper())
            
            if programming_header:
                if self.logger:
                    self.logger.debug(f"📅 Found programming header: {programming_header.get_text()}")
                
                # Find all content after the header until next major section
                current_element = programming_header.next_sibling
                current_date = None
                
                while current_element:
                    if hasattr(current_element, 'name'):
                        # Check for date headers (like "SEXTA-FEIRA – 01/08/2025")
                        if current_element.name in ['p', 'h6', 'strong'] and current_element.get_text():
                            text = current_element.get_text(strip=True)
                            
                            # Look for date patterns
                            date_patterns = [
                                r'(SEXTA-FEIRA|SÁBADO|DOMINGO)\s*[–-]\s*(\d{2}/\d{2}/\d{4})',
                                r'(SEXTA|SÁBADO|DOMINGO)\s*[–-]\s*(\d{2}/\d{2}/\d{4})',
                                r'(\d{2}/\d{2}/\d{4})'
                            ]
                            
                            for pattern in date_patterns:
                                match = re.search(pattern, text)
                                if match:
                                    try:
                                        if len(match.groups()) >= 2:
                                            date_str = match.group(2)
                                        else:
                                            date_str = match.group(1)
                                        
                                        current_date = datetime.strptime(date_str, '%d/%m/%Y').date()
                                        if self.logger:
                                            self.logger.debug(f"📅 Found date section: {current_date}")
                                        break
                                    except ValueError:
                                        continue
                        
                        # Parse event lists (ul elements)
                        elif current_element.name == 'ul':
                            if current_date:
                                list_events = self._parse_event_list(current_element, current_date, programming_context)
                                events.extend(list_events)
                                
                                if self.logger and list_events:
                                    self.logger.debug(f"🎯 Extracted {len(list_events)} events from {current_date}")
                        
                        # Stop at next major section
                        elif current_element.name in ['h1', 'h2', 'h3', 'h4', 'h5'] and current_element != programming_header:
                            break
                    
                    current_element = current_element.next_sibling
            
            else:
                if self.logger:
                    self.logger.debug("📅 No weekend programming header found")
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Error parsing weekend programming structure: {e}")
        
        return events

    def _parse_event_list(self, ul_element, event_date, programming_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Parse a ul element containing motorsport events.
        
        Args:
            ul_element: BeautifulSoup ul element
            event_date: Date for the events in this list
            programming_context: Programming context information
            
        Returns:
            List of event dictionaries
        """
        events = []
        
        try:
            for li in ul_element.find_all('li'):
                li_text = li.get_text(strip=True)
                
                if li_text and len(li_text) > 10:
                    event = self._parse_event_from_li(li, li_text, event_date, programming_context)
                    if event:
                        events.append(event)
        
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Error parsing event list: {e}")
        
        return events

    def _parse_event_from_li(self, li_element, li_text: str, event_date, programming_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Parse a single li element to extract event information.
        
        Args:
            li_element: BeautifulSoup li element
            li_text: Text content of the li element
            event_date: Date for this event
            programming_context: Programming context information
            
        Returns:
            Event dictionary or None
        """
        try:
            # Extract time (e.g., "04:55", "08:30")
            time_match = re.search(r'(\d{1,2}[:\.]\d{2})', li_text)
            event_time = time_match.group(1).replace('.', ':') if time_match else None
            
            # Extract category/name (e.g., "FÓRMULA 1", "NASCAR CUP")
            category_match = re.search(r'(\d{1,2}[:\.]\d{2})\s*[–-]?\s*([^–-]+?)(?:\s*[–-]|$)', li_text)
            if category_match:
                event_name = category_match.group(2).strip()
            else:
                # Fallback: try to extract from strong tags
                strong_tags = li_element.find_all('strong')
                if strong_tags:
                    event_name = strong_tags[0].get_text(strip=True)
                    # Remove time from the beginning if present
                    event_name = re.sub(r'^\d{1,2}[:\.]\d{2}\s*[–-]?\s*', '', event_name)
                else:
                    return None
            
            # Clean up event name
            event_name = event_name.strip(' –-')
            if not event_name:
                return None
            
            # Extract location (e.g., "GP da Hungria", "Curvelo/MG")
            location_match = re.search(r'[–-]\s*([^–-]+?)\s*[–-]', li_text)
            location = location_match.group(1).strip() if location_match else None
            
            # Extract category from event name
            category = self._extract_category(event_name)
            
            # Extract streaming links
            streaming_links = []
            for link in li_element.find_all('a', href=True):
                link_text = link.get_text(strip=True)
                link_url = link.get('href')
                if link_url and link_text:
                    streaming_links.append({
                        'name': link_text,
                        'url': link_url
                    })
            
            # Create event dictionary
            event = {
                'name': event_name,
                'category': category or 'Unknown',
                'date': event_date.strftime('%Y-%m-%d') if event_date else None,
                'time': event_time,
                'location': location,
                'country': 'Brasil',
                'session_type': self._extract_session_type(li_text),
                'streaming_links': streaming_links,
                'official_url': '',
                'raw_text': li_text,
                'from_weekend_programming': True
            }
            
            if self.logger:
                self.logger.debug(f"🎯 Parsed event: {event_name} at {event_time} on {event_date}")
            
            return event
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Error parsing event from li: {e}")
            return None

    def _extract_programming_context(self, soup, page_url: str = None) -> Dict[str, Any]:
        """
        Extract programming context (weekend dates and period) from page title or URL.
        
        Args:
            soup: BeautifulSoup object of the page
            page_url: URL of the page being parsed
            
        Returns:
            Dictionary with programming context (start_date, end_date, weekend_dates)
        """
        context = {
            'start_date': None,
            'end_date': None,
            'weekend_dates': [],
            'programming_title': None
        }
        
        try:
            # Extract from page title
            title_element = soup.find('title')
            if title_element:
                title = title_element.get_text(strip=True)
                context['programming_title'] = title
                
                # Look for date patterns in title (e.g., "01 a 03-08-2025" or "01-03/08/2025")
                date_range_patterns = [
                    r'(\d{1,2})\s*a\s*(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})',  # "01 a 03/08/2025"
                    r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})\s*a\s*(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})',  # "01/08/2025 a 03/08/2025"
                    r'final[\s\-]*de[\s\-]*semana[\s\-]*de[\s\-]*(\d{1,2})\s*a\s*(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})'  # "final de semana de 01 a 03/08/2025"
                ]
                
                for pattern in date_range_patterns:
                    match = re.search(pattern, title, re.IGNORECASE)
                    if match:
                        groups = match.groups()
                        if len(groups) == 4:  # Pattern like "01 a 03/08/2025"
                            start_day, end_day, month, year = groups
                            try:
                                year_int = int(year) if len(year) == 4 else (2000 + int(year) if int(year) < 50 else 1900 + int(year))
                                context['start_date'] = f"{int(start_day):02d}/{int(month):02d}/{year_int}"
                                context['end_date'] = f"{int(end_day):02d}/{int(month):02d}/{year_int}"
                                
                                # Generate weekend dates list
                                start_dt = self.parse_date_time(context['start_date'])
                                end_dt = self.parse_date_time(context['end_date'])
                                if start_dt and end_dt:
                                    current_dt = start_dt
                                    while current_dt <= end_dt:
                                        context['weekend_dates'].append(current_dt.strftime("%d/%m/%Y"))
                                        current_dt += timedelta(days=1)
                                break
                            except ValueError:
                                continue
            
            # Extract from URL if available
            if page_url and not context['start_date']:
                url_date_pattern = r'(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})'
                match = re.search(url_date_pattern, page_url)
                if match:
                    year, month, day = match.groups()
                    try:
                        context['start_date'] = f"{int(day):02d}/{int(month):02d}/{int(year)}"
                        # Assume 3-day weekend (Friday to Sunday)
                        start_dt = self.parse_date_time(context['start_date'])
                        if start_dt:
                            end_dt = start_dt + timedelta(days=2)
                            context['end_date'] = end_dt.strftime("%d/%m/%Y")
                            context['weekend_dates'] = [
                                start_dt.strftime("%d/%m/%Y"),
                                (start_dt + timedelta(days=1)).strftime("%d/%m/%Y"),
                                end_dt.strftime("%d/%m/%Y")
                            ]
                    except ValueError:
                        pass
        
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Error extracting programming context: {e}")
        
        return context
    
    def _extract_event_from_element(self, element, target_date: datetime, programming_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
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
            
            # If no date found but we have programming context, try to associate event to context
            if not event_date and programming_context and programming_context.get('weekend_dates'):
                # If event has time or category, it's likely part of the weekend programming
                if event_time or category:
                    # Use the first date from weekend context as default
                    event_date = programming_context['weekend_dates'][0]
                    if self.logger:
                        self.logger.debug(f"📅 Associated event '{event_name}' to programming context date: {event_date}")
            
            # Look for streaming links
            streaming_links = self._extract_streaming_links(element)
            
            # Get official URL if available
            official_url = self._extract_official_url(element)
            
            # Accept event if it has name and either explicit date or was associated to context
            if event_name and (event_date or (programming_context and category)):
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
                    'raw_text': text_content,
                    'from_context': not bool(self._extract_date(text_content))  # Flag to indicate if date came from context
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
        # Look for weekday + date patterns (e.g., "SÁBADO – 02/08/2025")
        weekday_date_pattern = r'(?:segunda|terça|quarta|quinta|sexta|sábado|domingo|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s*[–\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})'
        match = re.search(weekday_date_pattern, text, re.IGNORECASE)
        if match:
            date_part = match.group(1)
            # Process the date part
            date_match = re.search(r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})', date_part)
            if date_match:
                day, month, year = date_match.groups()
                try:
                    day_int, month_int, year_int = int(day), int(month), int(year)
                    if len(year) == 2:
                        year_int = 2000 + year_int if year_int < 50 else 1900 + year_int
                    if 1 <= day_int <= 31 and 1 <= month_int <= 12 and year_int >= 2020:
                        return f"{day_int:02d}/{month_int:02d}/{year_int}"
                except ValueError:
                    pass
        
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
        """Extract time from text with improved format support."""
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(?:h|hrs?|horas?)?',  # 14:30, 14:30h
            r'(\d{1,2})h(\d{2})',  # 14h30
            r'(\d{1,2})h\s*(\d{2})',  # 14h 30
            r'(\d{1,2}):(\d{2})',  # 14:30
            r'(\d{1,2})\s*h\s*(\d{2})',  # 14 h 30
            r'(\d{1,2})\s*[h:]\s*(\d{2})',  # 14 h 30 or 14:30
            r'às\s*(\d{1,2})[h:]?(\d{2})?',  # às 14h30, às 14:30, às 14
            r'(\d{1,2})\s*horas?\s*(?:e\s*)?(\d{2})?',  # 14 horas, 14 horas e 30
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                hour = int(match.group(1))
                minute_group = match.group(2) if len(match.groups()) > 1 and match.group(2) else '00'
                minute = int(minute_group) if minute_group else 0
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
    
    def _parse_text_content(self, html_content: str, target_date: datetime, programming_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
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
                event = self._extract_event_from_text_line(line, programming_context)
                if event:
                    events.append(event)
        
        return events
    
    def _extract_event_from_text_line(self, line: str, programming_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Extract event from a single text line."""
        try:
            event_name = self._extract_event_name(line)
            event_date = self._extract_date(line)
            event_time = self._extract_time(line)
            category = self._extract_category(line)
            location = self._extract_location(line)
            
            # If no date found but we have programming context, try to associate event to context
            if not event_date and programming_context and programming_context.get('weekend_dates'):
                # If event has time or category, it's likely part of the weekend programming
                if event_time or category:
                    # Use the first date from weekend context as default
                    event_date = programming_context['weekend_dates'][0]
                    if self.logger:
                        self.logger.debug(f"📅 Associated text event '{event_name}' to programming context date: {event_date}")
            
            # Accept event if it has name and either explicit date or was associated to context
            if event_name and (event_date or (programming_context and category)):
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
                    'raw_text': line,
                    'from_context': not bool(self._extract_date(line))  # Flag to indicate if date came from context
                }
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Error extracting from text line: {e}")
        
        return None
