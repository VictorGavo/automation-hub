#!/usr/bin/env python3
"""
Debug script to analyze form data structure and field mapping issues
"""

from database import DatabaseManager
from datetime import date, timedelta
import json

def debug_form_data():
    """Debug the current form data in database"""
    
    db_manager = DatabaseManager()
    
    # Check recent entries
    test_date = date(2025, 7, 21)  # Use test date from integration test
    
    print("🔍 Debugging Form Data Structure")
    print("=" * 50)
    
    entry = db_manager.get_daily_entry(test_date)
    
    if entry:
        print(f"📅 Date: {entry['date']}")
        print(f"🌅 SOD Timestamp: {entry['sod_timestamp']}")
        print(f"🌙 EOD Timestamp: {entry['eod_timestamp']}")
        print()
        
        if entry['sod_data']:
            print("🌅 SOD DATA FIELDS:")
            print("-" * 30)
            for key, value in entry['sod_data'].items():
                print(f"'{key}': '{value[:100]}{'...' if len(str(value)) > 100 else ''}'")
            print()
        
        if entry['eod_data']:
            print("🌙 EOD DATA FIELDS:")
            print("-" * 30)
            for key, value in entry['eod_data'].items():
                print(f"'{key}': '{value[:100]}{'...' if len(str(value)) > 100 else ''}'")
            print()
    else:
        print(f"❌ No entry found for {test_date}")

def check_field_mappings():
    """Check for field mapping issues"""
    print("🔍 FIELD MAPPING ANALYSIS")
    print("=" * 50)
    
    # Expected fields in template
    expected_sod_fields = [
        "What am I looking forward to the most today?",
        "Today's Big 3", 
        "I know today would be successful if I did or felt this by the end:",
        "3 things I'm grateful for in my life:",
        "3 things I'm grateful about myself:",
        "I'm excited today for:",
        "One word to describe the person I want to be today would be __ because:",
        "Someone who needs me on my a-game today is:",
        "What's a potential obstacle/stressful situation for today and how would my best self deal with it?",
        "Someone I could surprise with a note, gift, or sign of appreciation is:",
        "One action I could take today to demonstrate excellence or real value is:",
        "One bold action I could take today is:",
        "An overseeing high performance coach would tell me today that:",
        "The big projects I should keep in mind, even if I don't work on them today, are:"
    ]
    
    # Check actual data
    db_manager = DatabaseManager()
    test_date = date(2025, 7, 21)  # Use test date
    entry = db_manager.get_daily_entry(test_date)
    
    if entry and entry['sod_data']:
        actual_fields = list(entry['sod_data'].keys())
        
        print("✅ FIELDS FOUND IN DATABASE:")
        for field in actual_fields:
            print(f"  • {field}")
        print()
        
        print("❓ EXPECTED BUT MISSING:")
        for field in expected_sod_fields:
            if field not in actual_fields:
                print(f"  • {field}")
        print()
        
        print("❓ FOUND BUT NOT EXPECTED:")
        for field in actual_fields:
            if field not in expected_sod_fields:
                print(f"  • {field}")
    else:
        print("❌ No SOD data to analyze")

if __name__ == "__main__":
    debug_form_data()
    print()
    check_field_mappings()
