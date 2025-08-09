#!/usr/bin/env python3
"""
Test script for Notion API integration.
Tests connection, content parsing, and integration with markdown generation.
"""

import os
<<<<<<< HEAD
from datetime import datetime, date
=======
import sys
from datetime import datetime, date
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
>>>>>>> origin/main

from config import Config
from notion_manager import NotionManager
from database import DatabaseManager
from markdown_generator import MarkdownGenerator

def test_notion_connection():
    """Test basic Notion API connection and configuration."""
    print("🔍 Testing Notion API Connection...")
    print("-" * 50)
    
    # Check configuration
    print(f"NOTION_ENABLED: {Config.NOTION_ENABLED}")
    print(f"NOTION_API_TOKEN: {'✅ Set' if Config.NOTION_API_TOKEN else '❌ Not set'}")
    print(f"NOTION_DAILY_CAPTURE_PAGE_ID: {'✅ Set' if Config.NOTION_DAILY_CAPTURE_PAGE_ID else '❌ Not set'}")
    print()
    
    if not Config.NOTION_ENABLED:
        print("❌ Notion integration is disabled. Set NOTION_ENABLED=true")
        return False
    
    if not Config.NOTION_API_TOKEN or not Config.NOTION_DAILY_CAPTURE_PAGE_ID:
        print("❌ Notion API token or page ID not configured")
        return False
    
    # Test connection
    notion_manager = NotionManager()
    test_result = notion_manager.test_connection()
    
    if test_result['success']:
        print("✅ Notion API connection successful")
        print(f"   Page title: {test_result.get('page_title', 'Unknown')}")
        print(f"   Page ID: {test_result['page_id']}")
        return True
    else:
        print(f"❌ Notion API connection failed: {test_result['error']}")
        return False

def test_notion_content_parsing():
    """Test reading and parsing content from Notion Daily Capture page."""
    print("\n🔍 Testing Notion Content Parsing...")
    print("-" * 50)
    
    notion_manager = NotionManager()
    
    # Get content from Notion
    result = notion_manager.get_daily_capture_content()
    
    if not result['success']:
        print(f"❌ Failed to get content: {result['error']}")
        return False, None
    
    content = result['content']
    block_count = result['block_count']
    
    print(f"✅ Successfully read {block_count} blocks from Notion")
    print(f"   Found {len(content)} content sections")
    
    if content:
        print("\n📝 Parsed Content Structure:")
        for header, items in content.items():
            print(f"   📁 {header}: {len(items)} items")
            for item in items[:2]:  # Show first 2 items
                print(f"      • {item[:50]}{'...' if len(item) > 50 else ''}")
            if len(items) > 2:
                print(f"      ... and {len(items) - 2} more items")
        
        # Test markdown formatting
        print("\n📝 Formatted Markdown Preview:")
        markdown_content = notion_manager.format_content_for_markdown(content)
        preview_lines = markdown_content.split('\n')[:10]
        for line in preview_lines:
            print(f"   {line}")
        if len(markdown_content.split('\n')) > 10:
            print("   ...")
        
        return True, content
    else:
        print("ℹ️ No content found in Daily Capture page")
        return True, None

def test_markdown_integration():
    """Test integration with markdown generation."""
    print("\n🔍 Testing Markdown Integration...")
    print("-" * 50)
    
    # Create a test daily entry
    test_date = date.today()
    
    test_sod_data = {
        "What am I looking forward to the most today?": "Testing Notion integration",
        "Today's Big 3": "1. Test Notion API\n2. Verify content parsing\n3. Check markdown generation",
        "3 things I'm grateful for in my life:": "Health\nFamily\nTechnology",
        "3 things I'm grateful about myself:": "Persistence\nCuriosity\nGrowth mindset"
    }
    
    test_eod_data = {
        "Rating": "8",
        "Summary": "Successful day testing Notion integration",
        "Story": "The moment when the API connection worked perfectly",
        "Accomplishments": "Built and tested Notion integration",
        "Obstacles": "Initial API authentication issues",
        "Physical": "7",
        "Mental": "8",
        "Emotional": "8",
        "Spiritual": "7",
        "What did you do to re-energize? How did it go?": "Took a short walk, very refreshing",
        "What can I do tomorrow to be 1% better?": "Document the integration process better"
    }
    
    # Create test daily entry
    test_entry = {
        'date': test_date,
        'sod_data': test_sod_data,
        'sod_timestamp': datetime.now(),
        'eod_data': test_eod_data,
        'eod_timestamp': datetime.now()
    }
    
    print(f"📄 Generating test markdown for {test_date}")
    
    # Generate markdown with Notion integration
    markdown_gen = MarkdownGenerator()
    result_path = markdown_gen.generate_daily_template(test_entry)
    
    if result_path and os.path.exists(result_path):
        print(f"✅ Markdown generated successfully: {result_path}")
        
        # Check if Notion content was integrated
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "#### From Daily Capture" in content:
            print("✅ Notion content successfully integrated into markdown")
            
            # Show preview of integrated content
            lines = content.split('\n')
            capture_start = None
            for i, line in enumerate(lines):
                if "#### From Daily Capture" in line:
                    capture_start = i
                    break
            
            if capture_start:
                print("\n📝 Integrated Content Preview:")
                preview_end = min(capture_start + 10, len(lines))
                for line in lines[capture_start:preview_end]:
                    print(f"   {line}")
                if preview_end < len(lines):
                    print("   ...")
        else:
            print("ℹ️ No Notion content found in generated markdown (page may be empty)")
        
        return True
    else:
        print("❌ Failed to generate markdown")
        return False

