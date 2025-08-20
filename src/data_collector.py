"""
Data Collector for Motorsport Calendar

Orchestrates data collection from multiple prioritized sources,
handles source management, and coordinates the collection process.
"""

import asyncio
import concurrent.futures
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Type
import importlib
import inspect
from pathlib import Path
import time

from sources.base_source import BaseSource
from sources.tomada_tempo import TomadaTempoSource


class DataCollector:
    """Coordinates data collection from multiple motorsport sources."""
    
    def __init__(self, config_manager=None, logger=None, ui_manager=None, category_detector=None):
        """
        Initialize data collector.
        
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
        
        # Source management
        self.available_sources = {}
        self.active_sources = []
        self.source_priorities = {}
        self.excluded_sources = set()
        
        # Collection settings
        self.max_concurrent_sources = 3
        self.collection_timeout = 300  # 5 minutes
        self.retry_failed_sources = True
        self.max_retries = 1
        self.retry_backoff_seconds = 0.5
        
        # Statistics
        self.collection_stats = {
            'total_sources_attempted': 0,
            'successful_sources': 0,
            'failed_sources': 0,
            'total_events_collected': 0,
            'collection_start_time': None,
            'collection_end_time': None,
            'source_results': {}
        }
        
        # Load configuration and discover sources
        self._load_config()
        self._discover_sources()
        self._initialize_sources()
    
    def _load_config(self) -> None:
        """Load data collection configuration."""
        if not self.config:
            return
        
        data_sources_config = self.config.get_data_sources_config()
        
        # Collection settings
        self.max_concurrent_sources = data_sources_config.get('max_concurrent_sources', 3)
        self.collection_timeout = data_sources_config.get('collection_timeout_seconds', 300)
        self.retry_failed_sources = data_sources_config.get('retry_failed_sources', True)
        # Backward-compat: se max_retries não existir, usar retry_attempts
        self.max_retries = data_sources_config.get('max_retries', data_sources_config.get('retry_attempts', 1))
        self.retry_backoff_seconds = data_sources_config.get('retry_backoff_seconds', 0.5)
        
        # Source priorities from priority_order list
        priority_order = data_sources_config.get('priority_order', [])
        for i, source_name in enumerate(priority_order):
            # Higher priority for sources earlier in the list (reverse priority)
            self.source_priorities[source_name] = 100 - (i * 10)
        
        # Excluded sources list
        excluded_list = data_sources_config.get('excluded_sources', [])
        self.excluded_sources.update(excluded_list)
    
    def _discover_sources(self) -> None:
        """Discover available source classes."""
        # Built-in sources
        built_in_sources = {
            'tomada_tempo': TomadaTempoSource,
        }
        
        self.available_sources.update(built_in_sources)
        
        # Dynamically discover sources in the sources directory
        try:
            sources_dir = Path(__file__).parent.parent / 'sources'
            if sources_dir.exists():
                for source_file in sources_dir.glob('*.py'):
                    if source_file.name.startswith('_') or source_file.name == 'base_source.py':
                        continue
                    
                    module_name = source_file.stem
                    try:
                        # Import the module
                        module = importlib.import_module(f'sources.{module_name}')
                        
                        # Find source classes
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if (issubclass(obj, BaseSource) and 
                                obj != BaseSource and 
                                name.endswith('Source')):
                                
                                source_key = module_name
                                self.available_sources[source_key] = obj
                                
                                if self.logger:
                                    self.logger.debug(f"🔍 Discovered source: {name} ({source_key})")
                    
                    except Exception as e:
                        if self.logger:
                            self.logger.debug(f"⚠️ Failed to load source module {module_name}: {e}")
        
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Error discovering sources: {e}")
        
        if self.logger:
            self.logger.debug(f"📋 Available sources: {list(self.available_sources.keys())}")
    
    def _initialize_sources(self) -> None:
        """Initialize active source instances."""
        # Sort sources by priority (higher priority first)
        sorted_sources = sorted(
            self.available_sources.items(),
            key=lambda x: self.source_priorities.get(x[0], 50),
            reverse=True
        )
        
        for source_name, source_class in sorted_sources:
            if source_name in self.excluded_sources:
                if self.logger:
                    self.logger.debug(f"⏭️ Skipping excluded source: {source_name}")
                continue
            
            try:
                # Initialize source instance
                source_instance = source_class(
                    config_manager=self.config,
                    logger=self.logger,
                    ui_manager=self.ui
                )
                
                self.active_sources.append(source_instance)
                
                if self.logger:
                    self.logger.debug(f"✅ Initialized source: {source_instance.get_display_name()}")
            
            except Exception as e:
                if self.logger:
                    self.logger.log_source_error(source_name, f"Failed to initialize: {e}")
    
    def collect_events(self, target_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Collect events from all active sources.
        
        Args:
            target_date: Target date for event collection
            
        Returns:
            List of collected events from all sources
        """
        if self.logger:
            self.logger.log_step("🏁 Starting data collection from all sources")
        
        if self.ui:
            self.ui.show_step("Data Collection", "Collecting events from multiple sources...")
        
        # Initialize collection statistics
        self.collection_stats['collection_start_time'] = datetime.now().isoformat()
        self.collection_stats['total_sources_attempted'] = len(self.active_sources)
        
        all_events = []
        
        if not self.active_sources:
            if self.logger:
                self.logger.log_error("No active sources available for data collection")
            return all_events
        
        # Determine target date if not provided
        if not target_date:
            target_date = self._get_target_weekend()
        
        if self.logger:
            self.logger.debug(f"🎯 Target date for collection: {target_date.strftime('%Y-%m-%d')}")
        
        # Collect from sources (with concurrency control)
        if self.max_concurrent_sources > 1:
            all_events = self._collect_concurrent(target_date)
        else:
            all_events = self._collect_sequential(target_date)
        
        # Update final statistics
        self.collection_stats['collection_end_time'] = datetime.now().isoformat()
        self.collection_stats['total_events_collected'] = len(all_events)
        
        # Log collection summary
        self._log_collection_summary()
        
        return all_events
    
    def _collect_sequential(self, target_date: datetime) -> List[Dict[str, Any]]:
        """
        Collect events sequentially from all sources.
        
        Args:
            target_date: Target date for collection
            
        Returns:
            List of all collected events
        """
        all_events = []
        
        for source in self.active_sources:
            try:
                if self.logger:
                    self.logger.debug(f"🔄 Collecting from {source.get_display_name()}...")
                
                # Collect events from this source
                source_events = self._collect_from_source(source, target_date)
                
                # Add source metadata to events
                for event in source_events:
                    event['source_priority'] = self.source_priorities.get(source.source_name, 50)
                
                all_events.extend(source_events)
                
                # Update statistics
                self.collection_stats['successful_sources'] += 1
                self.collection_stats['source_results'][source.source_name] = {
                    'success': True,
                    'events_count': len(source_events),
                    'source_display_name': source.get_display_name()
                }
                
                if self.logger:
                    self.logger.log_source_success(source.get_display_name(), len(source_events))
            
            except Exception as e:
                error_msg = f"Collection failed: {str(e)}"
                
                self.collection_stats['failed_sources'] += 1
                self.collection_stats['source_results'][source.source_name] = {
                    'success': False,
                    'error': error_msg,
                    'source_display_name': source.get_display_name()
                }
                
                if self.logger:
                    self.logger.log_source_error(source.get_display_name(), error_msg)
        
        return all_events
    
    def _collect_concurrent(self, target_date: datetime) -> List[Dict[str, Any]]:
        """
        Collect events concurrently from multiple sources.
        
        Args:
            target_date: Target date for collection
            
        Returns:
            List of all collected events
        """
        all_events = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_sources) as executor:
            # Submit collection tasks
            future_to_source = {}
            for source in self.active_sources:
                future = executor.submit(self._collect_from_source, source, target_date)
                future_to_source[future] = source
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_source, timeout=self.collection_timeout):
                source = future_to_source[future]
                
                try:
                    source_events = future.result()
                    
                    # Add source metadata to events
                    for event in source_events:
                        event['source_priority'] = self.source_priorities.get(source.source_name, 50)
                    
                    all_events.extend(source_events)
                    
                    # Update statistics
                    self.collection_stats['successful_sources'] += 1
                    self.collection_stats['source_results'][source.source_name] = {
                        'success': True,
                        'events_count': len(source_events),
                        'source_display_name': source.get_display_name()
                    }
                    
                    if self.logger:
                        self.logger.log_source_success(source.get_display_name(), len(source_events))
                
                except concurrent.futures.TimeoutError:
                    error_msg = f"Collection timed out after {self.collection_timeout} seconds"
                    self._handle_source_error(source, error_msg)
                
                except Exception as e:
                    error_msg = f"Collection failed: {str(e)}"
                    self._handle_source_error(source, error_msg)
        
        return all_events
    
    def _collect_from_source(self, source: BaseSource, target_date: datetime) -> List[Dict[str, Any]]:
        """
        Collect events from a single source (for concurrent execution).
        
        Args:
            source: Source instance
            target_date: Target date for collection
            
        Returns:
            List of events from this source
        """
        total_attempts = 1
        if self.retry_failed_sources:
            # total tentativas = 1 (primeira) + max_retries (retries adicionais)
            total_attempts = 1 + max(0, int(self.max_retries))

        last_error: Exception | None = None

        for attempt in range(1, total_attempts + 1):
            try:
                return source.collect_events(target_date)
            except Exception as e:
                # Erros transitórios para retry
                is_transient = isinstance(e, (TimeoutError, OSError, IOError))

                # Se não habilitado, não-transitório, ou última tentativa: propagar
                if (not self.retry_failed_sources) or (not is_transient) or (attempt == total_attempts):
                    last_error = e
                    break

                # Log da tentativa e espera (backoff linear)
                if self.logger:
                    self.logger.debug(
                        f"⏳ Retry {attempt}/{total_attempts - 1} for {source.get_display_name()} after transient error: {e}"
                    )
                wait_seconds = float(self.retry_backoff_seconds) * attempt
                if wait_seconds > 0:
                    time.sleep(wait_seconds)

        # Se chegou aqui, falhou após tentativas
        if last_error is not None:
            raise last_error
        # fallback defensivo (não deve ocorrer)
        return []
    
    def _handle_source_error(self, source: BaseSource, error_msg: str) -> None:
        """Handle error from a source."""
        self.collection_stats['failed_sources'] += 1
        self.collection_stats['source_results'][source.source_name] = {
            'success': False,
            'error': error_msg,
            'source_display_name': source.get_display_name()
        }
        
        if self.logger:
            self.logger.log_source_error(source.get_display_name(), error_msg)
    
    def _get_target_weekend(self) -> datetime:
        """
        Determine the target weekend for event collection.
        
        Returns:
            Target weekend date
        """
        today = datetime.now()
        
        # If it's already weekend (Friday-Sunday), use current weekend
        if today.weekday() >= 4:  # Friday=4, Saturday=5, Sunday=6
            # Find the Friday of current week
            days_since_friday = today.weekday() - 4
            target_friday = today - timedelta(days=days_since_friday)
        else:
            # Use next weekend
            days_until_friday = (4 - today.weekday()) % 7
            if days_until_friday == 0:
                days_until_friday = 7
            target_friday = today + timedelta(days=days_until_friday)
        
        return target_friday
    
    def _log_collection_summary(self) -> None:
        """Log collection summary statistics."""
        if not self.logger:
            return
        
        stats = self.collection_stats
        
        self.logger.log_step(
            f"📊 Collection Summary: "
            f"{stats['successful_sources']}/{stats['total_sources_attempted']} sources successful, "
            f"{stats['total_events_collected']} events collected"
        )
        
        # Log individual source results
        for source_name, result in stats['source_results'].items():
            if result['success']:
                self.logger.debug(
                    f"✅ {result['source_display_name']}: {result['events_count']} events"
                )
            else:
                self.logger.debug(
                    f"❌ {result['source_display_name']}: {result['error']}"
                )
        
        # Calculate collection time
        if stats['collection_start_time'] and stats['collection_end_time']:
            start_time = datetime.fromisoformat(stats['collection_start_time'])
            end_time = datetime.fromisoformat(stats['collection_end_time'])
            duration = (end_time - start_time).total_seconds()
            
            self.logger.debug(f"⏱️ Collection completed in {duration:.1f} seconds")
    
    def get_source_statistics(self) -> Dict[str, Any]:
        """
        Get detailed statistics for all sources.
        
        Returns:
            Dictionary with source statistics
        """
        source_stats = {}
        
        for source in self.active_sources:
            source_stats[source.source_name] = source.get_statistics()
        
        return {
            'collection_stats': self.collection_stats,
            'source_stats': source_stats,
            'active_sources_count': len(self.active_sources),
            'available_sources_count': len(self.available_sources),
            'excluded_sources': list(self.excluded_sources)
        }
    
    def add_source(self, source_class: Type[BaseSource], priority: int = 50) -> bool:
        """
        Add a new source to the collector.
        
        Args:
            source_class: Source class to add
            priority: Priority for this source
            
        Returns:
            True if source was added successfully
        """
        try:
            source_name = source_class.__name__.replace('Source', '').lower()
            
            if source_name in self.excluded_sources:
                return False
            
            # Initialize source instance
            source_instance = source_class(
                config_manager=self.config,
                logger=self.logger,
                ui_manager=self.ui
            )
            
            self.active_sources.append(source_instance)
            self.source_priorities[source_name] = priority
            
            # Re-sort sources by priority
            self.active_sources.sort(
                key=lambda s: self.source_priorities.get(s.source_name, 50),
                reverse=True
            )
            
            if self.logger:
                self.logger.debug(f"➕ Added source: {source_instance.get_display_name()}")
            
            return True
        
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Failed to add source: {e}")
            return False
    
    def remove_source(self, source_name: str) -> bool:
        """
        Remove a source from the collector.
        
        Args:
            source_name: Name of source to remove
            
        Returns:
            True if source was removed successfully
        """
        for i, source in enumerate(self.active_sources):
            if source.source_name == source_name:
                removed_source = self.active_sources.pop(i)
                
                if self.logger:
                    self.logger.debug(f"➖ Removed source: {removed_source.get_display_name()}")
                
                return True
        
        return False
    
    def cleanup(self) -> None:
        """Clean up all source resources."""
        for source in self.active_sources:
            try:
                source.cleanup()
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"⚠️ Error cleaning up source {source.source_name}: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
    
    def __str__(self) -> str:
        """String representation."""
        return f"DataCollector({len(self.active_sources)} active sources)"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        source_names = [s.source_name for s in self.active_sources]
        return f"<DataCollector(sources={source_names})>"
