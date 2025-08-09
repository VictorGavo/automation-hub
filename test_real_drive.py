#!/usr/bin/env python3
import os
from datetime import date, datetime

print("Testing with real Google Drive path...")

# Show current environment
print(f"GOOGLE_DRIVE_ENABLED: {os.getenv('GOOGLE_DRIVE_ENABLED', 'Not set')}")
print(f"GOOGLE_DRIVE_SYNC_PATH: {os.getenv('GOOGLE_DRIVE_SYNC_PATH', 'Not set')}")

# Check if the path exists
from config import Config
print(f"Config path: {Config.GOOGLE_DRIVE_SYNC_PATH}")

if os.path.exists(Config.GOOGLE_DRIVE_SYNC_PATH):
    print(f"✅ Google Drive folder exists: {Config.GOOGLE_DRIVE_SYNC_PATH}")
else:
    print(f"❌ Google Drive folder not found: {Config.GOOGLE_DRIVE_SYNC_PATH}")
    print()
    print("Please check:")
    print("1. Is Google Drive desktop app installed and running?")
    print("2. Is the folder path correct?")
    print("3. Does the 'USV/My Calendar/My Daily Notes' folder exist in your Google Drive?")
    exit(1)

try:
    # Test with real path
    from file_system import FileSystemDriveManager
    
    manager = FileSystemDriveManager(Config.GOOGLE_DRIVE_SYNC_PATH)
    
    # Test folder access
    test_result = manager.test_sync_folder_access()
    
    if test_result['success']:
        print("✅ Real Google Drive folder access successful!")
        print(f"📁 Existing files: {test_result['existing_files_count']}")
        if test_result.get('sample_files'):
            print(f"📄 Sample files: {test_result['sample_files']}")
        
        # Test creating a small test file
        test_file = os.path.join('daily_notes', 'test_upload.md')
        
        # Create a test file first
        os.makedirs('daily_notes', exist_ok=True)
        with open(test_file, 'w') as f:
            f.write("# Test Upload\nThis is a test file for Google Drive integration.")
        
        # Test upload
        upload_result = manager.upload_daily_note(test_file, datetime.now())
        
        if upload_result['success']:
            print(f"✅ Test file upload successful!")
            print(f"   File: {upload_result['file_name']}")
            print(f"   Action: {upload_result['action']}")
            print(f"   Destination: {upload_result['destination_path']}")
            print()
            print("🎉 Check your Google Drive folder - the test file should be there!")
            print("You can delete 'test_upload.md' from Google Drive when you're done testing.")
        else:
            print(f"❌ Test file upload failed: {upload_result['error']}")
        
        # Clean up local test file
        if os.path.exists(test_file):
            os.remove(test_file)
            
    else:
        print(f"❌ Google Drive folder access failed: {test_result['error']}")
        if test_result.get('suggestion'):
            print(f"💡 Suggestion: {test_result['suggestion']}")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()