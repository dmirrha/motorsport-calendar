#!/usr/bin/env python3
"""
Motorsport Calendar Generator

Main executable script for collecting motorsport events from multiple sources,
processing them, and generating iCal files for Google Calendar import.

Usage:
    python motorsport_calendar.py [options]
    
Examples:
    python motorsport_calendar.py                    # Generate calendar for next weekend
    python motorsport_calendar.py --date 2024-08-10 # Generate for specific date
    python motorsport_calendar.py --config config/config.json # Use custom config
    python motorsport_calendar.py --output ./calendars/ # Custom output directory
"""

import os
import sys
import argparse
import traceback
from datetime import datetime, timedelta
from pathlib import Path

# Ensure the src directory is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_root, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from motorsport_calendar.config_manager import ConfigManager
from motorsport_calendar.logger import Logger
from motorsport_calendar.ui_manager import UIManager
from motorsport_calendar.category_detector import CategoryDetector
from motorsport_calendar.data_collector import DataCollector
from motorsport_calendar.event_processor import EventProcessor
from motorsport_calendar.ical_generator import ICalGenerator


class MotorsportCalendarGenerator:
    """Main application class for motorsport calendar generation."""
    
    def __init__(self, config_path: str = "config/config.json", output_dir: str = None):
        """
        Initialize the calendar generator.
        
        Args:
            config_path: Path to configuration file
            output_dir: Output directory override
        """
        self.config_path = config_path
        self.output_dir = output_dir
        
        # Core components
        self.config = None
        self.logger = None
        self.ui = None
        self.category_detector = None
        self.data_collector = None
        self.event_processor = None
        self.ical_generator = None
        
        # Execution statistics
        self.execution_stats = {
            'start_time': None,
            'end_time': None,
            'total_sources': 0,
            'successful_sources': 0,
            'total_events_collected': 0,
            'events_after_processing': 0,
            'calendars_generated': 0,
            'success': False,
            'error_message': None
        }
    
    def initialize(self) -> bool:
        """
        Initialize all components.
        
        Returns:
            True if initialization successful
        """
        try:
            # Initialize configuration manager
            self.config = ConfigManager(self.config_path)
            
            # Initialize logger
            self.logger = Logger(self.config)
            self.logger.log_step("🚀 Initializing Motorsport Calendar Generator")
            
            # Initialize UI manager
            self.ui = UIManager(self.config)
            self.ui.show_banner()
            
            # Initialize category detector
            self.category_detector = CategoryDetector(self.config, self.logger)
            
            # Initialize data collector
            self.data_collector = DataCollector(self.config, self.logger, self.ui, self.category_detector)
            
            # Initialize event processor
            self.event_processor = EventProcessor(self.config, self.logger, self.ui, self.category_detector)
            
            # Initialize iCal generator
            self.ical_generator = ICalGenerator(self.config, self.logger, self.ui)
            
            # Override output directory if specified
            if self.output_dir:
                self.ical_generator.output_directory = self.output_dir
            
            self.logger.log_success("✅ All components initialized successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize components: {str(e)}"
            if self.logger:
                self.logger.log_error(error_msg)
            else:
                print(f"❌ {error_msg}")
            
            self.execution_stats['error_message'] = error_msg
            return False
    
    def run(self, target_date: datetime = None) -> bool:
        """
        Run the complete calendar generation process.
        
        Args:
            target_date: Target date for event collection
            
        Returns:
            True if execution successful
        """
        self.execution_stats['start_time'] = datetime.now().isoformat()
        
        try:
            self.logger.log_step("🏁 Starting motorsport calendar generation")
            self.ui.show_step("Calendar Generation", "Starting complete process...")
            
            # Step 1: Collect events from all sources
            self.logger.log_step("📡 Step 1: Data Collection")
            raw_events = self.data_collector.collect_events(target_date)
            
            # Update statistics
            collector_stats = self.data_collector.get_source_statistics()
            self.execution_stats['total_sources'] = collector_stats['collection_stats']['total_sources_attempted']
            self.execution_stats['successful_sources'] = collector_stats['collection_stats']['successful_sources']
            self.execution_stats['total_events_collected'] = len(raw_events)
            
            if not raw_events:
                self.logger.log_warning("⚠️ No events collected from any source")
                self.ui.show_warning_message("No events found for the target period")
                return False
            
            self.logger.log_success(f"📡 Collected {len(raw_events)} events from {self.execution_stats['successful_sources']} sources")
            
            # Step 2: Process events (normalize, deduplicate, filter)
            self.logger.log_step("🔄 Step 2: Event Processing")
            processed_events = self.event_processor.process_events(raw_events, target_date)
            
            self.execution_stats['events_after_processing'] = len(processed_events)
            
            if not processed_events:
                self.logger.log_warning("⚠️ No events remaining after processing")
                self.ui.show_warning_message("No valid events found after processing")
                return False
            
            self.logger.log_success(f"🔄 Processed {len(processed_events)} valid events")
            
            # Step 3: Generate iCal file
            self.logger.log_step("📅 Step 3: iCal Generation")
            output_path = self.ical_generator.generate_calendar(processed_events)
            
            if not output_path:
                self.logger.log_error("❌ Failed to generate iCal file")
                return False
            
            self.execution_stats['calendars_generated'] = 1
            
            # Step 4: Validate generated calendar
            self.logger.log_step("✅ Step 4: Calendar Validation")
            validation_results = self.ical_generator.validate_calendar(output_path)
            
            if not validation_results['valid']:
                self.logger.log_warning(f"⚠️ Calendar validation issues: {validation_results['errors']}")
            else:
                self.logger.log_success("✅ Calendar validation passed")
            
            # Step 5: Show summary and results
            self._show_final_summary(output_path, processed_events)
            
            self.execution_stats['success'] = True
            return True
            
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            self.logger.log_error(error_msg)
            self.logger.debug(f"Full traceback: {traceback.format_exc()}")
            
            self.execution_stats['error_message'] = error_msg
            self.ui.show_error_message(error_msg)
            return False
        
        finally:
            self.execution_stats['end_time'] = datetime.now().isoformat()
            self._cleanup()
    
    def _show_final_summary(self, output_path: str, events: list) -> None:
        """Show final execution summary."""
        self.logger.log_step("📊 Execution Summary")
        
        # Calculate execution time
        start_time = datetime.fromisoformat(self.execution_stats['start_time'])
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Show summary in UI
        self.ui.show_final_summary(
            sources_successful=self.execution_stats['successful_sources'],
            sources_total=self.execution_stats['total_sources'],
            events_collected=self.execution_stats['total_events_collected'],
            events_processed=self.execution_stats['events_after_processing'],
            output_file=os.path.basename(output_path),
            execution_time=duration
        )
        
        # Show events by category
        self._show_events_by_category(events)
        
        # Log final success message
        self.logger.log_success(
            f"🎉 Calendar generation completed successfully! "
            f"Generated {os.path.basename(output_path)} with {len(events)} events in {duration:.1f}s"
        )
        
        # Show import instructions
        self.ui.show_import_instructions(output_path)
    
    def _show_events_by_category(self, events: list) -> None:
        """Show events grouped by category."""
        from collections import defaultdict
        
        events_by_category = defaultdict(list)
        for event in events:
            category = event.get('detected_category', 'Unknown')
            events_by_category[category].append(event)
        
        if self.ui:
            self.ui.show_events_by_category(dict(events_by_category))
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self.data_collector:
                self.data_collector.cleanup()
            
            if self.ical_generator:
                self.ical_generator.cleanup()
                
        except Exception as e:
            if self.logger:
                self.logger.debug(f"⚠️ Cleanup error: {e}")
    
    def get_execution_statistics(self) -> dict:
        """Get detailed execution statistics."""
        stats = self.execution_stats.copy()
        
        # Add component statistics if available
        if self.data_collector:
            stats['data_collection'] = self.data_collector.get_source_statistics()
        
        if self.event_processor:
            stats['event_processing'] = self.event_processor.get_processing_statistics()
        
        if self.ical_generator:
            stats['ical_generation'] = self.ical_generator.get_generation_statistics()
        
        if self.category_detector:
            stats['category_detection'] = self.category_detector.get_statistics()
        
        return stats


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate motorsport events calendar from multiple sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Generate calendar for next weekend
  %(prog)s --date 2024-08-10           # Generate for specific weekend
  %(prog)s --config custom.json        # Use custom configuration
  %(prog)s --output ./calendars/       # Custom output directory
  %(prog)s --verbose                   # Enable verbose logging
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config/config.json',
        help='Configuration file path (default: config/config.json)'
    )
    
    parser.add_argument(
        '--date', '-d',
        help='Target date for event collection (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output directory for generated files'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--validate-config',
        action='store_true',
        help='Validate configuration file and exit'
    )
    
    parser.add_argument(
        '--list-sources',
        action='store_true',
        help='List available data sources and exit'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Motorsport Calendar Generator 0.1.2'
    )
    
    return parser.parse_args()


