#!/usr/bin/env python3
"""
Setup script for test environment and database utilities
"""
import os
import sys
from database import DatabaseManager
from config import Config

def create_test_database():
    """Create test database if it doesn't exist"""
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    try:
        # Connect to postgres database to create test database
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if test database exists
        cursor.execute("""
            SELECT 1 FROM pg_database WHERE datname = %s
        """, (Config.DB_NAME,))
        
        if not cursor.fetchone():
            cursor.execute(f'CREATE DATABASE "{Config.DB_NAME}"')
            print(f"✅ Created test database: {Config.DB_NAME}")
        else:
            print(f"ℹ️  Test database already exists: {Config.DB_NAME}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating test database: {e}")
        return False
    
    return True

def setup_test_environment():
    """Setup test environment"""
    print("Setting up test environment...")
    print(f"Database: {Config.DB_NAME}")
    print(f"Testing Mode: {Config.TESTING}")
    
    # Create test database if needed
    if Config.TESTING:
        if not create_test_database():
            return False
    
    # Initialize database manager and create tables
    try:
        db_manager = DatabaseManager()
        db_manager.create_tables()
        print("✅ Database tables created/verified")
        
        # Test connection
        recent = db_manager.get_recent_entries(1)
        print(f"✅ Database connection verified - {len(recent)} recent entries found")
        
        db_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def clear_test_data():
    """Clear all data from test database (use with caution!)"""
    if not Config.TESTING:
        print("❌ This function only works in testing mode!")
        return False
    
    response = input(f"Are you sure you want to clear all data from {Config.DB_NAME}? (yes/no): ")
    if response.lower() != 'yes':
        print("Operation cancelled")
        return False
    
    try:
        db_manager = DatabaseManager()
        cursor = db_manager.connection.cursor()
        
        cursor.execute("DELETE FROM daily_entries")
        db_manager.connection.commit()
        
        cursor.close()
        db_manager.close()
        
        print("✅ Test data cleared")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing test data: {e}")
        return False

def show_database_status():
    """Show current database status"""
    print("Database Status:")
    print(f"  Database Name: {Config.DB_NAME}")
    print(f"  Testing Mode: {Config.TESTING}")
    print(f"  Host: {Config.DB_HOST}:{Config.DB_PORT}")
    print()
    
    try:
        db_manager = DatabaseManager()
        recent = db_manager.get_recent_entries(7)
        
        print(f"Recent entries (last 7 days):")
        if recent:
            for entry in recent:
                sod_status = "✅" if entry['has_sod'] else "❌"
                eod_status = "✅" if entry['has_eod'] else "❌"
                print(f"  {entry['date']}: SOD {sod_status} | EOD {eod_status}")
        else:
            print("  No entries found")
        
        db_manager.close()
        
    except Exception as e:
        print(f"❌ Error checking database status: {e}")

def switch_to_testing():
    """Switch to testing mode"""
    print("To switch to testing mode:")
    print("1. Set environment variable: export TESTING=true")
    print("2. Or update config.py directly")
    print("3. Restart your Flask app")
    print()
    print("Current testing mode:", Config.TESTING)

def switch_to_production():
    """Switch to production mode"""
    print("To switch to production mode:")
    print("1. Set environment variable: export TESTING=false")
    print("2. Or update config.py directly")
    print("3. Restart your Flask app")
    print()
    print("Current testing mode:", Config.TESTING)

def main():
    """Main menu for setup utilities"""
    while True:
        print("\n" + "=" * 50)
        print("Automation Hub - Database Setup Utilities")
        print("=" * 50)
        print("1. Setup test environment")
        print("2. Show database status")
        print("3. Clear test data (testing mode only)")
        print("4. Switch to testing mode (instructions)")
        print("5. Switch to production mode (instructions)")
        print("6. Exit")
        
        choice = input("\nSelect an option (1-6): ").strip()
        
        if choice == "1":
            setup_test_environment()
        elif choice == "2":
            show_database_status()
        elif choice == "3":
            clear_test_data()
        elif choice == "4":
            switch_to_testing()
        elif choice == "5":
            switch_to_production()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    # Print current config
    print("Current Configuration:")
    Config.print_config()
    print()
    
    # Check if specific action requested via command line
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        if action == "setup":
            setup_test_environment()
        elif action == "status":
            show_database_status()
        elif action == "clear":
            clear_test_data()
        else:
            print(f"Unknown action: {action}")
            print("Available actions: setup, status, clear")
    else:
        main()