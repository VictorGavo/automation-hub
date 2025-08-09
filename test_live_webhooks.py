#!/usr/bin/env python3
"""
Test script for live webhook endpoints on Pi
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://v-v-v.dev"  # Your live Pi domain

def test_health_endpoint():
    """Test the health endpoint"""
    print("🏥 Testing Health Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_sod_webhook():
    """Test SOD webhook with real-like data"""
    print("\n🌅 Testing SOD Webhook")
    print("=" * 50)
    
    # Sample data similar to your Google Forms structure
    test_data = {
        "Today's Big 3": "1. Test live Pi webhooks\n2. Update Google Apps Script\n3. Celebrate success",
        "I'm excited today for:": "Getting the Pi webhooks working perfectly!",
        "What would make today successful?": "All webhook tests pass and forms work end-to-end",
        "3 things I'm grateful for in my life:": "Working Pi setup\nSSL certificates\nAutomated daily workflows",
        "3 things I'm grateful about myself:": "Technical problem solving\nPersistence with setup\nWillingness to learn",
        "One word to describe the person I want to be today would be __ because:": "Accomplished - because we're making real progress",
        "Someone who needs me on my a-game today is:": "Future me who will use this daily workflow",
        "What's a potential obstacle/stressful situation for today and how would my best self deal with it?": "Network connectivity issues - test locally first, then debug step by step",
        "Someone I could surprise with a note, gift, or sign of appreciation is:": "The open source community that makes this possible",
        "One action I could take today to demonstrate excellence or real value is:": "Complete the webhook migration successfully",
        "One bold action I could take today is:": "Go live with the new Pi setup",
        "An overseeing high performance coach would tell me today that:": "Focus on one test at a time and document the process",
        "The big projects I should keep in mind, even if I don't work on them today, are:": "Pi optimization, backup strategies, monitoring setup",
        "I know today would be successful if I did or felt this by the end:": "Forms submit successfully to Pi and generate proper templates"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/sod",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"❌ SOD webhook failed: {e}")
        return False

def test_eod_webhook():
    """Test EOD webhook with real-like data"""
    print("\n🌙 Testing EOD Webhook")
    print("=" * 50)
    
    test_data = {
        "Rating": "9",
        "Summary": "Excellent day setting up Pi webhooks with SSL",
        "Story": "The moment when HTTPS webhooks started working was incredibly satisfying",
        "Accomplishments": "✅ SSL certificates installed\n✅ Nginx configured securely\n✅ Webhooks tested successfully",
        "Obstacles": "Some nginx configuration challenges, but solved with proper syntax",
        "What can I do tomorrow to be 1% better?": "Update Google Apps Script and test with real forms",
        "Physical": "8",
        "Mental": "9", 
        "Emotional": "9",
        "Spiritual": "7",
        "What did you do to re-energize? How did it go?": "Took breaks between configuration steps - very effective"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/eod",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"❌ EOD webhook failed: {e}")
        return False

def main():
    """Run all webhook tests"""
    print("🚀 Live Pi Webhook Testing")
    print("=" * 60)
    print(f"Testing: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {
        'health': test_health_endpoint(),
        'sod': test_sod_webhook(), 
        'eod': test_eod_webhook()
    }
    
    print("\n📊 Test Results Summary")
    print("=" * 50)
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test.upper()} webhook: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall Result: {'🎉 ALL TESTS PASSED' if all_passed else '⚠️  SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🔗 Your webhook URLs are ready:")
        print(f"   SOD: {BASE_URL}/webhook/sod")
        print(f"   EOD: {BASE_URL}/webhook/eod")
        print("\n📝 Next steps:")
        print("   1. Update your Google Apps Script with these URLs")
        print("   2. Test with actual form submissions")
        print("   3. Monitor logs: sudo tail -f /var/log/nginx/webhook.access.log")

if __name__ == "__main__":
    main()
