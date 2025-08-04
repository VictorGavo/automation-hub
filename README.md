# Automation Hub - Daily Books Workflow

A Flask-based automation server for processing daily Start-of-Day (SOD) and End-of-Day (EOD) forms, generating markdown templates, and managing daily note workflows.

## Current Status: Step 4 Complete ✅

**Working Features:**
- SOD form processing via Google Apps Script webhook
- PostgreSQL data storage with JSON support
- Daily markdown template generation with populated SOD responses
- REST API for data retrieval

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL 
- ngrok (for webhook testing)

### Installation

1. **Clone repository and install dependencies:**
   ```bash
   git clone <repository-url>
   cd automation-hub
   pip install -r requirements.txt
   ```

2. **Configure PostgreSQL:**
   - Create database: `automation_hub`
   - Update `config.py` with your database credentials

3. **Run database setup:**
   ```bash
   python test_db.py
   ```

4. **Start the server:**
   ```bash
   python app.py
   ```

5. **Setup ngrok for webhook testing:**
   ```bash
   ngrok http 5000
   ```

### Google Apps Script Configuration

Update your SOD form's Apps Script with the ngrok URL:
```javascript
var response = UrlFetchApp.fetch('https://your-ngrok-url.ngrok.io/webhook', options);
```

## API Endpoints

- `POST /webhook` - Receive SOD form data
- `GET /health` - Health check
- `GET /sod/YYYY-MM-DD` - Retrieve SOD data for specific date

## File Structure

- `app.py` - Main Flask application
- `database.py` - PostgreSQL database manager
- `config.py` - Configuration settings
- `markdown_generator.py` - Daily template generator
- `test_*.py` - Test scripts

## Next Development Steps

**Step 5: Google Drive Integration**
- Upload generated markdown files to Google Drive
- Implement proper folder structure

**Step 6: EOD Form Processing**
- Add EOD webhook endpoint
- Update markdown templates with EOD data

**Step 7: Previous Day Failsafe**
- Check for missing EOD submissions
- Handle previous day completion

**Step 8: Mobile Notes Integration**
- Notion API integration
- Mobile capture processing

**Step 9: Dockerization**
- Container setup for Raspberry Pi deployment

**Step X: Calendar Integration**
- Integrate daily calendar events display
- Compare planned vs actual time tracking
- Sync with Google Calendar API
- Show meeting summaries and schedule adherence

## Testing

```bash
# Test database connection
python test_db.py

# Test markdown generation
python test_markdown.py

# Test webhook with sample data
python test_webhook.py
```

## Development Approach

### 🎯 Self-Driven Development Branch

**Philosophy**: This branch emphasizes hands-on learning and manual coding to build deep understanding of the system.

**Learning Goals**:
- Master Flask application architecture and routing
- Understand PostgreSQL database operations and JSON handling  
- Learn API integration patterns (Notion, Google Drive)
- Practice Python testing, debugging, and best practices
- Build problem-solving and troubleshooting skills

### Development Workflow

**📚 Research First**: 
- Read documentation thoroughly before coding
- Understand the problem domain and requirements
- Study existing code patterns in the project

**🔨 Manual Implementation**:
- Write code yourself without AI assistance
- Break complex problems into smaller pieces
- Use print statements and logging for debugging
- Test incrementally as you build

**🧪 Test-Driven Approach**:
- Write tests before implementing features
- Run tests frequently to catch issues early
- Use the existing test suite as examples

### Available Resources

- **Flask docs**: https://flask.palletsprojects.com/
- **PostgreSQL Python**: https://www.psycopg.org/docs/
- **Notion API**: https://developers.notion.com/
- **Python testing**: https://docs.pytest.org/

### Next Development Tasks

1. **Fix SOD form data mapping** (see daily notes for specific issues)
2. **Debug EOD processing logic** (captures not updating correctly)  
3. **Improve template generation** (success criteria population)
4. **Plan Raspberry Pi deployment** (replace Cloudflare tunneling)