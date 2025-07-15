# database.py
import psycopg2
from psycopg2.extras import RealDictCursor, Json
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def create_tables(self):
        """Create necessary tables"""
        create_sod_table = """
        CREATE TABLE IF NOT EXISTS sod_responses (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            highlight TEXT,
            big_three TEXT,
            grateful_life TEXT,
            grateful_self TEXT,
            excited_for TEXT,
            word_description TEXT,
            needs_me TEXT,
            obstacle_solution TEXT,
            surprise_appreciation TEXT,
            excellence_action TEXT,
            bold_action TEXT,
            coach_advice TEXT,
            big_projects TEXT,
            success_criteria TEXT,
            raw_data JSONB
        );
        """
        
        create_eod_table = """
        CREATE TABLE IF NOT EXISTS eod_responses (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            rating INTEGER,
            summary TEXT,
            story TEXT,
            obstacles TEXT,
            thoughts TEXT,
            improvements TEXT,
            physical_energy INTEGER,
            mental_energy INTEGER,
            emotional_energy INTEGER,
            spiritual_energy INTEGER,
            re_energize_activities TEXT,
            raw_data JSONB
        );
        """
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(create_sod_table)
                cursor.execute(create_eod_table)
                self.connection.commit()
                logger.info("Tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            self.connection.rollback()
            raise
    
    def insert_sod_response(self, date, form_data):
        """Insert SOD form response"""
        insert_query = """
        INSERT INTO sod_responses (
            date, highlight, big_three, grateful_life, grateful_self,
            excited_for, word_description, needs_me, obstacle_solution,
            surprise_appreciation, excellence_action, bold_action,
            coach_advice, big_projects, success_criteria, raw_data
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_query, (
                    date,
                    form_data.get("What am I looking forward to the most today?"),
                    form_data.get("Today's Big 3"),
                    form_data.get("3 things I'm grateful for in my life:"),
                    form_data.get("3 things I'm grateful about myself:"),
                    form_data.get("I'm excited today for:"),
                    form_data.get("One word to describe the person I want to be today would be __ because:"),
                    form_data.get("Someone who needs me on my a-game today is:"),
                    form_data.get("What's a potential obstacle/stressful situation for today and how would my best self deal with it?"),
                    form_data.get("Someone I could surprise with a note, gift, or sign of appreciation is:"),
                    form_data.get("One action I could take today to demonstrate excellence or real value is:"),
                    form_data.get("One bold action I could take today is:"),
                    form_data.get("An overseeing high performance coach would tell me today that:"),
                    form_data.get("The big projects I should keep in mind, even if I don't work on them today, are:"),
                    form_data.get("I know today would be successful if I did or felt this by the end:"),
                    Json(form_data)  # Use psycopg2's Json adapter
                ))
                self.connection.commit()
                logger.info(f"SOD response inserted for date: {date}")
        except Exception as e:
            logger.error(f"Failed to insert SOD response: {e}")
            self.connection.rollback()
            raise
    
    def get_sod_response(self, date):
        """Get SOD response for a specific date"""
        query = "SELECT * FROM sod_responses WHERE date = %s"
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (date,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Failed to get SOD response: {e}")
            raise