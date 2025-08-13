"""Daily Books Module - SOD and EOD form processing logic"""

from .core import CoreUtils, DatabaseContext, ValidationResult, handle_exceptions, logger
from config import Config

class SODProcessor:
    """Handles Start-of-Day form processing logic"""
    
    def __init__(self):
        self.config = Config()
    
    def validate_sod_data(self, form_data, current_date):
        """Validate SOD form data"""
        if not form_data:
            return ValidationResult(False, "No form data provided")
        
        # Basic validation - can be expanded based on requirements
        required_fields = []  # Add required fields if needed
        missing_fields = [field for field in required_fields if field not in form_data]
        
        if missing_fields:
            return ValidationResult(False, f"Missing required fields: {', '.join(missing_fields)}")
        
        return ValidationResult(True, "SOD data is valid", form_data)
    
    def check_workflow_prerequisites(self, db_manager, current_date):
        """Check if previous day's EOD was completed"""
        prev_complete, prev_message = db_manager.check_previous_day_completion(current_date)
        
        if not prev_complete:
            logger.warning(f"Previous day workflow incomplete: {prev_message}")
            return ValidationResult(False, prev_message, {'warning': True})
        
        return ValidationResult(True, "Previous day completed")
    
    def process_sod_submission(self, form_data, current_date):
        """Process SOD form submission"""
        CoreUtils.log_processing_start("SOD", current_date)
        
        # Validate form data
        validation = self.validate_sod_data(form_data, current_date)
        if not validation.is_valid:
            return validation
        
        # Check workflow prerequisites
        with DatabaseContext() as db_manager:
            prerequisite_check = self.check_workflow_prerequisites(db_manager, current_date)
            
            # Store SOD data (continue even if previous day incomplete)
            success = db_manager.upsert_sod_data(current_date, form_data)
            
            if not success:
                return ValidationResult(False, "Failed to store SOD data")
        
        CoreUtils.log_processing_success("SOD", current_date)
        
        result_data = {
            'sod_stored': True,
            'previous_day_warning': prerequisite_check.message if not prerequisite_check.is_valid else None
        }
        
        return ValidationResult(True, "SOD data processed successfully", result_data)

class EODProcessor:
    """Handles End-of-Day form processing logic"""
    
    def __init__(self):
        self.config = Config()
    
    def validate_eod_data(self, form_data, current_date):
        """Validate EOD form data"""
        if not form_data:
            return ValidationResult(False, "No form data provided")
        
        # Basic validation - can be expanded based on requirements
        required_fields = []  # Add required fields if needed
        missing_fields = [field for field in required_fields if field not in form_data]
        
        if missing_fields:
            return ValidationResult(False, f"Missing required fields: {', '.join(missing_fields)}")
        
        return ValidationResult(True, "EOD data is valid", form_data)
    
    def check_workflow_prerequisites(self, db_manager, current_date):
        """Check if current day's SOD was completed"""
        sod_complete, sod_message = db_manager.check_current_day_sod(current_date)
        
        if not sod_complete:
            logger.warning(f"Current day SOD incomplete: {sod_message}")
            return ValidationResult(False, sod_message, {'warning': True})
        
        return ValidationResult(True, "SOD completed")
    
    def process_eod_submission(self, form_data, current_date):
        """Process EOD form submission"""
        CoreUtils.log_processing_start("EOD", current_date)
        
        # Validate form data
        validation = self.validate_eod_data(form_data, current_date)
        if not validation.is_valid:
            return validation
        
        # Check workflow prerequisites
        with DatabaseContext() as db_manager:
            prerequisite_check = self.check_workflow_prerequisites(db_manager, current_date)
            
            # Store EOD data (continue even if SOD incomplete)
            success = db_manager.upsert_eod_data(current_date, form_data)
            
            if not success:
                return ValidationResult(False, "Failed to store EOD data")
        
        CoreUtils.log_processing_success("EOD", current_date)
        
        result_data = {
            'eod_stored': True,
            'sod_warning': prerequisite_check.message if not prerequisite_check.is_valid else None
        }
        
        return ValidationResult(True, "EOD data processed successfully", result_data)

class DailyBooksManager:
    """Main manager class for daily books processing"""
    
    def __init__(self):
        self.sod_processor = SODProcessor()
        self.eod_processor = EODProcessor()
    
    def process_sod(self, form_data, current_date):
        """Process SOD form data and return result"""
        return self.sod_processor.process_sod_submission(form_data, current_date)
    
    def process_eod(self, form_data, current_date):
        """Process EOD form data and return result"""
        return self.eod_processor.process_eod_submission(form_data, current_date)
    
    def get_daily_entry(self, entry_date):
        """Get daily entry for a specific date"""
        try:
            with DatabaseContext() as db_manager:
                entry = db_manager.get_daily_entry(entry_date)
                return ValidationResult(True, "Entry retrieved", entry)
        except Exception as e:
            logger.error(f"Failed to get daily entry for {entry_date}: {e}")
            return ValidationResult(False, f"Failed to retrieve entry: {e}")
    
    def get_recent_entries(self, days=7):
        """Get recent entries for monitoring"""
        try:
            with DatabaseContext() as db_manager:
                entries = db_manager.get_recent_entries(days)
                return ValidationResult(True, "Recent entries retrieved", entries)
        except Exception as e:
            logger.error(f"Failed to get recent entries: {e}")
            return ValidationResult(False, f"Failed to retrieve entries: {e}")

# Export the main class
__all__ = ['DailyBooksManager', 'SODProcessor', 'EODProcessor']