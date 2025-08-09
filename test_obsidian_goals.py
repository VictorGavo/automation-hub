#!/usr/bin/env python3
"""
Test script for Obsidian goals integration.
"""

import sys
import os
from datetime import datetime, date

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from obsidian_goal_manager import ObsidianGoalManager
from config import Config

def test_obsidian_access():
    """Test basic Obsidian vault access."""
    print("🔍 Testing Obsidian Vault Access...")
    print("-" * 50)
    
    goal_manager = ObsidianGoalManager()
    result = goal_manager.test_obsidian_access()
    
    print(f"✅ Vault path: {result['vault_path']}")
    print(f"✅ Vault exists: {result['vault_exists']}")
    print(f"✅ Goals folder: {result['goals_folder']}")
    print(f"✅ Goals folder exists: {result['goals_folder_exists']}")
    
    if result['success']:
        print(f"\n📁 Found {len(result['goal_files'])} goal files:")
        for goal_file in result['goal_files']:
            if goal_file.get('readable', False):
                print(f"   📄 {goal_file['filename']}")
                print(f"      Timeframe: {goal_file['timeframe']}")
                print(f"      Description: {goal_file['description']}")
            else:
                print(f"   ❌ {goal_file['filename']} - {goal_file.get('error', 'Unknown error')}")
        return True
    else:
        print(f"\n❌ Errors found:")
        for error in result['errors']:
            print(f"   {error}")
        return False

def test_timeframe_calculation():
    """Test timeframe calculation for current date."""
    print("\n🔍 Testing Timeframe Calculation...")
    print("-" * 50)
    
    goal_manager = ObsidianGoalManager()
    today = date.today()
    timeframes = goal_manager._calculate_timeframes(today)
    
    print(f"📅 Date: {today}")
    print(f"📅 Timeframes calculated:")
    for timeframe_type, value in timeframes.items():
        print(f"   {timeframe_type.capitalize()}: {value}")
    
    return timeframes

def test_goal_loading():
    """Test loading goals for current timeframes."""
    print("\n🔍 Testing Goal Loading...")
    print("-" * 50)
    
    goal_manager = ObsidianGoalManager()
    result = goal_manager.get_current_goals()
    
    print(f"📊 Cache used: {result['cache_used']}")
    print(f"📊 Last updated: {result['last_updated']}")
    print(f"📊 Timeframes: {result['timeframes']}")
    
    print(f"\n🎯 Goals found:")
    goals_data = result['goals']
    
    for timeframe_type, goal_info in goals_data.items():
        print(f"\n   {timeframe_type.upper()}:")
        if goal_info.get('found', False):
            print(f"      ✅ {goal_info['title']}")
            print(f"      📝 {goal_info['description'][:50]}...")
            print(f"      🎯 {goal_info['why'][:50]}..." if goal_info['why'] else "      🎯 No 'why' specified")
            print(f"      📊 Status: {goal_info.get('status', 'No status')}")
        else:
            print(f"      ❌ {goal_info.get('error', 'Not found')}")
            print(f"      💡 {goal_info.get('summary', 'No summary')}")
    
    return result

def test_notion_formatting():
    """Test formatting goals for Notion."""
    print("\n🔍 Testing Notion Formatting...")
    print("-" * 50)
    
    goal_manager = ObsidianGoalManager()
    result = goal_manager.get_current_goals()
    notion_blocks = goal_manager.format_goals_for_notion(result['goals'])
    
    print(f"📦 Generated {len(notion_blocks)} Notion blocks")
    print(f"\n📝 Block preview:")
    
    for i, block in enumerate(notion_blocks[:10]):  # Show first 10 blocks
        block_type = block.get('type', 'unknown')
        
        if block_type == 'heading_1':
            content = block['heading_1']['rich_text'][0]['text']['content']
            print(f"   {i+1}. HEADING: {content}")
        elif block_type == 'paragraph':
            content = block['paragraph']['rich_text'][0]['text']['content']
            print(f"   {i+1}. PARAGRAPH: {content[:60]}...")
        elif block_type == 'bulleted_list_item':
            content = block['bulleted_list_item']['rich_text'][0]['text']['content']
            print(f"   {i+1}. BULLET: {content[:60]}...")
        else:
            print(f"   {i+1}. {block_type.upper()}: {str(block)[:50]}...")
    
    if len(notion_blocks) > 10:
        print(f"   ... and {len(notion_blocks) - 10} more blocks")
    
    return notion_blocks

def test_cache_behavior():
    """Test caching behavior."""
    print("\n🔍 Testing Cache Behavior...")
    print("-" * 50)
    
    goal_manager = ObsidianGoalManager()
    
    # First call - should load from Obsidian
    print("📚 First call (should read from Obsidian):")
    result1 = goal_manager.get_current_goals()
    print(f"   Cache used: {result1['cache_used']}")
    
    # Second call - should use cache
    print("📚 Second call (should use cache):")
    result2 = goal_manager.get_current_goals()
    print(f"   Cache used: {result2['cache_used']}")
    
    # Clear cache and try again
    print("📚 Clearing cache...")
    goal_manager.clear_cache()
    
    print("📚 Third call (should read from Obsidian again):")
    result3 = goal_manager.get_current_goals()
    print(f"   Cache used: {result3['cache_used']}")
    
    return result1, result2, result3

def run_full_test():
    """Run all tests."""
    print("🧪 Obsidian Goals Integration Test")
    print("=" * 60)
    
    # Test 1: Basic access
    if not test_obsidian_access():
        print("\n❌ Basic access test failed. Check your vault path.")
        return False
    
    # Test 2: Timeframe calculation  
    timeframes = test_timeframe_calculation()
    
    # Test 3: Goal loading
    goals_result = test_goal_loading()
    
    # Test 4: Notion formatting
    notion_blocks = test_notion_formatting()
    
    # Test 5: Cache behavior
    cache_results = test_cache_behavior()
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 Test Summary")
    print("=" * 60)
    
    goals_found = sum(1 for goal in goals_result['goals'].values() if goal.get('found', False))
    total_goals = len(goals_result['goals'])
    
    print(f"✅ Vault access: Working")
    print(f"✅ Timeframes: {len(timeframes)} calculated")
    print(f"✅ Goals loaded: {goals_found}/{total_goals} found")
    print(f"✅ Notion blocks: {len(notion_blocks)} generated")
    print(f"✅ Cache: Working")
    
    if goals_found > 0:
        print(f"\n🎉 Integration test successful!")
        print(f"Ready to integrate with SOD webhook.")
    else:
        print(f"\n⚠️ No goals found matching current timeframes.")
        print(f"Create some goal files in Obsidian with these timeframes:")
        for timeframe_type, value in timeframes.items():
            print(f"   - {timeframe_type.capitalize()}: {value}")
    
    return goals_found > 0

if __name__ == "__main__":
    try:
        run_full_test()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()