#!/usr/bin/env python3
"""
Core Functionality Tests
Tests basic database operations and configuration
"""

import sys
import os
from datetime import datetime, date, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config  # Remove DATABASE_CONFIG import
from database import DatabaseManager
import json

def test_database_connection():
    """Test database connection and basic operations"""
    print("🔍 Testing Database Connection...")
    print("-" * 50)
    
    try:
        # Test connection
        db_manager = DatabaseManager()
        print(f"✅ Connected to database: {Config.DB_NAME}")
        
        # Test table creation
        db_manager.create_tables()
        print("✅ Tables created/verified")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_sod_eod_operations():
    """Test SOD and EOD data operations"""
    print("\n🔍 Testing SOD/EOD Operations...")
    print("-" * 50)
    
    try:
        db_manager = DatabaseManager()
        test_date = date.today() - timedelta(days=1)  # Use yesterday to avoid conflicts
        
        # Test SOD data
        sod_data = {
            "highlight": "Test highlight",
            "big3": "1. Test task 1\n2. Test task 2\n3. Test task 3",
            "gratitude": "Test gratitude"
        }
        
        sod_success = db_manager.upsert_sod_data(test_date, sod_data)
        if sod_success:
            print("✅ SOD data insertion successful")
        else:
            print("❌ SOD data insertion failed")
            return False
        
        # Test EOD data
        eod_data = {
            "rating": "8",
            "summary": "Test summary",
            "accomplishments": "Test accomplishments"
        }
        
        eod_success = db_manager.upsert_eod_data(test_date, eod_data)
        if eod_success:
            print("✅ EOD data insertion successful")
        else:
            print("❌ EOD data insertion failed")
            return False
        
        # Test data retrieval
        entry = db_manager.get_daily_entry(test_date)
        if entry and entry['sod_data'] and entry['eod_data']:
            print("✅ Data retrieval successful")
            print(f"   SOD fields: {len(entry['sod_data'])}")
            print(f"   EOD fields: {len(entry['eod_data'])}")
        else:
            print("❌ Data retrieval failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ SOD/EOD operations failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n🔍 Testing Configuration...")
    print("-" * 50)
    
    try:
        # Test basic config attributes
        required_attrs = [
            'DB_NAME', 'DB_USER', 'DB_HOST', 'DB_PORT',
            'NOTION_ENABLED', 'OBSIDIAN_GOALS_ENABLED', 'GOOGLE_DRIVE_ENABLED',
            'TESTING', 'DEBUG'
        ]
        
        missing_attrs = []
        for attr in required_attrs:
            if not hasattr(Config, attr):
                missing_attrs.append(attr)
            else:
                print(f"✅ {attr}: {getattr(Config, attr)}")
        
        if missing_attrs:
            print(f"❌ Missing config attributes: {missing_attrs}")
            return False
        
        # Test database URL generation
        db_url = Config.get_db_url()
        if db_url and 'postgresql://' in db_url:
            print(f"✅ Database URL: {db_url}")
        else:
            print(f"❌ Invalid database URL: {db_url}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_workflow_validation():
    """Test workflow validation logic"""
    print("\n🔍 Testing Workflow Validation...")
    print("-" * 50)
    
    try:
        db_manager = DatabaseManager()
        test_date = date.today()
        
        # Test previous day completion check
        prev_complete, prev_message = db_manager.check_previous_day_completion(test_date)
        print(f"✅ Previous day check: {prev_message}")
        
        # Test current day SOD check
        sod_complete, sod_message = db_manager.check_current_day_sod(test_date)
        print(f"✅ Current SOD check: {sod_message}")
        
        return True
    except Exception as e:
        print(f"❌ Workflow validation failed: {e}")
        return False

def main():
    """Run all core functionality tests"""
    print("🧪 Core Functionality Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("SOD/EOD Operations", test_sod_eod_operations),
        ("Configuration", test_configuration),
        ("Workflow Validation", test_workflow_validation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All core functionality tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)