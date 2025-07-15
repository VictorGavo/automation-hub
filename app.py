from flask import Flask, request, jsonify
import logging
from datetime import datetime, date
import json
from database import DatabaseManager
from config import DATABASE_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize database
db = DatabaseManager(DATABASE_CONFIG)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Log the incoming request
        logger.info(f"Received webhook at {datetime.now()}")
        
        # Get the JSON data from the request
        data = request.get_json()
        
        # Log the received data
        logger.info(f"Received data: {json.dumps(data, indent=2)}")
        
        # Connect to database
        db.connect()
        
        # Insert SOD response for today
        today = date.today()
        db.insert_sod_response(today, data)
        
        logger.info(f"SOD response saved to database for {today}")
        
        # Disconnect from database
        db.disconnect()
        
        # Return success response
        return jsonify({
            "status": "success", 
            "message": "SOD data received and saved successfully",
            "date": today.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        # Make sure to disconnect even if there's an error
        try:
            db.disconnect()
        except:
            pass
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

@app.route('/sod/<date_str>', methods=['GET'])
def get_sod_data(date_str):
    """Get SOD data for a specific date (format: YYYY-MM-DD)"""
    try:
        # Parse the date
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Connect to database
        db.connect()
        
        # Get SOD response
        sod_data = db.get_sod_response(target_date)
        
        # Disconnect from database
        db.disconnect()
        
        if sod_data:
            return jsonify({"status": "success", "data": sod_data}), 200
        else:
            return jsonify({"status": "not_found", "message": f"No SOD data found for {date_str}"}), 404
            
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        logger.error(f"Error retrieving SOD data: {str(e)}")
        try:
            db.disconnect()
        except:
            pass
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)