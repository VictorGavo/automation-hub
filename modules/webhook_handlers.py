"""Webhook Handlers Module - Clean webhook routing and processing"""

from datetime import datetime
from flask import request, jsonify
from .core import CoreUtils, DatabaseContext, handle_exceptions, logger
from .daily_books import DailyBooksManager
from .daily_capture import DailyCaptureManager

class WebhookHandlers:
    """Centralized webhook handling with clean separation of concerns"""
    
    def __init__(self):
        self.daily_books = DailyBooksManager()
        self.daily_capture = DailyCaptureManager()
    
    @handle_exceptions
    def handle_sod_webhook(self):
        """Handle SOD (Start of Day) form submissions"""
        # Validate request
        form_data, error_response, status_code = CoreUtils.validate_json_request()
        if error_response:
            return error_response, status_code
        
        # Get current date
        current_date = CoreUtils.get_test_date_or_today()
        
        # Process SOD form data
        books_result = self.daily_books.process_sod(form_data, current_date)
        
        if not books_result.is_valid:
            return CoreUtils.create_error_response(books_result.message)
        
        # Get updated daily entry for capture processing
        entry_result = self.daily_books.get_daily_entry(current_date)
        if not entry_result.is_valid:
            logger.error(f"Failed to retrieve daily entry after SOD processing: {entry_result.message}")
            return CoreUtils.create_error_response("SOD stored but failed to retrieve entry for processing")
        
        daily_entry = entry_result.data
        
        # Process capture workflow (Notion update and markdown generation)
        capture_results = self.daily_capture.process_sod_workflow(form_data, daily_entry)
        
        notion_result = capture_results['notion_result']
        markdown_result = capture_results['markdown_result']
        
        # Build response
        response_data = {
            **books_result.data,
            'notion_update': notion_result.is_valid if notion_result else False,
            'notion_sections': notion_result.data.get('updated_sections', []) if notion_result and notion_result.is_valid else [],
            'template_generated': markdown_result.is_valid if markdown_result else False,
            'template_path': markdown_result.data.get('path') if markdown_result and markdown_result.is_valid else None
        }
        
        # Add any warnings
        if books_result.data and books_result.data.get('previous_day_warning'):
            response_data['warnings'] = [books_result.data['previous_day_warning']]
        
        if notion_result and not notion_result.is_valid:
            response_data.setdefault('warnings', []).append(f"Notion update failed: {notion_result.message}")
        
        if markdown_result and not markdown_result.is_valid:
            response_data.setdefault('warnings', []).append(f"Template generation failed: {markdown_result.message}")
        
        return CoreUtils.create_success_response(
            'SOD data processed successfully',
            current_date,
            **response_data
        )
    
    @handle_exceptions
    def handle_eod_webhook(self):
        """Handle EOD (End of Day) form submissions"""
        # Validate request
        form_data, error_response, status_code = CoreUtils.validate_json_request()
        if error_response:
            return error_response, status_code
        
        # Get current date
        current_date = CoreUtils.get_test_date_or_today()
        
        # Process EOD form data
        books_result = self.daily_books.process_eod(form_data, current_date)
        
        if not books_result.is_valid:
            return CoreUtils.create_error_response(books_result.message)
        
        # Get updated daily entry for capture processing
        entry_result = self.daily_books.get_daily_entry(current_date)
        if not entry_result.is_valid:
            logger.error(f"Failed to retrieve daily entry after EOD processing: {entry_result.message}")
            return CoreUtils.create_error_response("EOD stored but failed to retrieve entry for processing")
        
        daily_entry = entry_result.data
        
        # Process final workflow (captures and final markdown)
        capture_result = self.daily_capture.process_eod_workflow(daily_entry)
        
        # Build response
        response_data = {
            **books_result.data,
            'template_generated': capture_result.is_valid if capture_result else False,
            'template_path': capture_result.data.get('path') if capture_result and capture_result.is_valid else None,
            'notion_captures_processed': False,
            'captures_imported': 0
        }
        
        # Add Notion capture details if available
        if capture_result and capture_result.data:
            capture_data = capture_result.data
            if capture_data.get('notion_captures'):
                notion_captures = capture_data['notion_captures']
                response_data.update({
                    'notion_captures_processed': notion_captures.get('captures_processed', False),
                    'captures_imported': notion_captures.get('sections_imported', 0),
                    'blocks_cleared': notion_captures.get('blocks_cleared', 0)
                })
        
        # Add any warnings
        if books_result.data and books_result.data.get('sod_warning'):
            response_data['warnings'] = [books_result.data['sod_warning']]
        
        if capture_result and not capture_result.is_valid:
            response_data.setdefault('warnings', []).append(f"Capture processing failed: {capture_result.message}")
        
        return CoreUtils.create_success_response(
            'EOD data processed successfully',
            current_date,
            **response_data
        )

