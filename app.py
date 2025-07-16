from flask import Flask, request, jsonify
from datetime import datetime, date
import json
from database import DatabaseManager
from markdown_generator import MarkdownGenerator
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database manager
db_manager = DatabaseManager()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': Config.DB_NAME,
        'testing_mode': Config.TESTING
    })

@app.route('/webhook/sod', methods=['POST'])
def sod_webhook():
    """Handle SOD (Start of Day) form submissions"""
    try:
        # Get form data
        form_data = request.get_json()
        if not form_data:
            return jsonify({'error': 'No JSON data received'}), 400
        
        # Get current date
        # Get current date (or test date if provided)
        test_date_str = request.args.get('test_date')
        if test_date_str:
            current_date = datetime.strptime(test_date_str, '%Y-%m-%d').date()
        else:
            current_date = date.today()
        
        # Check if previous day's EOD was completed
        prev_complete, prev_message = db_manager.check_previous_day_completion(current_date)
        if not prev_complete:
            print(f"Warning: {prev_message}")
            # Note: We continue processing but log the warning
        
        # Store SOD data
        success = db_manager.upsert_sod_data(current_date, form_data)
        
        if success:
            # Generate/update markdown file
            markdown_gen = MarkdownGenerator()
            daily_entry = db_manager.get_daily_entry(current_date)
            markdown_gen.generate_daily_template(daily_entry)
            
            response = {
                'success': True,
                'message': 'SOD data processed successfully',
                'date': current_date.isoformat(),
                'previous_day_warning': prev_message if not prev_complete else None
            }
            
            return jsonify(response), 200
        else:
            return jsonify({'error': 'Failed to store SOD data'}), 500
            
    except Exception as e:
        print(f"Error processing SOD webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/webhook/eod', methods=['POST'])
def eod_webhook():
    """Handle EOD (End of Day) form submissions"""
    try:
        # Get form data
        form_data = request.get_json()
        if not form_data:
            return jsonify({'error': 'No JSON data received'}), 400
        
        # Get current date
        # Get current date (or test date if provided)
        test_date_str = request.args.get('test_date')
        if test_date_str:
            current_date = datetime.strptime(test_date_str, '%Y-%m-%d').date()
        else:
            current_date = date.today()
        
        # Check if current day's SOD was completed
        sod_complete, sod_message = db_manager.check_current_day_sod(current_date)
        if not sod_complete:
            print(f"Warning: {sod_message}")
            # Note: We continue processing but log the warning
        
        # Store EOD data
        success = db_manager.upsert_eod_data(current_date, form_data)
        
        if success:
            # Generate/update markdown file
            markdown_gen = MarkdownGenerator()
            daily_entry = db_manager.get_daily_entry(current_date)
            markdown_gen.generate_daily_template(daily_entry)
            
            response = {
                'success': True,
                'message': 'EOD data processed successfully',
                'date': current_date.isoformat(),
                'sod_warning': sod_message if not sod_complete else None
            }
            
            return jsonify(response), 200
        else:
            return jsonify({'error': 'Failed to store EOD data'}), 500
            
    except Exception as e:
        print(f"Error processing EOD webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/daily/<date_str>', methods=['GET'])
def get_daily_entry(date_str):
    """Get daily entry for a specific date"""
    try:
        # Parse date string
        entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get entry from database
        entry = db_manager.get_daily_entry(entry_date)
        
        if entry:
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
        else:
            return jsonify({'error': 'No entry found for this date'}), 404
            
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        print(f"Error getting daily entry: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/recent', methods=['GET'])
def get_recent_entries():
    """Get recent entries for monitoring"""
    try:
        days = request.args.get('days', 7, type=int)
        entries = db_manager.get_recent_entries(days)
        
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
    except Exception as e:
        print(f"Error getting recent entries: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/regenerate/<date_str>', methods=['POST'])
def regenerate_markdown(date_str):
    """Regenerate markdown file for a specific date"""
    try:
        # Parse date string
        entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get entry from database
        entry = db_manager.get_daily_entry(entry_date)
        
        if entry:
            # Regenerate markdown
            markdown_gen = MarkdownGenerator()
            markdown_gen.generate_daily_template(entry)
            
            return jsonify({
                'success': True,
                'message': f'Markdown regenerated for {date_str}'
            }), 200
        else:
            return jsonify({'error': 'No entry found for this date'}), 404
            
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        print(f"Error regenerating markdown: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Print current configuration
    print("Starting Automation Hub...")
    Config.print_config()
    
    # Create tables if they don't exist
    db_manager.create_tables()
    
    # Start Flask app
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)