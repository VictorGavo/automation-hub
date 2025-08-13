#!/usr/bin/env python3
"""
Debug Notion Capture Insertion
Let's trace through what's happening in the capture processing
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from modules.daily_capture import DailyCaptureManager
from modules.daily_books import DailyBooksManager

def debug_capture_processing():
    """Debug the capture processing step by step"""
    print("🔍 Debugging Notion Capture Processing...")
    print("="*50)
    
    # Get yesterday's entry (should have both SOD and EOD data)
    test_date = date(2025, 8, 13)
    
    # Get the daily entry
    books_manager = DailyBooksManager()
    entry_result = books_manager.get_daily_entry(test_date)
    
    if not entry_result.is_valid:
        print(f"❌ Failed to get daily entry: {entry_result.message}")
        return
    
    daily_entry = entry_result.data
    print(f"✅ Retrieved daily entry for {test_date}")
    print(f"   SOD data: {bool(daily_entry['sod_data'])}")
    print(f"   EOD data: {bool(daily_entry['eod_data'])}")
    
    # Test the capture manager
    capture_manager = DailyCaptureManager()
    
    # Test just the notion integration part
    print("\n🔍 Testing Notion Integration...")
    notion_result = capture_manager.notion_integration.process_daily_captures(daily_entry)
    
    print(f"Result valid: {notion_result.is_valid}")
    print(f"Message: {notion_result.message}")
    
    if notion_result.data:
        data = notion_result.data
        print(f"Captures processed: {data.get('captures_processed', False)}")
        print(f"Sections imported: {data.get('sections_imported', 0)}")
        print(f"Blocks cleared: {data.get('blocks_cleared', 0)}")
        
        if data.get('content'):
            content = data['content']
            print(f"\n📝 Generated content ({len(content)} chars):")
            print("─" * 30)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("─" * 30)
        else:
            print("❌ No content generated")
    
    # Test markdown generation separately
    print("\n🔍 Testing Markdown Generation...")
    markdown_result = capture_manager.markdown_manager.regenerate_template(daily_entry)
    
    print(f"Markdown valid: {markdown_result.is_valid}")
    print(f"Message: {markdown_result.message}")
    
    if markdown_result.data:
        print(f"Template generated: {markdown_result.data.get('template_generated', False)}")
        print(f"Path: {markdown_result.data.get('path')}")

def test_simple_insertion():
    """Test the insertion logic with sample data"""
    print("\n🧪 Testing Insertion Logic...")
    print("="*50)
    
    # Create sample content
    sample_content = """#### 💭 Quick Capture
* Testing fresh workflow on 2025-08-13
* This content should be imported
* Clean database test
* Final validation of the automation"""
    
    # Create sample markdown lines
    sample_lines = [
        "## Today",
        "",
        "### Captured Notes",
        "```dataview",
        "list",
        "where tags = \"#note/🌱\" and file.cday = this.file.cday", 
        "```",
        "",
        "### Created Notes",
        "```dataview",
        "list", 
        "where file.cday = this.file.cday",
        "```"
    ]
    
    print("📝 Sample content to insert:")
    print(sample_content)
    
    print(f"\n📄 Sample markdown structure ({len(sample_lines)} lines)")
    
    # Import the insertion function
    from markdown_generator import MarkdownGenerator
    generator = MarkdownGenerator()
    
    # Test insertion
    try:
        updated_lines = generator._insert_notion_captures(sample_lines, sample_content)
        print(f"\n✅ Insertion successful! {len(updated_lines)} lines total")
        
        # Show the result
        print("\n📋 Result preview:")
        for i, line in enumerate(updated_lines):
            marker = ">>> " if "Daily Capture" in line or "Quick Capture" in line else "    "
            print(f"{marker}{i+1:2}: {line}")
            
    except Exception as e:
        print(f"❌ Insertion failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_capture_processing()
    test_simple_insertion()