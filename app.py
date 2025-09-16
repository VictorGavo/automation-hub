"""
Automation Hub - Streamlined Flask Application
Modular architecture with clean separation of concerns
"""

from flask import Flask, jsonify, session, redirect, url_for, send_from_directory
from datetime import datetime
import os
import bcrypt
import subprocess

# Import configuration and database
from config import Config
from database import DatabaseManager

# Import modular handlers
from modules.webhook_handlers import create_webhook_handlers, create_api_handlers

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Initialize handlers
webhook_handlers = create_webhook_handlers()
api_handlers = create_api_handlers()

# Initialize database manager
db_manager = DatabaseManager()

# Add these imports at the top of your app.py if not already present
import subprocess
from datetime import datetime

# Your existing health endpoint - keep as is!
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': Config.DB_NAME,
        'testing_mode': Config.TESTING,
        'modules': {
            'daily_books': True,
            'daily_capture': True,
            'webhook_handlers': True,
            'notion_enabled': Config.NOTION_ENABLED,
            'obsidian_goals_enabled': Config.OBSIDIAN_GOALS_ENABLED,
            'google_drive_enabled': Config.GOOGLE_DRIVE_ENABLED
        }
    })

# ADD THIS NEW ENDPOINT for deployment verification
@app.route('/deploy-status', methods=['GET'])
def deploy_status():
    """Detailed deployment status for GitHub Actions"""
    try:
        # Get Git information
        git_info = get_git_deployment_info()
        
        # Test database connection (enhance your existing check)
        db_status = test_database_connection()
        
        # Test your existing modules
        module_tests = test_existing_modules()
        
        return jsonify({
            'deployment': '✅ Successful',
            'timestamp': datetime.now().isoformat(),
            'git': git_info,
            'database': db_status,
            'module_tests': module_tests,
            'config': {
                'database': Config.DB_NAME,
                'testing_mode': Config.TESTING,
                'notion_enabled': Config.NOTION_ENABLED,
                'obsidian_goals_enabled': Config.OBSIDIAN_GOALS_ENABLED,
                'google_drive_enabled': Config.GOOGLE_DRIVE_ENABLED
            }
        })
    except Exception as e:
        return jsonify({
            'deployment': '❌ Failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ADD THESE HELPER FUNCTIONS
def get_git_deployment_info():
    """Get Git deployment information"""
    try:
        # Get last commit info
        last_commit_result = subprocess.run(
            ['git', 'log', '-1', '--format=%H|%cd|%s'], 
            capture_output=True, text=True, cwd='/var/www/automation'
        )
        
        if last_commit_result.returncode == 0:
            commit_hash, commit_date, commit_msg = last_commit_result.stdout.strip().split('|', 2)
            short_hash = commit_hash[:7]
        else:
            short_hash, commit_date, commit_msg = "Unknown", "Unknown", "Unknown"
        
        # Get current branch
        branch_result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True, text=True, cwd='/var/www/automation'
        )
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "Unknown"
        
        return {
            'current_commit': short_hash,
            'last_deployment': commit_date,
            'last_commit_message': commit_msg,
            'current_branch': current_branch
        }
    except Exception as e:
        return {
            'error': f'Git info failed: {str(e)}',
            'current_commit': 'Unknown',
            'current_branch': 'Unknown'
        }

def test_database_connection():
    """Test database connection with more detail"""
    try:
        # Use your existing database connection method
        conn = get_db_connection()  # Your existing function
        
        # Test a simple query
        cursor = conn.execute('SELECT COUNT(*) FROM sqlite_master WHERE type="table"')
        table_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            'status': '✅ Connected',
            'database_type': Config.DB_NAME,
            'table_count': table_count,
            'testing_mode': Config.TESTING
        }
    except Exception as e:
        return {
            'status': f'❌ Error: {str(e)}',
            'database_type': Config.DB_NAME,
            'testing_mode': Config.TESTING
        }

def test_existing_modules():
    """Test your existing modules"""
    tests = {}
    
    # Test Daily Books module
    try:
        # Import your existing daily books functionality
        # Adjust import path based on your structure
        if hasattr(app, 'view_functions') and 'process_sod' in str(app.view_functions):
            tests['daily_books'] = '✅ SOD/EOD endpoints loaded'
        else:
            tests['daily_books'] = '⚠️ Endpoints not detected'
    except Exception as e:
        tests['daily_books'] = f'❌ Error: {str(e)}'
    
    # Test Daily Capture module  
    try:
        # Test if your daily capture functionality is working
        if hasattr(app, 'view_functions') and any('capture' in str(func) for func in app.view_functions.values()):
            tests['daily_capture'] = '✅ Capture endpoints loaded'
        else:
            tests['daily_capture'] = '⚠️ Endpoints not detected'
    except Exception as e:
        tests['daily_capture'] = f'❌ Error: {str(e)}'
    
    # Test Webhook handlers
    try:
        webhook_routes = [rule.rule for rule in app.url_map.iter_rules() if 'webhook' in rule.rule.lower()]
        if webhook_routes:
            tests['webhook_handlers'] = f'✅ Found {len(webhook_routes)} webhook routes'
        else:
            tests['webhook_handlers'] = '⚠️ No webhook routes detected'
    except Exception as e:
        tests['webhook_handlers'] = f'❌ Error: {str(e)}'
    
    # Test external integrations
    tests['notion_integration'] = '✅ Enabled' if Config.NOTION_ENABLED else '⚠️ Disabled'
    tests['obsidian_integration'] = '✅ Enabled' if Config.OBSIDIAN_GOALS_ENABLED else '⚠️ Disabled'
    tests['google_drive_integration'] = '✅ Enabled' if Config.GOOGLE_DRIVE_ENABLED else '⚠️ Disabled'
    
    return tests

