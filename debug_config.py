#!/usr/bin/env python3
"""
Debug configuration differences between Flask app and testing utility
"""
import os
import requests
from config import Config

def debug_configuration():
    print("=" * 60)
    print("CONFIGURATION DEBUG")
    print("=" * 60)
    
    # Check environment variables directly
    print("Environment Variables:")
    testing_env = os.getenv('TESTING', 'Not Set')
    print(f"  TESTING = '{testing_env}'")
    print(f"  DB_HOST = '{os.getenv('DB_HOST', 'Not Set')}'")
    print(f"  DB_NAME = '{os.getenv('DB_NAME', 'Not Set')}'")
    print()
    
    # Check Config class interpretation
    print("Config Class Interpretation:")
    print(f"  Config.TESTING = {Config.TESTING}")
    print(f"  Config.DB_NAME = {Config.DB_NAME}")
    print()
    
    # Check what Flask app reports
    print("Flask App Reports:")
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"  Database: {health['database']}")
            print(f"  Testing Mode: {health['testing_mode']}")
        else:
            print(f"  Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print()
    print("=" * 60)
    
    # Recommendations
    if Config.TESTING != testing_env.lower() == 'true':
        print("⚠️  MISMATCH DETECTED!")
        print()
        print("The environment variable and Config class don't match.")
        print("This usually means:")
        print("1. Environment variable was set AFTER starting Flask")
        print("2. Different terminal sessions have different env vars")
        print()
        print("To fix:")
        print("1. Stop Flask app (Ctrl+C)")
        print("2. Set environment: $env:TESTING = 'true'")
        print("3. Restart Flask: python app.py")
        print("4. Run testing again")
    else:
        print("✅ Configuration looks consistent!")

if __name__ == "__main__":
    debug_configuration()