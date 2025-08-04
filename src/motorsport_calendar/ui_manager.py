"""
Visual UI Manager for Motorsport Calendar

Provides colorful, step-by-step visual interface with progress bars,
icons, and pleasant visual elements for terminal output.
"""

import os
import time
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.align import Align
import colorama
from colorama import Fore, Back, Style


class UIManager:
    """Visual interface manager with rich formatting and progress tracking."""
    
    def __init__(self, config_manager=None):
        """
        Initialize UI manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager
        self.console = Console()
        self.progress_tasks: Dict[str, Any] = {}
        self.current_step = 0
        self.total_steps = 0
        
        # Initialize colorama for cross-platform color support
        colorama.init()
        
        # Check if visual interface is enabled
        self.enabled = True
        self.use_colors = True
        self.use_icons = True
        
        if self.config:
            self.enabled = self.config.get('general.visual_interface.enabled', True)
            self.use_colors = self.config.get('general.visual_interface.colors', True)
            self.use_icons = self.config.get('general.visual_interface.icons', True)
        
        # Icons and symbols
        self.icons = {
            'start': '🏁',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'loading': '🔄',
            'data': '📊',
            'network': '🌐',
            'file': '📁',
            'calendar': '📅',
            'racing': '🏎️',
            'motorcycle': '🏍️',
            'trophy': '🏆',
            'gear': '⚙️',
            'rocket': '🚀',
            'target': '🎯',
            'magnify': '🔍',
            'save': '💾',
            'link': '🔗',
            'clock': '⏰',
            'location': '📍',
            'broadcast': '📺'
        } if self.use_icons else {k: '' for k in [
            'start', 'success', 'error', 'warning', 'info', 'loading',
            'data', 'network', 'file', 'calendar', 'racing', 'motorcycle',
            'trophy', 'gear', 'rocket', 'target', 'magnify', 'save',
            'link', 'clock', 'location', 'broadcast'
        ]}
    
    def show_banner(self) -> None:
        """Display application banner."""
        if not self.enabled:
            return
        
        banner_text = """
🏁 MOTORSPORT CALENDAR GENERATOR 🏁
   Automated Weekend Events Collection
        Dynamic Category Detection