class APIHandlers:
    """Centralized API endpoint handling"""
    
    def __init__(self):
        self.daily_books = DailyBooksManager()
        self.daily_capture = DailyCaptureManager()
    
    @handle_exceptions
    def get_daily_entry(self, date_str):
        """Get daily entry for a specific date"""
        try:
            # Parse date string
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return CoreUtils.create_error_response('Invalid date format. Use YYYY-MM-DD', 400)
        
        # Get entry from database
        result = self.daily_books.get_daily_entry(entry_date)
        
        if not result.is_valid:
            return CoreUtils.create_error_response(result.message, 500)
        
        entry = result.data
        if not entry:
            return CoreUtils.create_error_response('No entry found for this date', 404)
        
        # Convert datetime objects to ISO format for JSON serialization
        response = {
            'id': entry['id'],
            'date': entry['date'].isoformat(),
            'sod_data': entry['sod_data'],
            'sod_timestamp': entry['sod_timestamp'].isoformat() if entry['sod_timestamp'] else None,
            'eod_data': entry['eod_data'],
            'eod_timestamp': entry['eod_timestamp'].isoformat() if entry['eod_timestamp'] else None,
            'created_at': entry['created_at'].isoformat(),
            'updated_at': entry['updated_at'].isoformat()
        }
        
        return jsonify(response), 200
    
    @handle_exceptions
    def get_recent_entries(self):
        """Get recent entries for monitoring"""
        days = request.args.get('days', 7, type=int)
        
        result = self.daily_books.get_recent_entries(days)
        
        if not result.is_valid:
            return CoreUtils.create_error_response(result.message, 500)
        
        entries = result.data
        
        # Convert to JSON-serializable format
        response = []
        for entry in entries:
            response.append({
                'date': entry['date'].isoformat(),
                'has_sod': entry['has_sod'],
                'has_eod': entry['has_eod'],
                'sod_timestamp': entry['sod_timestamp'].isoformat() if entry['sod_timestamp'] else None,
                'eod_timestamp': entry['eod_timestamp'].isoformat() if entry['eod_timestamp'] else None
            })
        
        return jsonify(response), 200
    
    @handle_exceptions
    def regenerate_markdown(self, date_str):
        """Regenerate markdown file for a specific date"""
        try:
            # Parse date string
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return CoreUtils.create_error_response('Invalid date format. Use YYYY-MM-DD', 400)
        
        # Get entry from database
        entry_result = self.daily_books.get_daily_entry(entry_date)
        
        if not entry_result.is_valid:
            return CoreUtils.create_error_response(entry_result.message, 500)
        
        entry = entry_result.data
        if not entry:
            return CoreUtils.create_error_response('No entry found for this date', 404)
        
        # Regenerate markdown
        result = self.daily_capture.markdown_manager.regenerate_template(entry)
        
        if result.is_valid:
            return CoreUtils.create_success_response(
                f'Markdown regenerated for {date_str}',
                entry_date,
                template_path=result.data.get('path')
            )
        else:
            return CoreUtils.create_error_response(result.message, 500)
    
    @handle_exceptions
    def update_notion_template(self):
        """Manually update Notion Daily Capture template with SOD data"""
        from config import Config
        
        if not Config.NOTION_ENABLED:
            return CoreUtils.create_error_response('Notion integration not enabled', 400)
        
        # Get date parameter
        date_str = request.args.get('date')
        if date_str:
            try:
                entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return CoreUtils.create_error_response('Invalid date format. Use YYYY-MM-DD', 400)
        else:
            entry_date = CoreUtils.get_test_date_or_today()
        
        # Get daily entry
        entry_result = self.daily_books.get_daily_entry(entry_date)
        
        if not entry_result.is_valid:
            return CoreUtils.create_error_response(entry_result.message, 500)
        
        entry = entry_result.data
        if not entry or not entry['sod_data']:
            return CoreUtils.create_error_response('No SOD data found for this date', 404)
        
        # Update Notion template
        result = self.daily_capture.manual_notion_update(entry['sod_data'], entry_date)
        
        if result.is_valid:
            return CoreUtils.create_success_response(
                'Notion template updated successfully',
                entry_date,
                updated_sections=result.data.get('updated_sections', []),
                blocks_added=result.data.get('blocks_added', 0)
            )
        else:
            return CoreUtils.create_error_response(result.message, 500)
    
    @handle_exceptions
    def test_notion_connection(self):
        """Test Notion API connection"""
        from config import Config
        
        if not Config.NOTION_ENABLED:
            return CoreUtils.create_error_response('Notion integration not enabled', 400)
        
        result = self.daily_capture.test_notion_connection()
        
        if result.is_valid:
            return jsonify(result.data), 200
        else:
            return CoreUtils.create_error_response(result.message, 500)

# Factory function to create handlers
def create_webhook_handlers():
    """Factory function to create webhook handlers"""
    return WebhookHandlers()

def create_api_handlers():
    """Factory function to create API handlers"""
    return APIHandlers()

# Export classes and factory functions
__all__ = ['WebhookHandlers', 'APIHandlers', 'create_webhook_handlers', 'create_api_handlers']