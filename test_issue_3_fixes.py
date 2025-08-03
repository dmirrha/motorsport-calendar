#!/usr/bin/env python3
"""
Test script to validate fixes for Issue #3: Event detection improvements in TomadaTempoSource

This script tests the following improvements:
1. Enhanced date extraction with weekday patterns (e.g., "SÁBADO – 02/08/2025")
2. Programming context extraction from page title/URL
3. Association of events without explicit dates to programming context
4. Improved time format support (14h30, às 14h30, etc.)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sources.tomada_tempo import TomadaTempoSource
from src.config_manager import ConfigManager
from src.logger import Logger
from bs4 import BeautifulSoup

def test_date_extraction():
    """Test enhanced date extraction with weekday patterns."""
    print("🧪 Testing enhanced date extraction...")
    
    source = TomadaTempoSource()
    
    test_cases = [
        ("SÁBADO – 02/08/2025", "02/08/2025"),
        ("DOMINGO – 03/08/2025", "03/08/2025"),
        ("sexta – 01/08/2025", "01/08/2025"),
        ("02/08/2025", "02/08/2025"),
        ("sábado 02/08/2025", "02/08/2025"),
    ]
    
    for text, expected in test_cases:
        result = source._extract_date(text)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{text}' -> '{result}' (expected: '{expected}')")

def test_time_extraction():
    """Test improved time format support."""
    print("\n🧪 Testing improved time extraction...")
    
    source = TomadaTempoSource()
    
    test_cases = [
        ("14:30", "14:30"),
        ("14h30", "14:30"),
        ("14h 30", "14:30"),
        ("às 14h30", "14:30"),
        ("às 14:30", "14:30"),
        ("14 horas", "14:00"),
        ("14 horas e 30", "14:30"),
        ("16:30 – NASCAR CUP", "16:30"),
        ("19:00 – FÓRMULA 1", "19:00"),
    ]
    
    for text, expected in test_cases:
        result = source._extract_time(text)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{text}' -> '{result}' (expected: '{expected}')")

def test_programming_context_extraction():
    """Test programming context extraction from page title."""
    print("\n🧪 Testing programming context extraction...")
    
    source = TomadaTempoSource()
    
    # Mock HTML with programming title
    html_content = """
    <html>
        <head>
            <title>PROGRAMAÇÃO DA TV E INTERNET - CORRIDAS TRANSMITIDAS NO FINAL DE SEMANA DE 01 A 03-08-2025</title>
        </head>
        <body>
            <h1>Programação do Final de Semana</h1>
        </body>
    </html>
    """
    
    soup = BeautifulSoup(html_content, 'html.parser')
    context = source._extract_programming_context(soup)
    
    print(f"  📅 Programming title: {context.get('programming_title', 'Not found')}")
    print(f"  📅 Start date: {context.get('start_date', 'Not found')}")
    print(f"  📅 End date: {context.get('end_date', 'Not found')}")
    print(f"  📅 Weekend dates: {context.get('weekend_dates', [])}")
    
    # Verify results
    expected_start = "01/08/2025"
    expected_end = "03/08/2025"
    
    status_start = "✅" if context.get('start_date') == expected_start else "❌"
    status_end = "✅" if context.get('end_date') == expected_end else "❌"
    
    print(f"  {status_start} Start date extraction: {context.get('start_date')} (expected: {expected_start})")
    print(f"  {status_end} End date extraction: {context.get('end_date')} (expected: {expected_end})")

def test_event_association_to_context():
    """Test association of events without explicit dates to programming context."""
    print("\n🧪 Testing event association to programming context...")
    
    source = TomadaTempoSource()
    
    # Mock programming context
    programming_context = {
        'start_date': '01/08/2025',
        'end_date': '03/08/2025',
        'weekend_dates': ['01/08/2025', '02/08/2025', '03/08/2025'],
        'programming_title': 'PROGRAMAÇÃO DO FINAL DE SEMANA'
    }
    
    test_cases = [
        {
            'line': 'F1 - FÓRMULA 1',
            'should_have_date': True,
            'description': 'F1 event without explicit date'
        },
        {
            'line': '16:30 – NASCAR CUP',
            'should_have_date': True,
            'description': 'NASCAR event with time but no date'
        },
        {
            'line': 'MotoGP - Grande Prêmio',
            'should_have_date': True,
            'description': 'MotoGP event without explicit date'
        },
        {
            'line': 'Random text without motorsport content',
            'should_have_date': False,
            'description': 'Non-motorsport content'
        }
    ]
    
    for test_case in test_cases:
        event = source._extract_event_from_text_line(test_case['line'], programming_context)
        
        if test_case['should_have_date']:
            has_date = event is not None and event.get('date') is not None
            status = "✅" if has_date else "❌"
            date_info = f"date: {event.get('date') if event else 'None'}" if event else "event: None"
            print(f"  {status} {test_case['description']}: {date_info}")
        else:
            is_none = event is None
            status = "✅" if is_none else "❌"
            print(f"  {status} {test_case['description']}: {'correctly filtered out' if is_none else 'incorrectly included'}")

def run_all_tests():
    """Run all test cases for Issue #3 fixes."""
    print("🔧 Testing Issue #3 fixes: Enhanced event detection in TomadaTempoSource")
    print("=" * 80)
    
    try:
        test_date_extraction()
        test_time_extraction()
        test_programming_context_extraction()
        test_event_association_to_context()
        
        print("\n" + "=" * 80)
        print("✅ All tests completed! Review the results above to verify the fixes.")
        print("📝 Note: Events without explicit dates should now be associated to programming context.")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