# ADD THIS ENDPOINT for quick GitHub Actions verification
@app.route('/github-actions-test', methods=['GET'])
def github_actions_test():
    """Simple endpoint specifically for GitHub Actions to verify deployment"""
    try:
        # Quick tests that GitHub Actions can run
        conn = get_db_connection()
        conn.execute('SELECT 1')
        conn.close()
        
        return jsonify({
            'github_actions': '✅ Deployment verified',
            'timestamp': datetime.now().isoformat(),
            'database': '✅ Connected',
            'service': '✅ Running'
        })
    except Exception as e:
        return jsonify({
            'github_actions': '❌ Deployment failed',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

# ============================================================================
# WEBHOOK ENDPOINTS
# ============================================================================

@app.route('/webhook/sod', methods=['POST'])
def sod_webhook():
    """Handle SOD (Start of Day) form submissions"""
    return webhook_handlers.handle_sod_webhook()

@app.route('/webhook/eod', methods=['POST'])
def eod_webhook():
    """Handle EOD (End of Day) form submissions"""
    return webhook_handlers.handle_eod_webhook()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/daily/<date_str>', methods=['GET'])
def get_daily_entry(date_str):
    """Get daily entry for a specific date"""
    return api_handlers.get_daily_entry(date_str)

@app.route('/api/recent', methods=['GET'])
def get_recent_entries():
    """Get recent entries for monitoring"""
    return api_handlers.get_recent_entries()

@app.route('/api/regenerate/<date_str>', methods=['POST'])
def regenerate_markdown(date_str):
    """Regenerate markdown file for a specific date"""
    return api_handlers.regenerate_markdown(date_str)

@app.route('/api/notion/update-template', methods=['POST'])
def update_notion_template():
    """Manually update Notion Daily Capture template with SOD data"""
    return api_handlers.update_notion_template()

@app.route('/api/notion/', methods=['GET'])
def test_notion_connection():
    """Test Notion API connection"""
    return api_handlers.test_notion_connection()

# ============================================================================
# DASHBOARD ENDPOINTS (Optional)
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Dashboard login route"""
    from flask import request
    
    if request.method == 'POST':
        password = request.form.get('password', '').encode()
        stored_hash = Config.DASHBOARD_PASSWORD_HASH.encode()
        if bcrypt.checkpw(password, stored_hash):
            session['dashboard_authenticated'] = True
            return redirect(url_for('dashboard'))
        else:
            # Show login form with error
            return send_from_directory(
                os.path.join(os.path.dirname(__file__), '../public'), 
                'dashboard.html'
            )
    
    # GET: show login form
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), '../public'), 
        'dashboard.html'
    )

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Dashboard route (protected)"""
    if not session.get('dashboard_authenticated'):
        return redirect(url_for('login'))
    
    # Serve dashboard.html from public directory
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), '../public'), 
        'dashboard.html'
    )

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': {
            'webhooks': ['/webhook/sod', '/webhook/eod'],
            'api': ['/api/daily/<date>', '/api/recent', '/api/regenerate/<date>'],
            'notion': ['/api/notion/test', '/api/notion/update-template'],
            'health': ['/health']
        }
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

def initialize_application():
    """Initialize application components"""
    print("🚀 Starting Automation Hub...")
    
    # Print current configuration
    Config.print_config()
    
    # Create database tables if they don't exist
    try:
        db_manager.create_tables()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    
    # Test integrations
    if Config.NOTION_ENABLED:
        print("✅ Notion integration enabled")
    else:
        print("ℹ️ Notion integration disabled")
    
    if Config.OBSIDIAN_GOALS_ENABLED:
        print("✅ Obsidian goals integration enabled")
    else:
        print("ℹ️ Obsidian goals integration disabled")
    
    if Config.GOOGLE_DRIVE_ENABLED:
        print("✅ Google Drive integration enabled")
    else:
        print("ℹ️ Google Drive integration disabled")
    
    print("🎉 Automation Hub ready!")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    try:
        initialize_application()
        
        # Start Flask app
        app.run(
            debug=Config.DEBUG, 
            host='0.0.0.0', 
            port=5000
        )
        
    except Exception as e:
        print(f"💥 Failed to start application: {e}")
        exit(1)
