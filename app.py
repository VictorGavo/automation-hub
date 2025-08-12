from flask import Flask, request, jsonify
from datetime import datetime, date
import json
from flask import session, redirect, url_for, render_template, send_from_directory
from database import DatabaseManager
from markdown_generator import MarkdownGenerator
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = Config.SECRET_KEY
# Initialize database manager
db_manager = DatabaseManager() # COMMENTED OUT FOR LOCAL DEV

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
            # Update Daily Capture template with SOD data AND goals
            # Update Daily Capture template with SOD data AND goals
            notion_result = None
            if Config.NOTION_ENABLED:
                try:
                    from notion_manager import NotionManager
                    notion_manager = NotionManager()
                    
                    # Get current goals if enabled
                    goals_blocks = []
                    if Config.OBSIDIAN_GOALS_ENABLED:
                        from obsidian_goal_manager import ObsidianGoalManager
                        goal_manager = ObsidianGoalManager()
                        goals_result = goal_manager.get_current_goals(current_date)
                        
                        if goals_result['goals']:
                            goals_blocks = goal_manager.format_goals_for_notion(goals_result['goals'])
                            cache_status = "cached" if goals_result['cache_used'] else "fresh"
                            goals_found = sum(1 for goal in goals_result['goals'].values() if goal.get('found', False))
                            print(f"✅ Loaded {goals_found}/4 goals from Obsidian ({cache_status})")
                    
                    # Update template with SOD data 
                    notion_result = notion_manager.update_daily_capture_template(form_data)
                    
                    if notion_result['success']:
                        updated_sections = notion_result.get('updated_sections', [])
                        print(f"✅ Updated Notion Daily Capture: {', '.join(updated_sections)}")
                    else:
                        print(f"❌ Failed to update Notion Daily Capture: {notion_result['error']}")
                        
                except Exception as e:
                    print(f"❌ Error updating Notion Daily Capture: {e}")
            
            # Generate/update markdown file
            markdown_gen = MarkdownGenerator()
            daily_entry = db_manager.get_daily_entry(current_date)

            # Only generate if no EOD data exists (first time creation)
            if not daily_entry['eod_data']:
                markdown_gen.generate_daily_template(daily_entry)
                print("✅ Generated initial daily template")
            else:
                print("ℹ️ EOD data exists, skipping markdown generation")
            

            response = {
                'success': True,
                'message': 'SOD data processed successfully',
                'date': current_date.isoformat(),
                'previous_day_warning': prev_message if not prev_complete else None,
                'notion_update': notion_result['success'] if notion_result else False
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
            # Process Notion captures (this happens during markdown generation)
            # but we'll track the results here for the API response
            notion_capture_result = None

            # Generate/update markdown file (this will process Notion captures)
            markdown_gen = MarkdownGenerator()
            daily_entry = db_manager.get_daily_entry(current_date)
            markdown_path = markdown_gen.generate_daily_template(daily_entry)

            # Check if markdown generation was successful
            markdown_success = markdown_path is not None
            
            response = {
                'success': True,
                'message': 'EOD data processed successfully',
                'date': current_date.isoformat(),
                'sod_warning': sod_message if not sod_complete else None,
                'markdown_generated': markdown_success,
                'notion_captures_processed': Config.NOTION_ENABLED and daily_entry['eod_data'] is not None
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

@app.route('/api/notion/update-template', methods=['POST'])
def update_notion_template():
    """Manually update Notion Daily Capture template with SOD data"""
    try:
        if not Config.NOTION_ENABLED:
            return jsonify({'error': 'Notion integration not enabled'}), 400
        
        # Get date parameter
        date_str = request.args.get('date')
        if date_str:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            entry_date = date.today()
        
        # Get daily entry
        entry = db_manager.get_daily_entry(entry_date)
        if not entry or not entry['sod_data']:
            return jsonify({'error': 'No SOD data found for this date'}), 404
        
        # Update Notion template
        from notion_manager import NotionManager
        notion_manager = NotionManager()
        result = notion_manager.update_daily_capture_template(entry['sod_data'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Notion template updated successfully',
                'date': entry_date.isoformat(),
                'updated_sections': result.get('updated_sections', []),
                'blocks_added': result.get('blocks_added', 0)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        print(f"Error updating Notion template: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/notion/test', methods=['GET'])
def test_notion_connection():
    """Test Notion API connection"""
    try:
        if not Config.NOTION_ENABLED:
            return jsonify({'error': 'Notion integration not enabled'}), 400
        
        from notion_manager import NotionManager
        notion_manager = NotionManager()
        result = notion_manager.test_connection()
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Print current configuration
    print("Starting Automation Hub...")
    Config.print_config()

    # Create tables if they don't exist
    # db_manager.create_tables() # COMMENTED OUT FOR LOCAL DEV

    # Start Flask app
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)

import os

# Dashboard login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '').encode()
        stored_hash = Config.DASHBOARD_PASSWORD_HASH.encode()
        if bcrypt.checkpw(password, stored_hash):
            session['dashboard_authenticated'] = True
            return redirect(url_for('dashboard'))
        else:
            # Show login form with error
            return send_from_directory(os.path.join(os.path.dirname(__file__), '../public'), 'dashboard.html')
    # GET: show login form
    return send_from_directory(os.path.join(os.path.dirname(__file__), '../public'), 'dashboard.html')

# Dashboard route (protected)
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not session.get('dashboard_authenticated'):
        return redirect(url_for('login'))
    # Serve dashboard.html from public directory
    return send_from_directory(os.path.join(os.path.dirname(__file__), '../public'), 'dashboard.html')
    print("Starting Automation Hub...")
    Config.print_config()
    
    # Create tables if they don't exist
    db_manager.create_tables()
    
    # Start Flask app
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
