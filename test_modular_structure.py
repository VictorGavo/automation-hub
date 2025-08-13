#!/usr/bin/env python3
"""
Modular Integration Test Runner
Tests the new modular structure with proper error handling
"""

import sys
import os
import subprocess
import time
import requests
from datetime import date, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_modular_imports():
    """Test that all modular components can be imported"""
    print("🧪 Testing Modular Imports...")
    print("-" * 50)
    
    try:
        # Test core modules
        from modules.core import CoreUtils, DatabaseContext, ValidationResult
        from modules.daily_books import DailyBooksManager
        from modules.daily_capture import DailyCaptureManager
        from modules.webhook_handlers import create_webhook_handlers, create_api_handlers
        
        print("✅ All modular imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_managers_creation():
    """Test that all managers can be created"""
    print("\n🧪 Testing Manager Creation...")
    print("-" * 50)
    
    try:
        from modules.daily_books import DailyBooksManager
        from modules.daily_capture import DailyCaptureManager
        from modules.webhook_handlers import create_webhook_handlers, create_api_handlers
        
        # Create managers
        daily_books = DailyBooksManager()
        daily_capture = DailyCaptureManager()
        webhook_handlers = create_webhook_handlers()
        api_handlers = create_api_handlers()
        
        print("✅ DailyBooksManager created")
        print("✅ DailyCaptureManager created")
        print("✅ WebhookHandlers created")
        print("✅ APIHandlers created")
        
        return True
    except Exception as e:
        print(f"❌ Manager creation failed: {e}")
        return False

def test_database_operations():
    """Test database operations through the modular structure"""
    print("\n🧪 Testing Database Operations...")
    print("-" * 50)
    
    try:
        from modules.daily_books import DailyBooksManager
        
        manager = DailyBooksManager()
        test_date = date.today() - timedelta(days=2)  # Use day before yesterday
        
        # Test SOD processing
        sod_data = {
            "highlight": "Test modular highlight",
            "big3": "1. Modular test 1\n2. Modular test 2\n3. Modular test 3"
        }
        
        sod_result = manager.process_sod(sod_data, test_date)
        if sod_result.is_valid:
            print("✅ SOD processing successful")
        else:
            print(f"❌ SOD processing failed: {sod_result.message}")
            return False
        
        # Test EOD processing
        eod_data = {
            "rating": "9",
            "summary": "Test modular summary"
        }
        
        eod_result = manager.process_eod(eod_data, test_date)
        if eod_result.is_valid:
            print("✅ EOD processing successful")
        else:
            print(f"❌ EOD processing failed: {eod_result.message}")
            return False
        
        # Test data retrieval
        entry_result = manager.get_daily_entry(test_date)
        if entry_result.is_valid and entry_result.data:
            print("✅ Data retrieval successful")
            entry = entry_result.data
            print(f"   SOD data: {bool(entry['sod_data'])}")
            print(f"   EOD data: {bool(entry['eod_data'])}")
        else:
            print("❌ Data retrieval failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Database operations failed: {e}")
        return False

def test_markdown_generation():
    """Test markdown generation through modular structure"""
    print("\n🧪 Testing Markdown Generation...")
    print("-" * 50)
    
    try:
        from modules.daily_capture import DailyCaptureManager
        from modules.daily_books import DailyBooksManager
        
        # Get a daily entry
        books_manager = DailyBooksManager()
        capture_manager = DailyCaptureManager()
        
        test_date = date.today() - timedelta(days=2)
        entry_result = books_manager.get_daily_entry(test_date)
        
        if not entry_result.is_valid or not entry_result.data:
            print("⚠️ No test data available for markdown generation")
            return True  # Skip this test
        
        # Test markdown generation
        markdown_result = capture_manager.markdown_manager.regenerate_template(entry_result.data)
        
        if markdown_result.is_valid:
            print("✅ Markdown generation successful")
            print(f"   Template path: {markdown_result.data.get('path')}")
        else:
            print(f"❌ Markdown generation failed: {markdown_result.message}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Markdown generation failed: {e}")
        return False

def test_integration_status():
    """Test integration status (without requiring them to be enabled)"""
    print("\n🧪 Testing Integration Status...")
    print("-" * 50)
    
    try:
        from config import Config
        from modules.daily_capture import DailyCaptureManager
        
        capture_manager = DailyCaptureManager()
        
        # Test Notion integration status
        print(f"📝 Notion enabled: {Config.NOTION_ENABLED}")
        if Config.NOTION_ENABLED:
            notion_test = capture_manager.test_notion_connection()
            print(f"   Connection test: {notion_test.is_valid}")
        
        # Test Obsidian goals status
        print(f"🎯 Obsidian goals enabled: {Config.OBSIDIAN_GOALS_ENABLED}")
        
        # Test Google Drive status
        print(f"📁 Google Drive enabled: {Config.GOOGLE_DRIVE_ENABLED}")
        
        print("✅ Integration status checked")
        return True
    except Exception as e:
        print(f"❌ Integration status check failed: {e}")
        return False

def check_flask_app_running():
    """Check if Flask app is running"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=2)
        return response.status_code == 200
    except:
        return False

def test_webhook_endpoints():
    """Test webhook endpoints if Flask app is running"""
    print("\n🧪 Testing Webhook Endpoints...")
    print("-" * 50)
    
    if not check_flask_app_running():
        print("⚠️ Flask app not running, skipping webhook tests")
        print("   Start with: python app.py")
        return True  # Skip but don't fail
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:5000/health')
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health endpoint working")
            print(f"   Modules loaded: {health_data.get('modules', {})}")
        else:
            print("❌ Health endpoint failed")
            return False
        
        # Test SOD webhook with test data
        test_date = (date.today() - timedelta(days=3)).strftime('%Y-%m-%d')
        sod_data = {"test": "modular_sod_data", "highlight": "Test highlight"}
        
        response = requests.post(
            f'http://localhost:5000/webhook/sod?test_date={test_date}',
            json=sod_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ SOD webhook working")
        else:
            print(f"❌ SOD webhook failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
        return False

def main():
    """Run all modular integration tests"""
    print("🚀 Modular Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Modular Imports", test_modular_imports),
        ("Manager Creation", test_managers_creation),
        ("Database Operations", test_database_operations),
        ("Markdown Generation", test_markdown_generation),
        ("Integration Status", test_integration_status),
        ("Webhook Endpoints", test_webhook_endpoints)
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result is True:
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            elif result is None:
                skipped += 1
                print(f"\n⏭️ {test_name}: SKIPPED")
            else:
                failed += 1
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("🎉 All modular integration tests passed!")
        print("\nNext steps:")
        print("1. Start Flask app: python app.py")
        print("2. Test webhooks manually or with existing test suite")
        print("3. Deploy when ready!")
        return True
    else:
        print("⚠️ Some tests failed. Check errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)