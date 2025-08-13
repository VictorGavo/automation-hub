import psycopg2
import psycopg2.extras
import sqlite3
import os
import json
from datetime import datetime, timedelta
from config import Config

class DatabaseManager:
    def __init__(self):
        self.config = Config()
        self.connection = None
        self.use_sqlite = getattr(self.config, 'USE_SQLITE', False) or \
                        os.getenv('USE_SQLITE', 'False').lower() == 'true'
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL or SQLite database"""
        try:
            if self.use_sqlite:
                print(f"Connecting to SQLite database: {self.config.DB_NAME}")
                self.connection = sqlite3.connect(self.config.DB_NAME)
                self.connection.row_factory = sqlite3.Row  # Makes rows dict-like
                print(f"Connected to SQLite database: {self.config.DB_NAME}")
            else:
                print(f"Connecting to PostgreSQL database: {self.config.DB_NAME}")
                self.connection = psycopg2.connect(
                    host=self.config.DB_HOST,
                    database=self.config.DB_NAME,
                    user=self.config.DB_USER,
                    password=self.config.DB_PASSWORD,
                    port=self.config.DB_PORT
                )
                print(f"Connected to database: {self.config.DB_NAME}")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise e
    
    def get_cursor(self):
        """Get appropriate cursor for database type"""
        if self.use_sqlite:
            return self.connection.cursor()
        else:
            return self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    def create_tables(self):
        """Create the daily_entries table with SOD and EOD support"""
        try:
            cursor = self.get_cursor()
            
            if self.use_sqlite:
                # SQLite table creation
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE UNIQUE NOT NULL,
                        sod_data TEXT,
                        sod_timestamp TIMESTAMP,
                        eod_data TEXT,
                        eod_timestamp TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create index on date for faster queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_daily_entries_date 
                    ON daily_entries(date)
                ''')
            else:
                # PostgreSQL table creation
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_entries (
                        id SERIAL PRIMARY KEY,
                        date DATE UNIQUE NOT NULL,
                        sod_data JSONB,
                        sod_timestamp TIMESTAMP,
                        eod_data JSONB,
                        eod_timestamp TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create index on date for faster queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_daily_entries_date 
                    ON daily_entries(date)
                ''')
                
                # Create trigger to update updated_at timestamp (PostgreSQL only)
                cursor.execute('''
                    CREATE OR REPLACE FUNCTION update_updated_at_column()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.updated_at = CURRENT_TIMESTAMP;
                        RETURN NEW;
                    END;
                    $$ language 'plpgsql';
                ''')
                
                cursor.execute('''
                    DROP TRIGGER IF EXISTS update_daily_entries_updated_at ON daily_entries;
                    CREATE TRIGGER update_daily_entries_updated_at
                        BEFORE UPDATE ON daily_entries
                        FOR EACH ROW
                        EXECUTE FUNCTION update_updated_at_column();
                ''')
            
            self.connection.commit()
            cursor.close()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")
            self.connection.rollback()
            raise
    
    def upsert_sod_data(self, date, sod_data):
        """Insert or update SOD data for a given date"""
        try:
            cursor = self.get_cursor()
            
            if self.use_sqlite:
                # SQLite upsert using INSERT OR REPLACE
                json_data = json.dumps(sod_data) if not isinstance(sod_data, str) else sod_data
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_entries (date, sod_data, sod_timestamp, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (date, json_data, datetime.now(), datetime.now()))
            else:
                # PostgreSQL upsert using ON CONFLICT
                json_data = json.dumps(sod_data) if not isinstance(sod_data, str) else sod_data
                cursor.execute('''
                    INSERT INTO daily_entries (date, sod_data, sod_timestamp)
                    VALUES (%s, %s::jsonb, %s)
                    ON CONFLICT (date) 
                    DO UPDATE SET 
                        sod_data = EXCLUDED.sod_data,
                        sod_timestamp = EXCLUDED.sod_timestamp
                ''', (date, json_data, datetime.now()))
            
            self.connection.commit()
            cursor.close()
            print(f"✅ SOD data saved for {date}")
            return True
        except Exception as e:
            print(f"Error upserting SOD data: {e}")
            self.connection.rollback()
            return False
    
    def upsert_eod_data(self, date, eod_data):
        """Insert or update EOD data for a given date"""
        try:
            cursor = self.get_cursor()
            
            if self.use_sqlite:
                # SQLite upsert using INSERT OR REPLACE
                json_data = json.dumps(eod_data) if not isinstance(eod_data, str) else eod_data
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_entries (date, eod_data, eod_timestamp, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (date, json_data, datetime.now(), datetime.now()))
            else:
                # PostgreSQL upsert using ON CONFLICT
                json_data = json.dumps(eod_data) if not isinstance(eod_data, str) else eod_data
                cursor.execute('''
                    INSERT INTO daily_entries (date, eod_data, eod_timestamp)
                    VALUES (%s, %s::jsonb, %s)
                    ON CONFLICT (date) 
                    DO UPDATE SET 
                        eod_data = EXCLUDED.eod_data,
                        eod_timestamp = EXCLUDED.eod_timestamp
                ''', (date, json_data, datetime.now()))
            
            self.connection.commit()
            cursor.close()
            print(f"✅ EOD data saved for {date}")
            return True
        except Exception as e:
            print(f"Error upserting EOD data: {e}")
            self.connection.rollback()
            return False
    
    def get_daily_entry(self, date):
        """Get complete daily entry for a specific date"""
        try:
            cursor = self.get_cursor()
            
            if self.use_sqlite:
                cursor.execute('''
                    SELECT * FROM daily_entries WHERE date = ?
                ''', (date,))
            else:
                cursor.execute('''
                    SELECT * FROM daily_entries WHERE date = %s
                ''', (date,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                if self.use_sqlite:
                    # Convert SQLite row to dict and parse JSON
                    return {
                        'id': result['id'],
                        'date': result['date'],
                        'sod_data': json.loads(result['sod_data']) if result['sod_data'] else None,
                        'sod_timestamp': result['sod_timestamp'],
                        'eod_data': json.loads(result['eod_data']) if result['eod_data'] else None,
                        'eod_timestamp': result['eod_timestamp'],
                        'created_at': result['created_at'],
                        'updated_at': result['updated_at']
                    }
                else:
                    # PostgreSQL JSONB columns are automatically parsed
                    return {
                        'id': result['id'],
                        'date': result['date'],
                        'sod_data': result['sod_data'],
                        'sod_timestamp': result['sod_timestamp'],
                        'eod_data': result['eod_data'],
                        'eod_timestamp': result['eod_timestamp'],
                        'created_at': result['created_at'],
                        'updated_at': result['updated_at']
                    }
            return None
        except Exception as e:
            print(f"Error getting daily entry: {e}")
            return None
    
    def check_previous_day_completion(self, current_date):
        """Check if previous day's EOD was completed"""
        try:
            previous_date = current_date - timedelta(days=1)
            entry = self.get_daily_entry(previous_date)
            
            if not entry:
                return False, "No entry found for previous day"
            
            if entry['eod_data'] is None:
                return False, "Previous day's EOD not completed"
            
            return True, "Previous day completed"
        except Exception as e:
            print(f"Error checking previous day completion: {e}")
            return False, f"Error checking previous day: {e}"
    
    def check_current_day_sod(self, current_date):
        """Check if current day's SOD was completed"""
        try:
            entry = self.get_daily_entry(current_date)
            
            if not entry or entry['sod_data'] is None:
                return False, "SOD not completed for current day"
            
            return True, "SOD completed"
        except Exception as e:
            print(f"Error checking current day SOD: {e}")
            return False, f"Error checking SOD: {e}"
    
    def get_recent_entries(self, days=7):
        """Get recent entries for debugging/monitoring"""
        try:
            cursor = self.get_cursor()
            
            if self.use_sqlite:
                cursor.execute('''
                    SELECT date, 
                           sod_data IS NOT NULL as has_sod,
                           eod_data IS NOT NULL as has_eod,
                           sod_timestamp,
                           eod_timestamp
                    FROM daily_entries 
                    WHERE date >= ?
                    ORDER BY date DESC
                ''', (datetime.now().date() - timedelta(days=days),))
            else:
                cursor.execute('''
                    SELECT date, 
                           sod_data IS NOT NULL as has_sod,
                           eod_data IS NOT NULL as has_eod,
                           sod_timestamp,
                           eod_timestamp
                    FROM daily_entries 
                    WHERE date >= %s
                    ORDER BY date DESC
                ''', (datetime.now().date() - timedelta(days=days),))
            
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            print(f"Error getting recent entries: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")