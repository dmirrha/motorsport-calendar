"""
Utilities for Motorsport Calendar.

This package contains utility modules for the Motorsport Calendar application.
"""

# Make utilities available at the package level
from .ical_generator import generate_ical

__all__ = ['generate_ical']
