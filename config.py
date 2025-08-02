import os
from datetime import datetime

class Config:
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'admin')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'rangerskip')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    # Testing flag - set to True for test database
    TESTING = os.getenv('TESTING', 'False').lower() == 'true'    
    
    DB_NAME = 'automation_hub_test' if TESTING else 'automation_hub'
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Google Drive Configuration
    GOOGLE_DRIVE_ENABLED = os.getenv('GOOGLE_DRIVE_ENABLED', 'False').lower() == 'true'
    GOOGLE_DRIVE_METHOD = os.getenv('GOOGLE_DRIVE_METHOD', 'filesystem')  # 'filesystem', 'oauth', or 'service_account'
    
    # File system sync method (recommended for Raspberry Pi)
    GOOGLE_DRIVE_SYNC_PATH = os.getenv('GOOGLE_DRIVE_SYNC_PATH', 'C:/Users/Victo/Google Drive/USV/My Calendar/My Daily Notes')

    # Notion API Configuration
    NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN', None)
    NOTION_DAILY_CAPTURE_PAGE_ID = os.getenv('NOTION_DAILY_CAPTURE_PAGE_ID', None)
    NOTION_ENABLED = os.getenv('NOTION_ENABLED', 'False').lower() == 'true'

    # Obsidian Integration
    OBSIDIAN_VAULT_METHOD = os.getenv('OBSIDIAN_VAULT_METHOD', 'local')  # 'local' or 'google_drive'
    OBSIDIAN_VAULT_LOCAL_PATH = os.getenv('OBSIDIAN_VAULT_PATH', 'C:/Users/Victo/Documents/Growth/Ultimate Starter Vault 2.1')
    OBSIDIAN_VAULT_GDRIVE_FOLDER_ID = os.getenv('OBSIDIAN_VAULT_GDRIVE_FOLDER_ID', None)
    OBSIDIAN_GOALS_ENABLED = os.getenv('OBSIDIAN_GOALS_ENABLED', 'False').lower() == 'true'
    
    # OAuth method (alternative)
    GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'service-account-key.json')
    GOOGLE_DRIVE_ROOT_FOLDER = os.getenv('GOOGLE_DRIVE_ROOT_FOLDER', 'Daily Notes')
    
    # File Paths
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'generated_notes')
    TEMPLATES_DIR = os.getenv('TEMPLATES_DIR', 'templates')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'automation_hub.log')
    
    # API Configuration
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))

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

    @staticmethod
    def get_db_connection_string():
        """Get PostgreSQL connection string."""
        return f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
    
    @staticmethod
    def create_output_dir():
        """Create output directory if it doesn't exist."""
        if not os.path.exists(Config.OUTPUT_DIR):
            os.makedirs(Config.OUTPUT_DIR)
    
    @staticmethod
    def validate_google_drive_config():
        """Validate Google Drive configuration."""
        if not Config.GOOGLE_DRIVE_ENABLED:
            return True
            
        if not os.path.exists(Config.GOOGLE_SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError(f"Google service account file not found: {Config.GOOGLE_SERVICE_ACCOUNT_FILE}")
        
        return True
