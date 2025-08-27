"""
Event Processor for Motorsport Calendar

Handles event normalization, deduplication, weekend detection,
and data quality validation for collected motorsport events.
"""

import re
from datetime import datetime, timedelta, tzinfo
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import defaultdict
import hashlib
from pathlib import Path

import numpy as np
from unidecode import unidecode
from src.silent_period import SilentPeriodManager
from src.ai.embeddings_service import EmbeddingsService, EmbeddingsConfig
from src.utils import AnomalyDetector, AnomalyConfig


class _TzWithZone(tzinfo):
    """Wrapper for tzinfo that adds a 'zone' attribute expected by tests.

    Delegates tz behavior to an underlying tzinfo (e.g., zoneinfo.ZoneInfo),
    while exposing a 'zone' attribute with the provided timezone name.
    """
    def __init__(self, base_tz: tzinfo, name: str):
        self._base = base_tz
        self.zone = name

    def utcoffset(self, dt: Optional[datetime]) -> Optional["timedelta"]:
        return self._base.utcoffset(dt)  # type: ignore[attr-defined]

    def dst(self, dt: Optional[datetime]) -> Optional["timedelta"]:
        return self._base.dst(dt)  # type: ignore[attr-defined]

    def tzname(self, dt: Optional[datetime]) -> Optional[str]:
        try:
            return self._base.tzname(dt)  # type: ignore[attr-defined]
        except Exception:
            return self.zone


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
        
        # Initialize silent period manager
        self.silent_period_manager = SilentPeriodManager(config_manager, logger)
        
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
        # Defaults para AI (compat com instâncias sem ConfigManager)
        self.ai_enabled: bool = False
        self.ai_dedup_threshold: float = 0.85
        self._ai_cfg: Dict[str, Any] = {}

        self._load_config()
        
        # AI/Embeddings
        self._embeddings_service: Optional[EmbeddingsService] = None
        # Anomaly detection (opcional)
        self._anomaly_cfg: AnomalyConfig = AnomalyConfig()
        self._anomaly_detector: Optional[AnomalyDetector] = None
        
    def _fuzzy_ratio(self, a: str, b: str) -> int:
        """Dynamic fuzzy ratio to allow test stubs to override fuzzywuzzy.

        Tries to import the current 'fuzzywuzzy' module from sys.modules using
        importlib, so tests that inject a stub before calling this method take effect
        even if this module was imported earlier in the test session.
        """
        try:
            import importlib
            fw = importlib.import_module('fuzzywuzzy')
            fuzz_mod = getattr(fw, 'fuzz', None)
            if fuzz_mod and hasattr(fuzz_mod, 'ratio'):
                return int(fuzz_mod.ratio(a, b))
        except Exception:
            pass
        # Fallback to a direct import path if available
        try:
            from fuzzywuzzy import fuzz as _fuzz  # type: ignore
            return int(_fuzz.ratio(a, b))
        except Exception:
            # Ultimate fallback: simple equality check (coarse)
            return 100 if str(a) == str(b) else 0

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

        # AI settings (validated em ConfigManager.validate_config via validate_ai_config)
        try:
            ai_cfg = self.config.get('ai', {})
        except Exception:
            ai_cfg = {}
        self.ai_enabled: bool = bool(ai_cfg.get('enabled', False))
        thresholds = ai_cfg.get('thresholds', {}) or {}
        try:
            self.ai_dedup_threshold: float = float(thresholds.get('dedup', 0.85))
        except Exception:
            self.ai_dedup_threshold = 0.85
        self._ai_cfg: Dict[str, Any] = ai_cfg

        # Quality/Anomaly settings (opcionais, não bloqueantes)
        try:
            q = self.config.get('quality', {}) or {}
            ad = q.get('anomaly_detection', {}) or {}
            enabled = bool(ad.get('enabled', False))
            min_h = int(ad.get('hours', {}).get('min', 6) if isinstance(ad.get('hours', {}), dict) else ad.get('min_hour', 6))
            max_h = int(ad.get('hours', {}).get('max', 23) if isinstance(ad.get('hours', {}), dict) else ad.get('max_hour', 23))
            examples = int(ad.get('examples_per_type', 3))
            self._anomaly_cfg = AnomalyConfig(enabled=enabled, min_hour=min_h, max_hour=max_h, examples_per_type=examples)
        except Exception:
            # Mantém defaults seguros
            self._anomaly_cfg = AnomalyConfig()

    def _get_embeddings_service(self) -> EmbeddingsService:
        """Lazy-inicializa e retorna o EmbeddingsService conforme config ai.*"""
        if self._embeddings_service is not None:
            return self._embeddings_service
        ai = self._ai_cfg or {}
        cache = ai.get('cache', {}) or {}
        emb = ai.get('embeddings', {}) or {}
        try:
            cfg = EmbeddingsConfig(
                enabled=self.ai_enabled,
                device=str(ai.get('device', 'cpu')),
                batch_size=int(ai.get('batch_size', 16)),
                backend=str(emb.get('backend', 'hashing')),
                dim=int(emb.get('dim', 256)),
                lru_capacity=int(emb.get('lru_capacity', 10000)),
                cache_dir=Path(str(cache.get('dir', 'cache/embeddings'))),
                ttl_days=int(cache.get('ttl_days', 30)),
            )
        except Exception:
            # Fallback seguro
            cfg = EmbeddingsConfig()
        self._embeddings_service = EmbeddingsService(cfg)
        return self._embeddings_service
    
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
        # Normalize target_weekend: accept either a weekend tuple or a single datetime
        if isinstance(target_weekend, datetime):
            # Convert provided date into the configured weekend window
            dt = target_weekend
            # Localize/convert to configured timezone if needed
            try:
                import pytz
                tz_name = self.config.get_timezone() if self.config else 'America/Sao_Paulo'
                tz = pytz.timezone(tz_name)
                if dt.tzinfo is None:
                    dt = tz.localize(dt)
                else:
                    dt = dt.astimezone(tz)
            except Exception:
                # Fallback: keep original dt if timezone handling fails
                pass
            
            event_weekday = dt.weekday()
            if event_weekday >= self.weekend_start_day:
                days_to_start = event_weekday - self.weekend_start_day
                weekend_start = dt - timedelta(days=days_to_start)
            else:
                days_until_start = self.weekend_start_day - event_weekday
                weekend_start = dt + timedelta(days=days_until_start)
            weekend_end = weekend_start + timedelta(days=self.weekend_end_day - self.weekend_start_day)
            # Extend boundaries with configured hours
            weekend_start = weekend_start - timedelta(hours=self.extend_weekend_hours)
            weekend_end = weekend_end + timedelta(hours=self.extend_weekend_hours)
            target_weekend = (weekend_start, weekend_end)
        elif isinstance(target_weekend, tuple) and len(target_weekend) == 2:
            # Ensure weekend tuple datetimes are timezone-aware
            start, end = target_weekend
            try:
                import pytz
                tz_name = self.config.get_timezone() if self.config else 'America/Sao_Paulo'
                tz = pytz.timezone(tz_name)
                if isinstance(start, datetime) and start.tzinfo is None:
                    start = tz.localize(start)
                if isinstance(end, datetime) and end.tzinfo is None:
                    end = tz.localize(end)
                target_weekend = (start, end)
            except Exception:
                # If localization fails, proceed as-is
                pass

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
        
        # Step 6: Apply silent period filtering
        final_events, filtered_events = self.silent_period_manager.filter_events(validated_events)
        self.processing_stats['events_silent_filtered'] = len(filtered_events)
        self.processing_stats['events_final'] = len(final_events)
        
        # Log silent period filtering summary
        if filtered_events:
            self.silent_period_manager.log_filtering_summary(filtered_events)
        
        # Update final statistics
        self.processing_stats['processing_end_time'] = datetime.now().isoformat()

        # Optional: anomaly detection summary (não bloqueante)
        try:
            self._log_anomalies_summary(final_events, target_weekend)
        except Exception:
            # Nunca bloquear o pipeline por causa de relatório de anomalias
            pass

        # Log processing summary
        self._log_processing_summary()
        
        return final_events

    def _get_anomaly_detector(self) -> AnomalyDetector:
        if self._anomaly_detector is None:
            self._anomaly_detector = AnomalyDetector(self._anomaly_cfg)
        return self._anomaly_detector

    def _log_anomalies_summary(self, events: List[Dict[str, Any]], target_weekend: Optional[Tuple[datetime, datetime]]) -> None:
        # Apenas se habilitado
        if not isinstance(self._anomaly_cfg, AnomalyConfig) or not self._anomaly_cfg.enabled:
            return
        detector = self._get_anomaly_detector()
        report = detector.evaluate(events, target_weekend=target_weekend)
        detector.log_summary(report, logger=self.logger)
    
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
        # Preserve original name for display
        original_name = event.get('name', '')

        # Create normalized event structure
        normalized = {
            'event_id': event.get('event_id', self._generate_event_id(event)),
            'name': self._normalize_name(original_name),
            'display_name': str(original_name).strip(),
            'raw_category': self._normalize_category(event.get('raw_category', event.get('category', ''))),
            'detected_category': None,  # Will be filled by category detector
            'date': self._normalize_date(event.get('date')),
            'time': self._normalize_time(event.get('time')),
            'datetime': None,  # Will be computed from date/time
            'timezone': (event.get('timezone') or (self.config.get_timezone() if self.config else 'America/Sao_Paulo')),
            'location': self._normalize_location(event.get('location', '')),
            'country': self._normalize_country(event.get('country', '')),
            'session_type': self._normalize_session_type(event.get('session_type', 'race')),
            'streaming_links': self._normalize_streaming_links(event.get('streaming_links', [])),
            'official_url': event.get('official_url', ''),
            'source': event.get('source', 'unknown'),
            'source_display_name': event.get('source_display_name', 'XXUnknown SourceXX'),
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
        """Normalize event name: lowercase, unaccented, condensed spaces, common aliases."""
        if not name:
            return ""
        s = unidecode(str(name)).lower().strip()
        # Normalize dashes and multiple spaces
        s = s.replace('–', '-')
        s = re.sub(r'\s+', ' ', s)
        # Common aliases
        s = s.replace('formula1', 'formula 1').replace('formula-1', 'formula 1')
        s = re.sub(r'\bf-?1\b', 'formula 1', s)
        return s

    def _normalize_category(self, category: str) -> str:
        """Normalize category to a canonical display form (e.g., 'Formula 1')."""
        if not category:
            return ""
        c = unidecode(str(category)).strip().lower()
        category_map = {
            'f1': 'Formula 1',
            'formula1': 'Formula 1',
            'formula-1': 'Formula 1',
            'formula 1': 'Formula 1',
            'f2': 'Formula 2',
            'formula 2': 'Formula 2',
            'f3': 'Formula 3',
            'formula 3': 'Formula 3',
            'motogp': 'MotoGP',
            'moto gp': 'MotoGP',
            'moto2': 'Moto2',
            'moto 2': 'Moto2',
            'moto3': 'Moto3',
            'moto 3': 'Moto3',
            'stockcar': 'Stock Car',
            'stock-car': 'Stock Car',
            'stock car': 'Stock Car',
            'nascar': 'NASCAR',
            'indycar': 'IndyCar',
            'indy car': 'IndyCar',
            'wec': 'WEC',
            'wsbk': 'WSBK',
            'wrc': 'WRC',
            'formulae': 'Formula E',
            'formula-e': 'Formula E',
            'formula e': 'Formula E',
        }
        return category_map.get(c, str(category).strip())
    
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
            # If a datetime is provided, extract time
            if isinstance(time_value, datetime):
                return time_value.strftime('%H:%M')

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

    def _compute_datetime(self, date_str: Optional[str], time_str: Optional[str], timezone_str: Optional[str]) -> Optional[datetime]:
        """Compute timezone-aware datetime from date, time and timezone strings."""
        if not date_str:
            return None

        dt_str = date_str
        if time_str:
            dt_str += f" {time_str}"

        # Parse datetime
        dt: Optional[datetime] = None
        try:
            try:
                from dateutil import parser  # type: ignore
                dt = parser.parse(dt_str)
            except ImportError:
                # Fallback if dateutil is not installed
                if time_str:
                    try:
                        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                    except ValueError:
                        dt = None
                if dt is None:
                    try:
                        dt = datetime.strptime(dt_str, "%Y-%m-%d")
                    except ValueError:
                        return None
        except Exception:
            return None

        # If time was not provided, default to 12:00 (noon) for better midpoint semantics
        if not time_str:
            try:
                dt = dt.replace(hour=12, minute=0, second=0, microsecond=0)
            except Exception:
                pass

        # Apply timezone if possible
        tz_name = timezone_str or (self.config.get_timezone() if self.config else 'America/Sao_Paulo')
        try:
            import pytz  # type: ignore
            tz = pytz.timezone(tz_name)
            if dt.tzinfo is None:
                dt = tz.localize(dt)
            else:
                dt = dt.astimezone(tz)
        except ImportError:
            # Fallback to zoneinfo (Python 3.9+)
            try:
                from zoneinfo import ZoneInfo  # type: ignore
                base_tz = ZoneInfo(tz_name)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=_TzWithZone(base_tz, tz_name))
                else:
                    dt = dt.astimezone(base_tz)
                    # Ensure tzinfo has 'zone' attribute for test compatibility
                    dt = dt.replace(tzinfo=_TzWithZone(base_tz, tz_name))
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"Failed to compute datetime: timezone fallback failed for '{tz_name}': {e}")
                return None
        except Exception as e:
            # pytz is available but timezone lookup/localization failed
            if self.logger:
                self.logger.debug(f"Failed to compute datetime: timezone '{tz_name}' invalid or localization failed: {e}")
            return None

        return dt

    def _normalize_location(self, location: str) -> str:
        """Normalize location name to a canonical form when possible."""
        if not location:
            return ""

        raw = str(location).strip()
        key = unidecode(raw).lower()

        location_map = {
            'interlagos': 'Autódromo José Carlos Pace (Interlagos)',
            'jacarepagua': 'Autódromo Internacional Nelson Piquet',
            'silverstone': 'Silverstone Circuit',
            'monza': 'Autodromo Nazionale di Monza',
            'spa': 'Circuit de Spa-Francorchamps',
            'monaco': 'Circuit de Monaco',
            'suzuka': 'Suzuka International Racing Course',
        }

        return location_map.get(key, raw)
    
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
    
    def _normalize_streaming_links(self, links: List[Any]) -> List[str]:
        """Normalize streaming links from various formats.
        
        Accepts both dictionary format ({'name': 'X', 'url': 'Y'}) 
        and string format ('http://...').
        
        Args:
            links: List of streaming links in various formats
            
        Returns:
            List of normalized URL strings
        """
        if not links:
            return []
        
        normalized_links = []
        for link in links:
            url = None
            
            # Handle dictionary format: {'name': 'SITE BAND', 'url': 'http://...'}
            if isinstance(link, dict):
                url = link.get('url', '')
            # Handle string format: 'http://...'
            elif isinstance(link, str):
                url = link.strip()
            
            # Validate and add URL
            if url and isinstance(url, str) and url.strip():
                url = url.strip()
                if url.startswith('http'):
                    normalized_links.append(url)
        
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
            # If no category detector, use raw categories (fallback to 'category')
            # and normalize to lowercase to align with test expectations.
            for event in events:
                raw_cat = event.get('raw_category') or event.get('category') or 'Unknown'
                event['detected_category'] = str(raw_cat).strip().lower() or 'unknown'
            return events
        
        if self.logger:
            self.logger.debug("🏷️ Detecting event categories...")
        
        # Batch detect categories using full event dictionaries (enables context-aware detection)
        detected_categories = self.category_detector.detect_categories_batch(events)
        
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
            # Default to next weekend (timezone-aware)
            import pytz
            tz_name = self.config.get_timezone() if self.config else 'America/Sao_Paulo'
            tz = pytz.timezone(tz_name)
            today = datetime.now(tz)
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
        # Check datetime similarity (guard-rail)
        dt1 = event1.get('datetime')
        dt2 = event2.get('datetime')
        
        if dt1 and dt2:
            time_diff = abs((dt1 - dt2).total_seconds()) / 60  # minutes
            if time_diff > self.time_tolerance_minutes:
                return False

        # Check category similarity (guard-rail)
        cat1 = event1.get('detected_category', '').lower()
        cat2 = event2.get('detected_category', '').lower()
        
        if cat1 and cat2:
            cat_similarity = self._fuzzy_ratio(cat1, cat2)
            if cat_similarity < self.category_similarity_threshold:
                return False

        # Check location similarity (guard-rail)
        loc1 = event1.get('location', '').lower()
        loc2 = event2.get('location', '').lower()
        
        if loc1 and loc2:
            loc_similarity = self._fuzzy_ratio(loc1, loc2)
            if loc_similarity < self.location_similarity_threshold:
                return False

        # If AI disabled, fallback to original fuzzy name thresholding
        name1 = unidecode(event1.get('name', '')).lower()
        name2 = unidecode(event2.get('name', '')).lower()
        if not self.ai_enabled:
            name_similarity = self._fuzzy_ratio(name1, name2)
            # similarity_threshold may be configured as 0..1 or 0..100; normalize
            thresh = self.similarity_threshold
            try:
                thresh = float(thresh)
            except Exception:
                thresh = 85.0
            if thresh <= 1.0:
                thresh = thresh * 100.0
            return float(name_similarity) >= thresh

        # AI enabled: compute composite score (fuzzy + semantic)
        fuzzy_name_norm = (self._fuzzy_ratio(name1, name2) / 100.0) if (name1 or name2) else 0.0

        # Prepare semantic pairs (only if non-empty)
        texts: List[str] = []
        idx = {}
        if name1 and name2:
            idx['name'] = (len(texts), len(texts) + 1)
            texts.extend([name1, name2])
        if loc1 and loc2:
            idx['loc'] = (len(texts), len(texts) + 1)
            texts.extend([loc1, loc2])

        semantic_vals: List[float] = []
        if texts:
            try:
                vecs = self._get_embeddings_service().embed_texts(texts)
                np_vecs = [np.asarray(v, dtype=np.float32) for v in vecs]
                if 'name' in idx:
                    i, j = idx['name']
                    a, b = np_vecs[i], np_vecs[j]
                    semantic_vals.append(float(np.dot(a, b)))
                if 'loc' in idx:
                    i, j = idx['loc']
                    a, b = np_vecs[i], np_vecs[j]
                    semantic_vals.append(float(np.dot(a, b)))
            except Exception:
                # Em caso de falha na IA, ignorar componente semântico
                pass

        semantic_mean = float(np.mean(semantic_vals)) if semantic_vals else 0.0
        # Pesos iniciais 50/50 entre fuzzy e semântico
        score = 0.5 * fuzzy_name_norm + 0.5 * semantic_mean
        
        return score >= self.ai_dedup_threshold
    
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
                bool(e.get('official_url', '')),
                # Deterministic final tie-breaker to ensure stability across runs
                str(e.get('event_id', ''))
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
        
        # Include silent period filtering in summary
        final_count = stats.get('events_final', stats['events_validated'])
        silent_filtered = stats.get('events_silent_filtered', 0)
        
        summary_msg = (
            f"📊 Processing Summary: "
            f"{stats['events_input']} → {final_count} events "
            f"({stats['duplicates_removed']} duplicates removed"
        )
        
        if silent_filtered > 0:
            summary_msg += f", {silent_filtered} silent period filtered"
        
        summary_msg += f", {stats['categories_detected']} categories detected)"
        
        self.logger.log_step(summary_msg)
        
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
