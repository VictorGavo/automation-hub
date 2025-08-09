#!/usr/bin/env python3
import os
import tempfile
from datetime import date, datetime

print("Testing complete markdown generation + Google Drive upload workflow...")

# Set up test environment
test_dir = os.path.join(tempfile.gettempdir(), 'test_drive_workflow')
os.environ['GOOGLE_DRIVE_ENABLED'] = 'true'
os.environ['GOOGLE_DRIVE_SYNC_PATH'] = test_dir

print(f"Using test directory: {test_dir}")

try:
    # Reload markdown generator to pick up environment changes
    from importlib import reload
    import markdown_generator
    reload(markdown_generator)
    
    # Create a mock daily entry (like what comes from your database)
    mock_daily_entry = {
        'date': date.today(),
        'sod_data': {
            "What am I looking forward to the most today?": "Testing the Google Drive integration!",
            "Today's Big 3": "1. Complete Google Drive integration\n2. Test the workflow\n3. Celebrate success"
        },
        'sod_timestamp': datetime.now(),
        'eod_data': None,
        'eod_timestamp': None
    }
    
    # Generate markdown with Google Drive upload
    generator = markdown_generator.MarkdownGenerator()
    result = generator.generate_daily_template(mock_daily_entry)
    
    if result:
        print(f"✅ Markdown generated: {result}")
        
        # Check if file exists in sync folder
        sync_filename = f"{date.today().strftime('%Y-%m-%d')}.md"
        sync_path = os.path.join(test_dir, sync_filename)
        
        if os.path.exists(sync_path):
            print(f"✅ File successfully copied to sync folder: {sync_path}")
            
            # Verify content
            with open(sync_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "Testing the Google Drive integration!" in content:
                print("✅ Sync file contains correct SOD data")
            else:
                print("❌ Sync file missing expected content")
                
        else:
            print(f"❌ File not found in sync folder: {sync_path}")
    else:
        print("❌ Markdown generation failed")
    
    # Clean up
    import shutil
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    if result and os.path.exists(result):
        os.remove(result)
    print("✅ Test completed and cleaned up")
    
except Exception as e:
    print(f"❌ Workflow test failed: {e}")
    import traceback
    traceback.print_exc()