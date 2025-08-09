#!/usr/bin/env python3
"""
Core functionality tests - consolidated from multiple debug scripts
"""
import os
import sys
from datetime import date, datetime
from database import DatabaseManager
from config import Config, DATABASE_CONFIG
from markdown_generator import MarkdownGenerator


def test_database_connection():
    """Test database connection and basic operations"""
    print("Testing database connection...")
    
    db = DatabaseManager(DATABASE_CONFIG)
    try:
        db.connect()
        print("✅ Database connection successful")
        
        db.create_tables()
        print("✅ Tables created successfully")
        
        # Test data insertion
        test_data = {
            "What am I looking forward to the most today?": "Testing core functionality",
            "Today's Big 3": "1. Clean test files\n2. Consolidate functionality\n3. Remove tech debt",
            "3 things I'm grateful for in my life:": "Automation\nClean code\nEfficiency"
        }
        
        db.insert_sod_response(date.today(), test_data)
        print("✅ Test data inserted successfully")
        
        result = db.get_sod_response(date.today())
        if result:
            print(f"✅ Data retrieved: {result.get('highlight', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    finally:
        db.disconnect()


def test_markdown_generation():
    """Test markdown generation functionality"""
    print("\nTesting markdown generation...")
    
    try:
        generator = MarkdownGenerator()
        print(f"✅ MarkdownGenerator initialized - Drive manager: {generator.drive_manager}")
        
        # Test with mock data
        today = date.today()
        mock_entry = {
            'date': today,
            'sod_data': {
                "What am I looking forward to the most today?": "Core functionality testing",
                "Today's Big 3": "Clean tests\nRemove debt\nImprove code"
            },
            'sod_timestamp': datetime.now(),
            'eod_data': None,
            'eod_timestamp': None
        }
        
        result = generator.generate_daily_template(mock_entry)
        if result and os.path.exists(result):
            print(f"✅ Markdown generated: {result}")
            return True
        else:
            print("❌ Markdown generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Markdown test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading and environment variables"""
    print("\nTesting configuration...")
    
    try:
        print(f"Database Host: {Config.DB_HOST}")
        print(f"Database Name: {Config.DB_NAME}")
        print(f"Testing Mode: {Config.TESTING}")
        print(f"Google Drive Enabled: {Config.GOOGLE_DRIVE_ENABLED}")
        print(f"Google Drive Sync Path: {Config.GOOGLE_DRIVE_SYNC_PATH}")
        print("✅ Configuration loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def run_all_tests():
    """Run all core functionality tests"""
    print("=" * 60)
    print("CORE FUNCTIONALITY TESTS")
    print("=" * 60)
    
    tests = [
        test_configuration,
        test_database_connection,
        test_markdown_generation
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
