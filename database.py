import psycopg2
import psycopg2.extras
import json
from datetime import datetime, timedelta, date
from config import Config
import sqlite3

class DatabaseManager:
    def __init__(self):
        self.config = Config()
        self.connection = None
        self.db_type = None
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL or SQLite database based on configuration"""
        try:
            # Determine database type based on configuration
            # Use SQLite if password is empty or if explicitly configured for SQLite
            if (not self.config.DB_PASSWORD or 
                self.config.DB_PASSWORD == '' or 
                getattr(self.config, 'USE_SQLITE', False) or
                self.config.TESTING):
                # SQLite
                self.db_type = 'sqlite'
                self.connection = sqlite3.connect(f'{self.config.DB_NAME}.db', check_same_thread=False)
                self.connection.row_factory = sqlite3.Row  # Enable row access by column name
                print(f"Connected to SQLite database: {self.config.DB_NAME}")
            else:
                # PostgreSQL
                self.db_type = 'postgresql'
                self.connection = psycopg2.connect(
                    host=self.config.DB_HOST,
                    database=self.config.DB_NAME,
                    user=self.config.DB_USER,
                    password=self.config.DB_PASSWORD,
                    port=self.config.DB_PORT
                )
                print(f"Connected to PostgreSQL database: {self.config.DB_NAME}")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def create_tables(self):
        """Create the daily_entries table with SOD and EOD support"""
        try:
            cursor = self.connection.cursor()
            
            if self.db_type == 'postgresql':
                # PostgreSQL schema
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
                
                # Create trigger to update updated_at timestamp
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
            else:
                # SQLite schema
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT UNIQUE NOT NULL,
                        sod_data TEXT,
                        sod_timestamp TEXT,
                        eod_data TEXT,
                        eod_timestamp TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create index on date for faster queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_daily_entries_date 
                    ON daily_entries(date)
                ''')
            
            self.connection.commit()
            cursor.close()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")
            self.connection.rollback()
            raise
    
    def _convert_date_for_storage(self, date_obj):
        """Convert date object to appropriate format for storage"""
        if isinstance(date_obj, str):
            return date_obj
        return date_obj.strftime('%Y-%m-%d') if date_obj else None
    
    def _convert_date_from_storage(self, date_str):
        """Convert stored date to date object"""
        if isinstance(date_str, date):
            return date_str
        if isinstance(date_str, str):
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        return date_str
    
    def _convert_datetime_for_storage(self, datetime_obj):
        """Convert datetime object to appropriate format for storage"""
        if isinstance(datetime_obj, str):
            return datetime_obj
        return datetime_obj.isoformat() if datetime_obj else None
    
    def _convert_datetime_from_storage(self, datetime_str):
        """Convert stored datetime to datetime object"""
        if isinstance(datetime_str, datetime):
            return datetime_str
        if isinstance(datetime_str, str):
            try:
                return datetime.fromisoformat(datetime_str)
            except:
                return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        return datetime_str
    
    def _prepare_json_data(self, data):
        """Prepare JSON data for storage"""
        if self.db_type == 'postgresql':
            return json.dumps(data) if not isinstance(data, str) else data
        else:
            return json.dumps(data) if data else None
    
    def _parse_json_data(self, data):
        """Parse JSON data from storage"""
        if not data:
            return None
        if isinstance(data, dict):
            return data
        if isinstance(data, str):
            try:
                return json.loads(data)
            except:
                return None
        return data
    
    def upsert_sod_data(self, date_obj, sod_data):
        """Insert or update SOD data for a given date"""
        try:
            cursor = self.connection.cursor()
            
            date_str = self._convert_date_for_storage(date_obj)
            json_data = self._prepare_json_data(sod_data)
            timestamp_str = self._convert_datetime_for_storage(datetime.now())
            
            if self.db_type == 'postgresql':
                cursor.execute('''
                    INSERT INTO daily_entries (date, sod_data, sod_timestamp)
                    VALUES (%s, %s::jsonb, %s)
                    ON CONFLICT (date) 
                    DO UPDATE SET 
                        sod_data = EXCLUDED.sod_data,
                        sod_timestamp = EXCLUDED.sod_timestamp
                ''', (date_str, json_data, timestamp_str))
            else:
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_entries 
                    (date, sod_data, sod_timestamp, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (date_str, json_data, timestamp_str, timestamp_str))
            
            self.connection.commit()
            cursor.close()
            print(f"✅ SOD data saved for {date_obj}")
            return True
        except Exception as e:
            print(f"Error upserting SOD data: {e}")
            self.connection.rollback()
            return False
    
    def upsert_eod_data(self, date_obj, eod_data):
        """Insert or update EOD data for a given date"""
        try:
            cursor = self.connection.cursor()
            
            date_str = self._convert_date_for_storage(date_obj)
            json_data = self._prepare_json_data(eod_data)
            timestamp_str = self._convert_datetime_for_storage(datetime.now())
            
            if self.db_type == 'postgresql':
                cursor.execute('''
                    INSERT INTO daily_entries (date, eod_data, eod_timestamp)
                    VALUES (%s, %s::jsonb, %s)
                    ON CONFLICT (date) 
                    DO UPDATE SET 
                        eod_data = EXCLUDED.eod_data,
                        eod_timestamp = EXCLUDED.eod_timestamp
                ''', (date_str, json_data, timestamp_str))
            else:
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_entries 
                    (date, eod_data, eod_timestamp, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (date_str, json_data, timestamp_str, timestamp_str))
            
            self.connection.commit()
            cursor.close()
            print(f"✅ EOD data saved for {date_obj}")
            return True
        except Exception as e:
            print(f"Error upserting EOD data: {e}")
            self.connection.rollback()
            return False
    
    def get_daily_entry(self, date_obj):
        """Get complete daily entry for a specific date"""
        try:
            if self.db_type == 'postgresql':
                cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            else:
                cursor = self.connection.cursor()
                
            date_str = self._convert_date_for_storage(date_obj)
            
            if self.db_type == 'sqlite':
                cursor.execute('SELECT * FROM daily_entries WHERE date = ?', (date_str,))
            else:
                cursor.execute('SELECT * FROM daily_entries WHERE date = %s', (date_str,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                if self.db_type == 'sqlite':
                    # Convert SQLite row to dict
                    result_dict = dict(result)
                    return {
                        'id': result_dict['id'],
                        'date': self._convert_date_from_storage(result_dict['date']),
                        'sod_data': self._parse_json_data(result_dict['sod_data']),
                        'sod_timestamp': self._convert_datetime_from_storage(result_dict['sod_timestamp']),
                        'eod_data': self._parse_json_data(result_dict['eod_data']),
                        'eod_timestamp': self._convert_datetime_from_storage(result_dict['eod_timestamp']),
                        'created_at': self._convert_datetime_from_storage(result_dict['created_at']),
                        'updated_at': self._convert_datetime_from_storage(result_dict['updated_at'])
                    }
                else:
                    # PostgreSQL with RealDictCursor
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
        """Get recent entries for debugging/monitoring with fixed detection logic"""
        try:
            cursor = self.connection.cursor()
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            start_date_str = self._convert_date_for_storage(start_date)
            
            if self.db_type == 'sqlite':
                cursor.execute('''
                    SELECT date, 
                        sod_data,
                        eod_data,
                        sod_timestamp,
                        eod_timestamp
                    FROM daily_entries 
                    WHERE date >= ?
                    ORDER BY date DESC
                ''', (start_date_str,))
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
                ''', (start_date_str,))
            
            results = cursor.fetchall()
            cursor.close()
            
            # Convert results to consistent format
            formatted_results = []
            for result in results:
                if self.db_type == 'sqlite':
                    result_dict = dict(result)
                    
                    # Parse JSON data to check if it's actually present
                    sod_data = self._parse_json_data(result_dict['sod_data'])
                    eod_data = self._parse_json_data(result_dict['eod_data'])
                    
                    formatted_results.append({
                        'date': self._convert_date_from_storage(result_dict['date']),
                        'has_sod': bool(sod_data and len(sod_data) > 0),  # Check if data exists and not empty
                        'has_eod': bool(eod_data and len(eod_data) > 0),  # Check if data exists and not empty
                        'sod_timestamp': self._convert_datetime_from_storage(result_dict['sod_timestamp']),
                        'eod_timestamp': self._convert_datetime_from_storage(result_dict['eod_timestamp'])
                    })
                else:
                    formatted_results.append(dict(result))
            
            return formatted_results
        except Exception as e:
            print(f"Error getting recent entries: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")