#!/usr/bin/env python3
"""
Test script for EOD webhook functionality
"""
import requests
<<<<<<< HEAD
=======
import json
>>>>>>> origin/main
from datetime import datetime, date

# Configuration
BASE_URL = "http://localhost:5000"  # Change to your ngrok URL when testing with Google Forms

def test_eod_webhook():
    """Test EOD webhook with sample data"""
    
    # Sample EOD data - adjust fields based on your actual form
    sample_eod_data = {
        "day_rating": "8/10",
        "accomplishments": "- Completed the EOD webhook implementation\n- Fixed database schema issues\n- Tested markdown generation",
        "challenges": "- Had some issues with JSON serialization\n- Took longer than expected to debug timestamp formatting",
        "learnings": "- Learned about PostgreSQL UPSERT functionality\n- Better understanding of Flask error handling",
        "gratitude": "- Grateful for a productive day\n- Appreciate the time to work on this project",
        "tomorrow_prep": "- Review and test Google Drive integration\n- Prepare for Step 5 implementation",
        "reflection": "Good day overall. Made solid progress on the automation hub. The EOD integration is working well.",
        "energy_level_evening": "7/10",
        "stress_level": "3/10",
        "exercise_completed": "Yes - 30 min walk",
        "screen_time": "6 hours",
        "timestamp": datetime.now().isoformat()
    }
    
    # Test EOD webhook
    print("Testing EOD webhook...")
    print(f"Sending data to: {BASE_URL}/webhook/eod")
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/eod",
            json=sample_eod_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ EOD webhook test passed!")
            return True
        else:
            print("❌ EOD webhook test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing EOD webhook: {e}")
        return False

def test_sod_webhook():
    """Test SOD webhook with sample data"""
    
    # Sample SOD data - adjust fields based on your actual form
    sample_sod_data = {
        "sleep_quality": "Good",
        "sleep_hours": "7.5",
        "energy_level": "8/10",
        "mood": "Positive",
        "priorities": "1. Implement EOD webhook\n2. Test full workflow\n3. Update documentation",
        "goals": "- Complete Step 6 of the automation hub\n- Test both SOD and EOD workflows\n- Prepare for Google Drive integration",
        "notes": "Feeling good about today's progress. Ready to tackle the EOD implementation.",
        "weather_preference": "Sunny",
        "exercise_plan": "Evening walk",
        "timestamp": datetime.now().isoformat()
    }
    
    # Test SOD webhook
    print("Testing SOD webhook...")
    print(f"Sending data to: {BASE_URL}/webhook/sod")
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/sod",
            json=sample_sod_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ SOD webhook test passed!")
            return True
        else:
            print("❌ SOD webhook test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing SOD webhook: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\nTesting API endpoints...")
    
    today = date.today().strftime('%Y-%m-%d')
    
    # Test get daily entry
    try:
        response = requests.get(f"{BASE_URL}/api/daily/{today}")
        print(f"GET /api/daily/{today}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Has SOD: {data['sod_data'] is not None}")
            print(f"  Has EOD: {data['eod_data'] is not None}")
        print()
    except Exception as e:
        print(f"Error testing daily endpoint: {e}")
    
    # Test recent entries
    try:
        response = requests.get(f"{BASE_URL}/api/recent?days=3")
        print(f"GET /api/recent: {response.status_code}")
        if response.status_code == 200:
            entries = response.json()
            print(f"  Found {len(entries)} recent entries")
            for entry in entries:
                print(f"    {entry['date']}: SOD={entry['has_sod']}, EOD={entry['has_eod']}")
        print()
    except Exception as e:
        print(f"Error testing recent endpoint: {e}")
    
    # Test health check
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"GET /health: {response.status_code}")
        if response.status_code == 200:
            health = response.json()
            print(f"  Database: {health['database']}")
            print(f"  Testing Mode: {health['testing_mode']}")
        print()
    except Exception as e:
        print(f"Error testing health endpoint: {e}")

def test_missing_data_scenarios():
    """Test scenarios with missing SOD or EOD data"""
    print("\nTesting missing data scenarios...")
    
    # This would require manipulating the database or testing on different dates
    # For now, just document the expected behavior
    print("Expected behaviors:")
    print("- SOD submitted without previous EOD: Warning logged, processing continues")
    print("- EOD submitted without current SOD: Warning logged, processing continues")
    print("- Missing SOD in markdown: Shows '❌ SOD form not completed'")
    print("- Missing EOD in markdown: Shows '⏳ EOD form not completed'")
    print("- Multiple submissions: Latest submission overwrites previous data")

def run_full_test():
    """Run complete test suite"""
    print("🚀 Starting full EOD webhook test suite...")
    print("=" * 50)
    
    # Test health check first
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server not responding. Make sure Flask app is running.")
            return
        else:
            health = response.json()
            print(f"✅ Server healthy - Database: {health['database']}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure Flask app is running on port 5000")
        return
    
    print()
    
    # Run tests
    sod_success = test_sod_webhook()
    print()
    eod_success = test_eod_webhook()
    print()
    test_api_endpoints()
    test_missing_data_scenarios()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"SOD Webhook: {'✅ PASS' if sod_success else '❌ FAIL'}")
    print(f"EOD Webhook: {'✅ PASS' if eod_success else '❌ FAIL'}")
    
    if sod_success and eod_success:
        print("\n🎉 All tests passed! Check the daily_notes folder for generated markdown.")
        print(f"Look for: daily_notes/{date.today().strftime('%Y-%m-%d')}.md")
    else:
        print("\n⚠️  Some tests failed. Check the Flask app logs for details.")

if __name__ == "__main__":
    run_full_test()