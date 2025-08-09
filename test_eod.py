# test_eod.py
import requests
import json
from datetime import date

def test_eod_webhook():
    """Test the EOD webhook endpoint with sample data"""
    
    # Sample EOD form data
    sample_eod_data = {
        "How would you rate today? (1-10)": 8,
        "Daily summary": "Had a productive day working on the automation hub project. Made good progress on implementing EOD form processing.",
        "What was a moment today that provided immense emotion, insight, or meaning?": "Successfully implementing the EOD webhook gave me a sense of accomplishment and progress.",
        "What was an obstacle I faced, how did I deal with it, and what can I learn from for the future?": "Had some challenges with the database field mappings, but solved it by carefully reviewing the schema and testing incrementally.",
        "What ideas was I pondering on or were lingering in my mind?": "Thinking about how to make the form field mappings more flexible and robust for future changes.",
        "What can I do tomorrow to be 1% better?": "Start the day with a clear plan and prioritize the most important tasks first.",
        "Physical Energy (1-10)": 7,
        "Mental Energy (1-10)": 8,
        "Emotional Energy (1-10)": 8,
        "Spiritual Energy (1-10)": 6,
        "What did I do to re-energize? How did it go?": "Took a short walk outside and had some coffee. It helped me refocus and feel more energized."
    }
    
    # Test the EOD webhook
    url = "http://localhost:5000/webhook/eod"
    
    try:
        response = requests.post(url, json=sample_eod_data)
        
        if response.status_code == 200:
            print("✅ EOD webhook test successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ EOD webhook test failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Flask app is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error testing EOD webhook: {str(e)}")

def test_eod_retrieval():
    """Test retrieving EOD data for today"""
    
    today_str = date.today().strftime('%Y-%m-%d')
    url = f"http://localhost:5000/eod/{today_str}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            print("✅ EOD data retrieval successful!")
            data = response.json()
            print(f"Found EOD data for {today_str}")
            print(f"Rating: {data['data'].get('rating', 'N/A')}")
            print(f"Summary: {data['data'].get('summary', 'N/A')[:100]}...")
        elif response.status_code == 404:
            print(f"ℹ️ No EOD data found for {today_str}")
        else:
            print(f"❌ EOD retrieval failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Flask app is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error retrieving EOD data: {str(e)}")

if __name__ == "__main__":
    print("Testing EOD Webhook Functionality")
    print("=" * 40)
    
    print("\n1. Testing EOD webhook submission...")
    test_eod_webhook()
    
    print("\n2. Testing EOD data retrieval...")
    test_eod_retrieval()
    
    print("\n✅ EOD testing complete!")