def test_notion_cleanup():
    """Test clearing the Notion Daily Capture page."""
    print("\n🔍 Testing Notion Page Cleanup...")
    print("-" * 50)
    
    notion_manager = NotionManager()
    
    # Get current content first
    before_result = notion_manager.get_daily_capture_content()
    
    if not before_result['success']:
        print(f"❌ Failed to read page before cleanup: {before_result['error']}")
        return False
    
    before_sections = len(before_result['content'])
    before_blocks = before_result['block_count']
    
    print(f"📊 Before cleanup: {before_blocks} blocks, {before_sections} content sections")
    
    if before_blocks == 0:
        print("ℹ️ Page is already empty, nothing to clean up")
        return True
    
    # Perform cleanup
    cleanup_result = notion_manager.clear_daily_capture_page()
    
    if not cleanup_result['success']:
        print(f"❌ Failed to clear page: {cleanup_result['error']}")
        return False
    
    deleted_blocks = cleanup_result['deleted_blocks']
    print(f"✅ Successfully deleted {deleted_blocks} blocks")
    
    # Verify cleanup
    after_result = notion_manager.get_daily_capture_content()
    
    if after_result['success']:
        after_blocks = after_result['block_count']
        after_sections = len(after_result['content'])
        
        print(f"📊 After cleanup: {after_blocks} blocks, {after_sections} content sections")
        
        if after_blocks == 0:
            print("✅ Page successfully cleared")
            return True
        else:
            print(f"⚠️ Page not completely cleared ({after_blocks} blocks remaining)")
            return False
    else:
        print(f"❌ Failed to verify cleanup: {after_result['error']}")
        return False

def prompt_user_choice():
    """Prompt user for which tests to run."""
    print("🧪 Notion Integration Test Suite")
    print("=" * 50)
    print("Available tests:")
    print("1. Connection Test - Test API connection and configuration")
    print("2. Content Parsing Test - Read and parse Notion page content")
    print("3. Markdown Integration Test - Test full integration with daily notes")
    print("4. Cleanup Test - Test clearing the Notion page")
    print("5. Full Test Suite - Run all tests")
    print()
    
    while True:
        choice = input("Enter your choice (1-5) or 'q' to quit: ").strip()
        
        if choice.lower() == 'q':
            return None
        
        if choice in ['1', '2', '3', '4', '5']:
            return int(choice)
        
        print("Invalid choice. Please enter 1-5 or 'q'.")

def main():
    """Main test function."""
    choice = prompt_user_choice()
    
    if choice is None:
        print("Goodbye!")
        return
    
    success_count = 0
    total_tests = 0
    
    try:
        if choice == 1 or choice == 5:
            total_tests += 1
            if test_notion_connection():
                success_count += 1
        
        if choice == 2 or choice == 5:
            total_tests += 1
            success, content = test_notion_content_parsing()
            if success:
                success_count += 1
        
        if choice == 3 or choice == 5:
            total_tests += 1
            if test_markdown_integration():
                success_count += 1
        
        if choice == 4 or choice == 5:
            total_tests += 1
            if test_notion_cleanup():
                success_count += 1
        
        # Run specific single test
        if choice == 1:
            test_notion_connection()
        elif choice == 2:
            test_notion_content_parsing()
        elif choice == 3:
            test_markdown_integration()
        elif choice == 4:
            test_notion_cleanup()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        return
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if choice == 5:
        print("\n" + "=" * 50)
        print("🏁 Test Suite Complete")
        print(f"✅ {success_count}/{total_tests} tests passed")
        
        if success_count == total_tests:
            print("🎉 All tests passed! Notion integration is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()