"""
        
        banner = Panel(
            Align.center(Text(banner_text, style="bold blue")),
            box=box.DOUBLE,
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(banner)
        self.console.print()
    
    def show_config_summary(self, config_summary: Dict[str, Any]) -> None:
        """
        Display configuration summary.
        
        Args:
            config_summary: Dictionary with configuration details
        """
        if not self.enabled:
            return
        
        table = Table(title="📋 Configuration Summary", box=box.ROUNDED)
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        for key, value in config_summary.items():
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value[:3])
                if len(value) > 3:
                    value_str += f" ... (+{len(value)-3} more)"
            else:
                value_str = str(value)
            
            table.add_row(key, value_str)
        
        self.console.print(table)
        self.console.print()
    
    def start_step_progress(self, total_steps: int) -> None:
        """
        Initialize step-by-step progress tracking.
        
        Args:
            total_steps: Total number of steps
        """
        self.total_steps = total_steps
        self.current_step = 0
    
    def show_step(self, step_name: str, description: str = "") -> None:
        """
        Display current step with progress.
        
        Args:
            step_name: Name of the current step
            description: Optional step description
        """
        if not self.enabled:
            return
        
        self.current_step += 1
        
        # Progress indicator
        progress_bar = "█" * self.current_step + "░" * (self.total_steps - self.current_step)
        progress_text = f"[{self.current_step}/{self.total_steps}]"
        
        step_text = Text()
        step_text.append(f"{self.icons['gear']} ", style="blue")
        step_text.append(f"STEP {progress_text}: ", style="bold blue")
        step_text.append(step_name, style="bold white")
        
        if description:
            step_text.append(f"\n   {description}", style="dim white")
        
        panel = Panel(
            step_text,
            border_style="blue",
            padding=(0, 1)
        )
        
        self.console.print(panel)
    
    def show_source_collection_start(self, sources: List[str]) -> None:
        """
        Display start of data source collection.
        
        Args:
            sources: List of data sources to collect from
        """
        if not self.enabled:
            return
        
        table = Table(title=f"{self.icons['network']} Data Sources Collection", box=box.SIMPLE)
        table.add_column("Priority", style="cyan", width=8)
        table.add_column("Source", style="green")
        table.add_column("Status", style="yellow")
        
        for i, source in enumerate(sources, 1):
            table.add_row(str(i), source, "Pending...")
        
        self.console.print(table)
    
    def create_progress_bar(self, task_name: str, total: Optional[int] = None) -> Any:
        """
        Create a progress bar for a specific task.
        
        Args:
            task_name: Name of the task
            total: Total number of items (None for indeterminate)
            
        Returns:
            Progress task ID
        """
        if not self.enabled:
            return None
        
        if task_name not in self.progress_tasks:
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=self.console
            )
            
            task_id = progress.add_task(task_name, total=total)
            self.progress_tasks[task_name] = {
                'progress': progress,
                'task_id': task_id
            }
        
        return self.progress_tasks[task_name]['task_id']
    
    def update_progress(self, task_name: str, advance: int = 1, description: str = None) -> None:
        """
        Update progress for a specific task.
        
        Args:
            task_name: Name of the task
            advance: Number of items to advance
            description: Optional new description
        """
        if not self.enabled or task_name not in self.progress_tasks:
            return
        
        task_info = self.progress_tasks[task_name]
        task_info['progress'].update(task_info['task_id'], advance=advance)
        
        if description:
            task_info['progress'].update(task_info['task_id'], description=description)
    
    def show_source_result(self, source: str, success: bool, event_count: int = 0, 
                          error_message: str = "") -> None:
        """
        Display result of data source collection.
        
        Args:
            source: Source name
            success: Whether collection was successful
            event_count: Number of events collected
            error_message: Error message if failed
        """
        if not self.enabled:
            return
        
        if success:
            icon = self.icons['success']
            status = f"✓ {event_count} events"
            style = "green"
        else:
            icon = self.icons['error']
            status = f"✗ {error_message}"
            style = "red"
        
        result_text = Text()
        result_text.append(f"{icon} ", style=style)
        result_text.append(f"{source}: ", style="bold")
        result_text.append(status, style=style)
        
        self.console.print(f"  {result_text}")
    
    def show_category_detection_results(self, categories: Dict[str, Any]) -> None:
        """
        Display category detection results.
        
        Args:
            categories: Dictionary with detected categories and their info
        """
        if not self.enabled or not categories:
            return
        
        table = Table(title=f"{self.icons['target']} Dynamic Category Detection", box=box.ROUNDED)
        table.add_column("Category", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Events", style="yellow", justify="right")
        table.add_column("Confidence", style="blue", justify="right")
        table.add_column("Sources", style="magenta")
        
        for category, info in categories.items():
            category_type = info.get('type', 'unknown')
            event_count = info.get('event_count', 0)
            confidence = info.get('confidence', 0.0)
            sources = info.get('sources', [])
            
            # Add appropriate icon based on type
            type_icon = {
                'cars': self.icons['racing'],
                'motorcycles': self.icons['motorcycle'],
                'mixed': f"{self.icons['racing']}{self.icons['motorcycle']}",
                'other': self.icons['gear']
            }.get(category_type, '')
            
            confidence_color = "green" if confidence > 0.8 else "yellow" if confidence > 0.6 else "red"
            
            table.add_row(
                f"{type_icon} {category}",
                category_type.title(),
                str(event_count),
                f"[{confidence_color}]{confidence:.1%}[/{confidence_color}]",
                ", ".join(sources[:2]) + ("..." if len(sources) > 2 else "")
            )
        
        self.console.print(table)
        self.console.print()
    
    def show_weekend_detection(self, weekend_info: Dict[str, Any]) -> None:
        """
        Display weekend detection results.
        
        Args:
            weekend_info: Dictionary with weekend detection info
        """
        if not self.enabled:
            return
        
        start_date = weekend_info.get('start_date', 'Unknown')
        end_date = weekend_info.get('end_date', 'Unknown')
        total_events = weekend_info.get('total_events', 0)
        
        weekend_text = Text()
        weekend_text.append(f"{self.icons['calendar']} Weekend Detected: ", style="bold blue")
        weekend_text.append(f"{start_date} to {end_date}", style="green")
        weekend_text.append(f" ({total_events} events)", style="yellow")
        
        panel = Panel(
            weekend_text,
            border_style="green",
            padding=(0, 1)
        )
        
        self.console.print(panel)
    
    def show_event_summary(self, events: List[Dict[str, Any]]) -> None:
        """
        Display summary of collected events.
        
        Args:
            events: List of event dictionaries
        """
        if not self.enabled or not events:
            return
        
        table = Table(title=f"{self.icons['trophy']} Collected Events Summary", box=box.ROUNDED)
        table.add_column("Time", style="cyan", width=8)
        table.add_column("Event", style="green")
        table.add_column("Category", style="yellow")
        table.add_column("Location", style="blue")
        table.add_column("Stream", style="magenta")
        
        for event in events[:10]:  # Show first 10 events
            time_str = event.get('time', 'TBD')
            name = event.get('name', 'Unknown Event')[:40]
            category = event.get('category', 'Unknown')
            location = event.get('location', 'TBD')[:20]
            has_stream = self.icons['broadcast'] if event.get('streaming_links') else '-'
            
            table.add_row(time_str, name, category, location, has_stream)
        
        if len(events) > 10:
            table.add_row("...", f"... and {len(events) - 10} more events", "...", "...", "...")
        
        self.console.print(table)
        self.console.print()
    
    def show_deduplication_results(self, duplicates_removed: int, total_before: int) -> None:
        """
        Display deduplication results.
        
        Args:
            duplicates_removed: Number of duplicates removed
            total_before: Total events before deduplication
        """
        if not self.enabled:
            return
        
        if duplicates_removed > 0:
            dedup_text = Text()
            dedup_text.append(f"{self.icons['magnify']} Deduplication: ", style="bold blue")
            dedup_text.append(f"Removed {duplicates_removed} duplicates ", style="red")
            dedup_text.append(f"({total_before} → {total_before - duplicates_removed})", style="green")
            
            self.console.print(dedup_text)
        else:
            self.console.print(f"{self.icons['success']} No duplicates found - all events unique!")
    
    def show_ical_generation(self, filepath: str, event_count: int) -> None:
        """
        Display iCal generation results.
        
        Args:
            filepath: Path to generated iCal file
            event_count: Number of events in the file
        """
        if not self.enabled:
            return
        
        ical_text = Text()
        ical_text.append(f"{self.icons['save']} iCal Generated: ", style="bold green")
        ical_text.append(f"{filepath}", style="blue")
        ical_text.append(f" ({event_count} events)", style="yellow")
        
        panel = Panel(
            ical_text,
            title="📋 Calendar File Ready",
            border_style="green",
            padding=(0, 1)
        )
        
        self.console.print(panel)
    
    def show_success_message(self, message: str) -> None:
        """Display success message."""
        if not self.enabled:
            return
        
        success_text = Text()
        success_text.append(f"{self.icons['success']} ", style="green")
        success_text.append(message, style="bold green")
        
        self.console.print(success_text)
    
    def show_error_message(self, message: str) -> None:
        """Display error message."""
        if not self.enabled:
            return
        
        error_text = Text()
        error_text.append(f"{self.icons['error']} ", style="red")
        error_text.append(message, style="bold red")
        
        self.console.print(error_text)
    
    def show_step_result(self, step_name: str, success: bool, message: str = "") -> None:
        """Display step completion result."""
        if not self.enabled:
            return
        
        if success:
            icon = self.icons['success']
            style = "green"
            status = "COMPLETED"
        else:
            icon = self.icons['error']
            style = "red"
            status = "FAILED"
        
        result_text = Text()
        result_text.append(f"{icon} ", style=style)
        result_text.append(f"{step_name} {status}", style=f"bold {style}")
        
        if message:
            result_text.append(f": {message}", style=style)
        
        self.console.print(result_text)
    
    def show_warning_message(self, message: str) -> None:
        """Display warning message."""
        if not self.enabled:
            return
        
        warning_text = Text()
        warning_text.append(f"{self.icons['warning']} ", style="yellow")
        warning_text.append(message, style="bold yellow")
        
        self.console.print(warning_text)
    
    def show_final_summary(self, **kwargs) -> None:
        """
        Display final execution summary.
        
        Args:
            **kwargs: Execution summary data as keyword arguments
        """
        if not self.enabled:
            return
        
        # Create summary table
        table = Table(title=f"{self.icons['trophy']} Execution Summary", box=box.ROUNDED)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        # Convert kwargs to readable format
        readable_metrics = {
            'sources_successful': 'Sources Successful',
            'sources_total': 'Total Sources',
            'events_collected': 'Events Collected',
            'events_processed': 'Events Processed',
            'output_file': 'Output File',
            'execution_time': 'Execution Time (s)'
        }
        
        for key, value in kwargs.items():
            display_key = readable_metrics.get(key, key.replace('_', ' ').title())
            
            if isinstance(value, (int, float)):
                if key == 'execution_time':
                    value_str = f"{value:.1f}s"
                else:
                    value_str = f"{value:,}" if isinstance(value, int) else f"{value:.2f}"
            else:
                value_str = str(value)
            
            table.add_row(display_key, value_str)
        
        self.console.print()
        self.console.print(table)
        self.console.print()
    
    def show_events_by_category(self, events_by_category: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        Display events grouped by category.
        
        Args:
            events_by_category: Dictionary of events grouped by category
        """
        if not self.enabled or not events_by_category:
            return
        
        # Display each category
        for category, category_events in events_by_category.items():
            category_text = Text()
            category_text.append(f"{self.icons['racing']} ", style="blue")
            category_text.append(f"{category}", style="bold blue")
            category_text.append(f" ({len(category_events)} events)", style="dim blue")
            
            self.console.print(category_text)
            
            for event in category_events:
                event_text = Text()
                event_text.append("  • ", style="dim")
                event_text.append(event.get('name', 'Unknown Event'), style="white")
                
                if event.get('date'):
                    event_text.append(f" - {event['date']}", style="dim cyan")
                
                if event.get('location'):
                    event_text.append(f" @ {event['location']}", style="dim yellow")
                
                self.console.print(event_text)
            
            self.console.print()
    
    def show_import_instructions(self, output_file: str) -> None:
        """
        Display instructions for importing the iCal file into Google Calendar.
        
        Args:
            output_file: Path to the generated iCal file
        """
        if not self.enabled:
            return
        
        instructions_text = Text()
        instructions_text.append(f"{self.icons['info']} ", style="blue")
        instructions_text.append("Google Calendar Import Instructions:", style="bold blue")
        
        self.console.print()
        self.console.print(instructions_text)
        self.console.print()
        
        steps = [
            "1. Open Google Calendar (calendar.google.com)",
            "2. Click the '+' button next to 'Other calendars'",
            "3. Select 'Create new calendar' or 'Import'",
            f"4. Upload the file: {os.path.basename(output_file)}",
            "5. Choose your preferred calendar settings",
            "6. Click 'Import' to add the motorsport events"
        ]
        
        for step in steps:
            step_text = Text()
            step_text.append("  • ", style="dim")
            step_text.append(step, style="white")
            self.console.print(step_text)
        
        self.console.print()
        
        tip_text = Text()
        tip_text.append(f"{self.icons['target']} ", style="yellow")
        tip_text.append("Tip: ", style="bold yellow")
        tip_text.append("The events will appear in your calendar with reminders and direct broadcast links!", style="yellow")
        
        self.console.print(tip_text)
        self.console.print()
    
    def show_completion_summary(self, summary: Dict[str, Any]) -> None:
        """
        Display final completion summary.
        
        Args:
            summary: Dictionary with execution summary
        """
        if not self.enabled:
            return
        
        # Create completion panel
        completion_text = Text()
        completion_text.append(f"{self.icons['trophy']} EXECUTION COMPLETED SUCCESSFULLY!\n\n", 
                              style="bold green")
        
        for key, value in summary.items():
            completion_text.append(f"• {key}: ", style="cyan")
            completion_text.append(f"{value}\n", style="white")
        
        panel = Panel(
            completion_text,
            title=f"{self.icons['start']} Motorsport Calendar - Execution Summary",
            border_style="green",
            box=box.DOUBLE,
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)
        self.console.print()
    
    def print_separator(self) -> None:
        """Print a visual separator line."""
        if self.enabled:
            self.console.print("─" * 80, style="dim blue")
    
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        if self.enabled:
            self.console.clear()
    
    def pause(self, seconds: float = 1.0) -> None:
        """
        Pause execution for visual effect.
        
        Args:
            seconds: Number of seconds to pause
        """
        if self.enabled:
            time.sleep(seconds)
    
    def close_progress_bars(self) -> None:
        """Close all active progress bars."""
        for task_info in self.progress_tasks.values():
            try:
                task_info['progress'].stop()
            except:
                pass
        
        self.progress_tasks.clear()
