#!/usr/bin/env python3
"""
Debug script to see what content is currently in the Notion Daily Capture page.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_manager import NotionManager
from config import Config

def debug_notion_content():
    """Debug the current content in Notion Daily Capture page."""
    print("🔍 Debugging Notion Daily Capture Content")
    print("=" * 50)
    
    if not Config.NOTION_ENABLED:
        print("❌ Notion integration is disabled")
        return
    
    notion_manager = NotionManager()
    
    # Test connection first
    test_result = notion_manager.test_connection()
    if not test_result['success']:
        print(f"❌ Connection failed: {test_result['error']}")
        return
    
    print(f"✅ Connected to page: {test_result['page_title']}")
    print()
    
    # Get current content
    result = notion_manager.get_daily_capture_content()
    
    if not result['success']:
        print(f"❌ Failed to read content: {result['error']}")
        return
    
    content = result['content']
    block_count = result['block_count']
    
    print(f"📊 Total blocks: {block_count}")
    print(f"📊 Content sections: {len(content)}")
    print()
    
    if not content:
        print("📄 Page is empty or has no structured content")
        return
    
    # Show all content sections
    print("📝 All Content Sections:")
    print("-" * 30)
    
    for header, items in content.items():
        print(f"📁 {header}")
        print(f"   Items: {len(items)}")
        
        for i, item in enumerate(items, 1):
            if len(item) > 60:
                item_preview = item[:57] + "..."
            else:
                item_preview = item
            print(f"   {i}. {item_preview}")
        print()
    
    # Test markdown formatting
    print("🔄 Testing Markdown Formatting:")
    print("-" * 30)
    
    markdown_result = notion_manager.format_content_for_markdown(content)
    
    if markdown_result.strip():
        print("Generated markdown:")
        print(markdown_result)
    else:
        print("❌ No markdown generated (no Quick Capture sections found)")
        
        # Check what headers we're looking for vs what exists
        quick_capture_headers = ['💭 Quick Capture', 'Quick Capture', 'Capture']
        existing_headers = list(content.keys())
        
        print(f"\nLooking for headers containing: {quick_capture_headers}")
        print(f"Found headers: {existing_headers}")
        
        # Check for partial matches
        print("\nPartial match analysis:")
        for existing_header in existing_headers:
            matches = [qc_header for qc_header in quick_capture_headers if qc_header in existing_header]
            if matches:
                print(f"   '{existing_header}' matches: {matches}")
            else:
                print(f"   '{existing_header}' - no matches")

if __name__ == "__main__":
    debug_notion_content()