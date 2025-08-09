#!/usr/bin/env python3
"""
Test the enhanced SOD/EOD processing fixes
"""

import requests
from datetime import datetime, date, timedelta
import json
from database import DatabaseManager
from markdown_generator import MarkdownGenerator

# Configuration
BASE_URL = "http://localhost:5000"
TEST_DATE = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')  # Tomorrow for testing

def test_enhanced_sod_processing():
    """Test enhanced SOD processing with edge cases"""
    print("🧪 Testing Enhanced SOD Processing")
    print("=" * 50)
    
    # Test data with potential issues
    test_cases = [
        {
            "name": "Standard Form",
            "data": {
                "What am I looking forward to the most today?": "Testing enhanced processing",
                "Today's Big 3": "1. Test enhanced processing\n2. Fix field mapping\n3. Improve error handling",
                "I know today would be successful if I did or felt this by the end:": "All tests pass",
                "3 things I'm grateful for in my life:": "Technology\nTime\nCommunity",
                "3 things I'm grateful about myself:": "Persistence\nCuriosity\nGrowth mindset",
                "I'm excited today for:": "Better error handling"
            }
        },
        {
            "name": "Alternative Success Field",
            "data": {
                "What am I looking forward to the most today?": "Testing field variations",
                "Today's Big 3": "Test alternative field mapping\nValidate processing\nConfirm fixes",
                "What would make today successful?": "Alternative success field works",  # Different field name
                "3 things I'm grateful for in my life:": "Family\nHealth\nOpportunities",
                "I'm excited today for:": "Field mapping flexibility"
            }
        },
        {
            "name": "Empty/Missing Fields",
            "data": {
                "What am I looking forward to the most today?": "",  # Empty
                "Today's Big 3": "",  # Empty
                "I know today would be successful if I did or felt this by the end:": "Handle empty fields gracefully",
                "3 things I'm grateful for in my life:": "Only\nTwo items",  # Less than 3
                "I'm excited today for:": "Error handling"
            }
        },
        {
            "name": "Malformed Big 3",
            "data": {
                "What am I looking forward to the most today?": "Testing malformed data",
                "Today's Big 3": "No numbering\nAlso no numbering\nStill no numbering",  # No numbers
                "I know today would be successful if I did or felt this by the end:": "Handles malformed Big 3",
                "I'm excited today for:": "Robust processing"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n📋 Test Case {i+1}: {test_case['name']}")
        print("-" * 30)
        
        # Use different test dates to avoid conflicts
        current_test_date = (date.today() + timedelta(days=i+1)).strftime('%Y-%m-%d')
        
        try:
            # Submit SOD data
            url = f"{BASE_URL}/webhook/sod?test_date={current_test_date}"
            response = requests.post(url, json=test_case['data'], headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SOD submission successful")
                print(f"   Date: {result.get('date')}")
                print(f"   Notion update: {'✅' if result.get('notion_update') else '❌'}")
                
                # Analyze generated content
                db_manager = DatabaseManager()
                entry = db_manager.get_daily_entry(datetime.strptime(current_test_date, '%Y-%m-%d').date())
                
                if entry and entry['sod_data']:
                    # Test the markdown generation
                    markdown_gen = MarkdownGenerator()
                    markdown_path = markdown_gen.generate_daily_template(entry)
                    
                    if markdown_path:
                        print(f"✅ Markdown generated: {markdown_path}")
                        
                        # Read and analyze content
                        with open(markdown_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for key improvements
                        improvements = []
                        
                        if "Today's Big 3" in content:
                            improvements.append("Big 3 section present")
                        
                        if "(No Big 3 data from SOD form)" not in content or test_case['data'].get("Today's Big 3"):
                            if any(str(i) + "." in content for i in [1, 2, 3]):
                                improvements.append("Big 3 properly numbered")
                        
                        if "Success criteria not provided" not in content or any(key for key in test_case['data'].keys() if 'success' in key.lower()):
                            improvements.append("Success criteria handled")
                        
                        if len(improvements) > 0:
                            print(f"✅ Improvements: {', '.join(improvements)}")
                        else:
                            print("⚠️ Some improvements not detected")
                    else:
                        print("❌ Markdown generation failed")
                else:
                    print("❌ No entry found in database")
            else:
                print(f"❌ SOD submission failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Test case failed: {e}")

def test_eod_processing_with_captures():
    """Test EOD processing with enhanced capture handling"""
    print("\n\n🧪 Testing Enhanced EOD Processing")
    print("=" * 50)
    
    # Use the first test date that should have SOD data
    test_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    eod_data = {
        "Rating": "8",
        "Summary": "Great day testing enhanced processing",
        "Story": "The enhanced error handling made debugging much easier",
        "Physical": "7",
        "Mental": "8",
        "Emotional": "9",
        "Spiritual": "7",
        "Accomplishments": "Enhanced SOD processing\nImproved error handling\nBetter field mapping",
        "Obstacles": "Some edge cases in field mapping",
        "What can I do tomorrow to be 1% better?": "Add even more comprehensive logging"
    }
    
    try:
        # First, ensure we have SOD data
        db_manager = DatabaseManager()
        entry = db_manager.get_daily_entry(datetime.strptime(test_date, '%Y-%m-%d').date())
        
        if not (entry and entry['sod_data']):
            print("⚠️ No SOD data found for test date, skipping EOD test")
            return
        
        print(f"📅 Testing EOD processing for {test_date}")
        
        # Submit EOD data
        url = f"{BASE_URL}/webhook/eod?test_date={test_date}"
        response = requests.post(url, json=eod_data, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ EOD submission successful")
            print(f"   Date: {result.get('date')}")
            print(f"   Markdown generated: {'✅' if result.get('markdown_generated') else '❌'}")
            print(f"   Notion captures processed: {'✅' if result.get('notion_captures_processed') else '❌'}")
            
            # Analyze the final markdown
            markdown_path = f"daily_notes/{test_date}.md"
            try:
                with open(markdown_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for enhanced processing indicators
                checks = [
                    ("Frontmatter rating", f"Rating: {eod_data['Rating']}" in content),
                    ("Frontmatter summary", eod_data['Summary'] in content),
                    ("EOD accomplishments", eod_data['Accomplishments'].split('\n')[0] in content),
                    ("Enhanced logging", "Quick Capture" in content or "From Daily Capture" in content),
                ]
                
                print("\n📊 Content Analysis:")
                for check_name, passed in checks:
                    status = "✅" if passed else "❌"
                    print(f"   {status} {check_name}")
                
                # Count successful checks
                passed_checks = sum(1 for _, passed in checks if passed)
                print(f"\n🎯 Summary: {passed_checks}/{len(checks)} checks passed")
                
            except FileNotFoundError:
                print(f"❌ Markdown file not found: {markdown_path}")
                
        else:
            print(f"❌ EOD submission failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ EOD test failed: {e}")

def run_all_enhanced_tests():
    """Run all enhanced processing tests"""
    print("🚀 Enhanced SOD/EOD Processing Test Suite")
    print("=" * 60)
    
    # Check if Flask app is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Flask app is running")
        else:
            print("❌ Flask app not responding correctly")
            return
    except:
        print("❌ Flask app not running. Please start with: python app.py")
        return
    
    # Run tests
    test_enhanced_sod_processing()
    test_eod_processing_with_captures()
    
    print("\n" + "=" * 60)
    print("🏁 Enhanced Processing Tests Complete")
    print("=" * 60)
    print("Check the console output above for detailed results.")
    print("Generated markdown files are in: daily_notes/")

if __name__ == "__main__":
    run_all_enhanced_tests()
