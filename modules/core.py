"""Core Module - Shared utilities and dependencies"""

from datetime import datetime, date
from flask import jsonify, request
from database import DatabaseManager
from config import Config
import logging

# Setup logging
logger = logging.getLogger(__name__)

class CoreUtils:
    """Shared utility functions used across modules"""
    
    @staticmethod
    def get_test_date_or_today():
        """Get test date from request args or today's date"""
        test_date_str = request.args.get('test_date')
        if test_date_str:
            return datetime.strptime(test_date_str, '%Y-%m-%d').date()
        return date.today()
    
    @staticmethod
    def validate_json_request():
        """Validate and return JSON data from request"""
        form_data = request.get_json()
        if not form_data:
            return None, jsonify({'error': 'No JSON data received'}), 400
        return form_data, None, None
    
    @staticmethod
    def create_success_response(message, date_obj, **kwargs):
        """Create standardized success response"""
        response = {
            'success': True,
            'message': message,
            'date': date_obj.isoformat(),
            **kwargs
        }
        return jsonify(response), 200
    
    @staticmethod
    def create_error_response(error_message, status_code=500):
        """Create standardized error response"""
        return jsonify({'error': error_message}), status_code
    
    @staticmethod
    def log_processing_start(form_type, date_obj):
        """Log the start of form processing"""
        logger.info(f"Starting {form_type} processing for {date_obj}")
        print(f"🔄 Processing {form_type} form for {date_obj}")
    
    @staticmethod
    def log_processing_success(form_type, date_obj):
        """Log successful form processing"""
        logger.info(f"{form_type} processing completed successfully for {date_obj}")
        print(f"✅ {form_type} processing completed for {date_obj}")
    
    @staticmethod
    def log_processing_error(form_type, date_obj, error):
        """Log form processing errors"""
        logger.error(f"{form_type} processing failed for {date_obj}: {error}")
        print(f"❌ {form_type} processing failed for {date_obj}: {error}")

class DatabaseContext:
    """Database context manager for consistent DB operations"""
    
    def __init__(self):
        self.db_manager = None
    
    def __enter__(self):
        self.db_manager = DatabaseManager()
        return self.db_manager
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db_manager:
            # DatabaseManager handles its own connection management
            pass
        if exc_type is not None:
            logger.error(f"Database operation failed: {exc_val}")
            return False
        return True

class ValidationResult:
    """Standardized validation result object"""
    
    def __init__(self, is_valid, message, data=None):
        self.is_valid = is_valid
        self.message = message
        self.data = data
    
    def to_dict(self):
        return {
            'valid': self.is_valid,
            'message': self.message,
            'data': self.data
        }

def handle_exceptions(func):
    """Decorator for consistent exception handling in endpoints"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Unhandled exception in {func.__name__}: {e}", exc_info=True)
            return CoreUtils.create_error_response('Internal server error')
    return wrapper

# Common imports that modules will need
__all__ = [
    'CoreUtils', 
    'DatabaseContext', 
    'ValidationResult', 
    'handle_exceptions',
    'logger'
]