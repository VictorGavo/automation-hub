# test_db.py
from database import DatabaseManager
from config import DATABASE_CONFIG
import logging

logging.basicConfig(level=logging.INFO)

def test_database():
    db = DatabaseManager(DATABASE_CONFIG)
    try:
        # Test connection
        db.connect()
        print("✅ Database connection successful")
        
        # Create tables
        db.create_tables()
        print("✅ Tables created successfully")
        
        # Test data insertion (using your actual form data)
        test_data = {
            "What am I looking forward to the most today?": "Coding",
            "Today's Big 3": "GHC workday\nGet Evelyn setup\nWork on Automation hub",
            "3 things I'm grateful for in my life:": "My siblings\nMy children\nTechnology",
            "3 things I'm grateful about myself:": "I show up\nI push myself\nI want to better myself"
        }
        
        from datetime import date
        db.insert_sod_response(date.today(), test_data)
        print("✅ Test data inserted successfully")
        
        # Test data retrieval
        result = db.get_sod_response(date.today())
        print(f"✅ Data retrieved: {result['highlight']}")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    test_database()