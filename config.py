import os
from datetime import datetime

class Config:
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'polymath88')
    DB_PORT = os.getenv('DB_PORT', '5433')
    
    # Testing flag - set to True for test database
    TESTING = os.getenv('TESTING', 'False').lower() == 'true'
    
    # Database names
    DB_NAME = 'automation_hub_test' if TESTING else 'automation_hub'
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Webhook configuration
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', None)  # Optional webhook validation
    
    # Timezone configuration
    TIMEZONE = os.getenv('TIMEZONE', 'America/Los_Angeles')
    
    @classmethod
    def get_db_url(cls):
        """Get the database URL based on testing flag"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def print_config(cls):
        """Print current configuration (useful for debugging)"""
        print(f"Database: {cls.DB_NAME}")
        print(f"Testing Mode: {cls.TESTING}")
        print(f"Debug Mode: {cls.DEBUG}")
        print(f"Timezone: {cls.TIMEZONE}")