def validate_config_file(config_path: str) -> bool:
    """Validate configuration file."""
    try:
        config = ConfigManager(config_path)
        print(f"✅ Configuration file '{config_path}' is valid")
        
        # Show configuration summary
        general_config = config.get_general_config()
        data_sources = config.get_data_sources_config()
        
        print(f"📋 Configuration Summary:")
        print(f"   • Timezone: {general_config.get('timezone', 'America/Sao_Paulo')}")
        print(f"   • Data sources: {len(data_sources.get('sources', {}))}")
        print(f"   • Output directory: {config.get_ical_config().get('output', {}).get('directory', 'output')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


def list_available_sources() -> None:
    """List available data sources."""
    try:
        # Initialize minimal components to discover sources
        config = ConfigManager()
        logger = Logger(config)
        data_collector = DataCollector(config, logger)
        
        print("📡 Available Data Sources:")
        
        for source in data_collector.active_sources:
            priority = data_collector.source_priorities.get(source.source_name, 50)
            print(f"   • {source.get_display_name()} (Priority: {priority})")
            print(f"     URL: {source.get_base_url()}")
            print(f"     Status: {'✅ Active' if source.source_name not in data_collector.excluded_sources else '❌ Excluded'}")
            print()
        
        excluded_count = len(data_collector.excluded_sources)
        if excluded_count > 0:
            print(f"⚠️ {excluded_count} sources are excluded in configuration")
        
    except Exception as e:
        print(f"❌ Failed to list sources: {e}")


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Handle special commands
    if args.validate_config:
        success = validate_config_file(args.config)
        sys.exit(0 if success else 1)
    
    if args.list_sources:
        list_available_sources()
        sys.exit(0)
    
    # Check if configuration file exists
    if not os.path.exists(args.config):
        print(f"❌ Configuration file '{args.config}' not found")
        print(f"💡 Create a configuration file based on 'config.example.json'")
        sys.exit(1)
    
    # Parse target date
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            print(f"❌ Invalid date format: {args.date}. Use YYYY-MM-DD format.")
            sys.exit(1)
    
    # Create and run calendar generator
    try:
        generator = MotorsportCalendarGenerator(
            config_path=args.config,
            output_dir=args.output
        )
        
        # Initialize components
        if not generator.initialize():
            print("❌ Failed to initialize calendar generator")
            sys.exit(1)
        
        # Set verbose logging if requested
        if args.verbose and generator.logger:
            generator.logger.set_console_level('DEBUG')
        
        # Run calendar generation
        success = generator.run(target_date)
        
        # Show final statistics if verbose
        if args.verbose:
            stats = generator.get_execution_statistics()
            print("\n📊 Detailed Statistics:")
            print(f"   • Execution time: {stats.get('execution_time', 'N/A')}")
            print(f"   • Sources attempted: {stats.get('total_sources', 0)}")
            print(f"   • Sources successful: {stats.get('successful_sources', 0)}")
            print(f"   • Events collected: {stats.get('total_events_collected', 0)}")
            print(f"   • Events processed: {stats.get('events_after_processing', 0)}")
            print(f"   • Calendars generated: {stats.get('calendars_generated', 0)}")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Execution interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
