#!/usr/bin/env python3
import os
import tempfile
from datetime import datetime

print("Testing FileSystemDriveManager integration with MarkdownGenerator...")

# Set up environment for testing
test_dir = os.path.join(tempfile.gettempdir(), 'test_drive_sync')
os.environ['GOOGLE_DRIVE_ENABLED'] = 'true'
os.environ['GOOGLE_DRIVE_SYNC_PATH'] = test_dir

print(f"Using test directory: {test_dir}")

try:
    # Test that MarkdownGenerator can import and initialize the drive manager
    from importlib import reload
    import markdown_generator
    reload(markdown_generator)  # Reload to pick up environment changes
    
    generator = markdown_generator.MarkdownGenerator()
    
    if generator.drive_manager is not None:
        print("✅ MarkdownGenerator successfully initialized FileSystemDriveManager")
        print(f"   Sync path: {generator.drive_manager.sync_folder_path}")
        
        # Test that the manager can access the folder
        test_result = generator.drive_manager.test_sync_folder_access()
        if test_result['success']:
            print("✅ Drive manager can access sync folder")
        else:
            print(f"❌ Drive manager cannot access sync folder: {test_result['error']}")
        
        # Test that it can list files (should be empty initially)
        files = generator.drive_manager.list_daily_notes()
        print(f"✅ Found {len(files)} existing files in sync folder")
        
    else:
        print("❌ MarkdownGenerator failed to initialize drive manager")
    
    # Clean up
    import shutil
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    print("✅ Test completed and cleaned up")
    
except Exception as e:
    print(f"❌ Integration test failed: {e}")
    import traceback
    traceback.print_exc()