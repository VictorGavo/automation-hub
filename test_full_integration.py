#!/usr/bin/env python3
"""
Test script for full SOD/EOD integration with Notion.
Tests the complete workflow from form submission to markdown generation.
"""

import requests
from datetime import datetime, date

# Configuration
BASE_URL = "http://localhost:5000"  # Adjust if your Flask app runs on different port
TEST_DATE = "2025-07-21"  # Use tomorrow's date for testing

def test_sod_submission():
    """Test SOD form submission and Notion template update."""
    print("🌅 Testing SOD Submission...")
    print("-" * 50)
    
    # Sample SOD data
    sod_data = {
        "What am I looking forward to the most today?": "Testing the complete SOD/EOD integration with Notion",
        "Today's Big 3": "1. Complete SOD integration testing\n2. Verify Notion template updates\n3. Test EOD capture processing",
        "What would make today successful?": "All integration tests pass and workflows work smoothly",
        "3 things I'm grateful for in my life:": "Technology that enables automation\nTime to build useful systems\nA supportive development community",
        "3 things I'm grateful about myself:": "Persistence in solving complex problems\nWillingness to learn new technologies\nAttention to detail in testing",
        "I'm excited today for:": "Seeing all the pieces work together seamlessly",
        "One word to describe the person I want to be today would be __ because:": "Focused - because this integration requires attention to detail",
        "Someone who needs me on my a-game today is:": "Future me who will use this automation system",
        "What's a potential obstacle/stressful situation for today and how would my best self deal with it?": "API errors - handle gracefully with proper error messages and fallbacks",
        "Someone I could surprise with a note, gift, or sign of appreciation is:": "The open source community that builds the tools I use",
        "One action I could take today to demonstrate excellence or real value is:": "Create thorough tests that ensure reliability",
        "One bold action I could take today is:": "Complete the full integration in one testing session",
        "An overseeing high performance coach would tell me today that:": "Focus on one test at a time and celebrate small wins",
        "The big projects I should keep in mind, even if I don't work on them today, are:": "Goal sync from Obsidian, calendar integration, mobile optimization",
        "I know today would be successful if I did or felt this by the end:": "All tests pass and the system works end-to-end"
    }
    
    try:
        # Submit SOD data
        url = f"{BASE_URL}/webhook/sod?test_date={TEST_DATE}"
        response = requests.post(url, json=sod_data, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SOD submission successful")
            print(f"   Message: {result.get('message', 'No message')}")
            print(f"   Date: {result.get('date', 'Unknown')}")
            print(f"   Notion update: {'✅' if result.get('notion_update') else '❌'}")
            
            if result.get('previous_day_warning'):
                print(f"   ⚠️ Warning: {result['previous_day_warning']}")
            
            return True, result
        else:
            print(f"❌ SOD submission failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Is your Flask app running on localhost:5000?")
        return False, None
    except Exception as e:
        print(f"❌ Error during SOD submission: {e}")
        return False, None

def test_notion_template_state():
    """Check the current state of the Notion template after SOD."""
    print("\n🔍 Checking Notion Template State...")
    print("-" * 50)
    
    try:
        # Test Notion connection
        url = f"{BASE_URL}/api/notion/test"
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Notion connection successful")
                print(f"   Page: {result.get('page_title', 'Unknown')}")
                
                # Note: We can't directly read the template state via API
                # but we can verify the connection works
                return True
            else:
                print(f"❌ Notion connection failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Failed to test Notion connection: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Notion state: {e}")
        return False

def add_test_captures_to_notion():
    """
    Instructions for manually adding test captures to Notion.
    This step requires manual action since we don't have a 'write content' API method.
    """
    print("\n📝 Manual Step Required...")
    print("-" * 50)
    print("Please add the following test content to your Notion Daily Capture page:")
    print()
    print("💭 Quick Capture")
    print("* Integration test capture #1")
    print("* This should appear in the daily note")
    print("* Testing nested items:")
    print("  * Nested item A")
    print("  * Nested item B")
    print("* Final test capture item")
    print()
    print("Press Enter when you've added this content to Notion...")
    input()

def test_eod_submission():
    """Test EOD form submission and Notion capture processing."""
    print("\n🌙 Testing EOD Submission...")
    print("-" * 50)
    
    # Sample EOD data
    eod_data = {
        "Rating": "9",
        "Summary": "Excellent day testing the complete integration workflow. All major components working smoothly.",
        "Story": "The moment when I saw the Notion captures seamlessly integrate into the daily markdown file was incredibly satisfying.",
        "Accomplishments": "Successfully tested SOD integration\nVerified Notion template updates\nProcessed daily captures correctly\nGenerated complete markdown files",
        "Obstacles": "Minor API timing issues that were resolved with proper error handling",
        "Physical": "8",
        "Mental": "9", 
        "Emotional": "8",
        "Spiritual": "7",
        "What did you do to re-energize? How did it go?": "Took short breaks between test phases, very effective for maintaining focus",
        "What can I do tomorrow to be 1% better?": "Add more comprehensive error handling and user feedback messages"
    }
    
    try:
        # Submit EOD data
        url = f"{BASE_URL}/webhook/eod?test_date={TEST_DATE}"
        response = requests.post(url, json=eod_data, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ EOD submission successful")
            print(f"   Message: {result.get('message', 'No message')}")
            print(f"   Date: {result.get('date', 'Unknown')}")
            print(f"   Markdown generated: {'✅' if result.get('markdown_generated') else '❌'}")
            print(f"   Notion captures processed: {'✅' if result.get('notion_captures_processed') else '❌'}")
            
            if result.get('sod_warning'):
                print(f"   ⚠️ Warning: {result['sod_warning']}")
            
            return True, result
        else:
            print(f"❌ EOD submission failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error during EOD submission: {e}")
        return False, None

def verify_generated_markdown():
    """Check the generated markdown file for correct integration."""
    print("\n📄 Verifying Generated Markdown...")
    print("-" * 50)
    
    try:
        # Get daily entry via API
        url = f"{BASE_URL}/api/daily/{TEST_DATE}"
        response = requests.get(url)
        
        if response.status_code == 200:
            entry = response.json()
            print("✅ Daily entry retrieved from database")
            print(f"   Has SOD data: {'✅' if entry.get('sod_data') else '❌'}")
            print(f"   Has EOD data: {'✅' if entry.get('eod_data') else '❌'}")
            
            # Check if markdown file exists locally
            import os
            markdown_path = f"daily_notes/{TEST_DATE}.md"
            
            if os.path.exists(markdown_path):
                print(f"✅ Markdown file exists: {markdown_path}")
                
                # Read and analyze the content
                with open(markdown_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for key sections
                checks = {
                    "SOD Big 3 populated": "Complete SOD integration testing" in content,
                    "SOD gratitude populated": "Technology that enables automation" in content,
                    "EOD rating in frontmatter": "Rating: 9" in content,
                    "EOD summary in frontmatter": "Excellent day testing" in content,
                    "Notion captures integrated": "#### From Daily Capture" in content or "💭 Quick Capture" in content,
                    "Test capture content": "Integration test capture #1" in content
                }
                
                print("\n🔍 Content Analysis:")
                for check, passed in checks.items():
                    status = "✅" if passed else "❌"
                    print(f"   {status} {check}")
                
                # Show preview of captured content
                if "#### From Daily Capture" in content or "💭 Quick Capture" in content:
                    lines = content.split('\n')
                    capture_start = None
                    for i, line in enumerate(lines):
                        if "#### From Daily Capture" in line or "#### 💭 Quick Capture" in line:
                            capture_start = i
                            break
                    
                    if capture_start:
                        print(f"\n📝 Captured Content Preview:")
                        preview_end = min(capture_start + 8, len(lines))
                        for line in lines[capture_start:preview_end]:
                            print(f"   {line}")
                
                return all(checks.values())
            else:
                print(f"❌ Markdown file not found: {markdown_path}")
                return False
        else:
            print(f"❌ Failed to retrieve daily entry: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying markdown: {e}")
        return False

def test_notion_cleanup():
    """Verify that Notion page was cleaned and rebuilt."""
    print("\n🧹 Testing Notion Cleanup and Rebuild...")
    print("-" * 50)
    
    print("Please check your Notion Daily Capture page and verify:")
    print("✅ Previous Quick Capture content has been cleared")
    print("✅ Big 3 section shows today's goals from SOD")
    print("✅ Success Criteria section shows today's criteria from SOD")
    print("✅ Current Goals section is preserved")
    print("✅ Quick Capture section is ready for new entries")
    print()
    
    response = input("Does the Notion page look correct? (y/n): ").lower().strip()
    return response in ['y', 'yes']

def run_full_integration_test():
    """Run the complete integration test suite."""
    print("🧪 Full SOD/EOD Integration Test")
    print("=" * 60)
    print(f"Test Date: {TEST_DATE}")
    print(f"Flask App: {BASE_URL}")
    print()
    
    # Check if Flask app is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Flask app health check failed")
            return False
    except:
        print("❌ Cannot connect to Flask app. Is it running on localhost:5000?")
        print("   Start it with: python app.py")
        return False
    
    print("✅ Flask app is running")
    print()
    
    # Test sequence
    results = []
    
    # Step 1: SOD Submission
    sod_success, sod_result = test_sod_submission()
    results.append(('SOD Submission', sod_success))
    
    if not sod_success:
        print("\n❌ SOD test failed, stopping test sequence")
        return False
    
    # Step 2: Notion Template State
    notion_state = test_notion_template_state()
    results.append(('Notion Connection', notion_state))
    
    # Step 3: Manual Notion Content Addition
    add_test_captures_to_notion()
    
    # Step 4: EOD Submission
    eod_success, eod_result = test_eod_submission()
    results.append(('EOD Submission', eod_success))
    
    if not eod_success:
        print("\n❌ EOD test failed")
        return False
    
    # Step 5: Verify Generated Markdown
    markdown_success = verify_generated_markdown()
    results.append(('Markdown Generation', markdown_success))
    
    # Step 6: Notion Cleanup Check
    cleanup_success = test_notion_cleanup()
    results.append(('Notion Cleanup', cleanup_success))
    
    # Final Results
    print("\n" + "=" * 60)
    print("🏁 Integration Test Results")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your SOD/EOD/Notion integration is working correctly!")
    else:
        failed_tests = [name for name, success in results if not success]
        print(f"\n⚠️ {len(failed_tests)} test(s) failed: {', '.join(failed_tests)}")
    
    return all_passed

if __name__ == "__main__":
    try:
        run_full_integration_test()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()