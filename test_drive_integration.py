#!/usr/bin/env python3
"""
Test Google Drive integration with your existing automation hub
"""

import os
import sys
from datetime import datetime, date
from config import Config

def test_file_system_drive_manager():
    """Test the file system drive manager"""
    print("Testing File System Drive Manager...")
    print(f"Sync Path: {Config.GOOGLE_DRIVE_SYNC_PATH}")
    
    try:
        from file_system import FileSystemDriveManager
        
        # Initialize the manager
        drive_manager = FileSystemDriveManager(Config.GOOGLE_DRIVE_SYNC_PATH)
        
        # Test folder access
        test_result = drive_manager.test_sync_folder_access()
        
        if test_result['success']:
            print("✅ Sync folder access successful!")
            print(f"📁 Folder path: {test_result['sync_folder_path']}")
            print(f"📄 Existing files: {test_result['existing_files_count']}")
            print(f"🔄 Google Drive process: {test_result['google_drive_process']}")
            
            if test_result.get('warning'):
                print(f"⚠️  Warning: {test_result['warning']}")
            
            return True
        else:
            print(f"❌ Sync folder access failed: {test_result['error']}")
            print(f"💡 Suggestion: {test_result.get('suggestion', 'Check folder configuration')}")
            return False
            
    except ImportError:
        print("❌ Could not import FileSystemDriveManager")
        print("Make sure file_system.py exists in your project directory")
        return False
    except Exception as e:
        print(f"❌ Error testing drive manager: {e}")
        return False

def test_with_existing_markdown():
    """Test uploading an existing markdown file"""
    print("\nTesting with existing markdown file...")
    
    # Find the most recent markdown file
    daily_notes_dir = "daily_notes"
    
    if not os.path.exists(daily_notes_dir):
        print(f"❌ Daily notes directory not found: {daily_notes_dir}")
        return False
    
    markdown_files = [f for f in os.listdir(daily_notes_dir) if f.endswith('.md')]
    
    if not markdown_files:
        print(f"❌ No markdown files found in {daily_notes_dir}")
        return False
    
    # Use the most recent file
    markdown_files.sort()
    test_file = os.path.join(daily_notes_dir, markdown_files[-1])
    
    print(f"📄 Testing with file: {test_file}")
    
    try:
        from file_system import FileSystemDriveManager
        
        drive_manager = FileSystemDriveManager(Config.GOOGLE_DRIVE_SYNC_PATH)
        
        # Extract date from filename for the upload
        date_str = markdown_files[-1].replace('.md', '')
        test_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Test upload
        upload_result = drive_manager.upload_daily_note(test_file, test_date)
        
        if upload_result['success']:
            print("✅ File upload successful!")
            print(f"📁 Destination: {upload_result['destination_path']}")
            print(f"🔄 Action: {upload_result['action']}")
            print(f"📊 File size: {upload_result['file_size']} bytes")
            return True
        else:
            print(f"❌ File upload failed: {upload_result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing file upload: {e}")
        return False

def test_markdown_generation_with_drive():
    """Test generating markdown with Google Drive integration"""
    print("\nTesting markdown generation with Google Drive...")
    
    try:
        from markdown_generator import MarkdownGenerator
        from database import DatabaseManager
        
        # Get today's data
        db_manager = DatabaseManager()
        today = date.today()
        daily_entry = db_manager.get_daily_entry(today)
        
        if not daily_entry:
            print(f"❌ No daily entry found for {today}")
            print("Submit your SOD/EOD forms first, then test again")
            return False
        
        # Generate markdown with drive integration
        markdown_gen = MarkdownGenerator()
        result = markdown_gen.generate_daily_template(daily_entry)
        
        if result:
            print(f"✅ Markdown generated: {result}")
            
            # Check if it has drive manager
            if markdown_gen.drive_manager:
                print("✅ Google Drive integration active in markdown generator")
            else:
                print("⚠️  Google Drive integration not active")
            
            return True
        else:
            print("❌ Markdown generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing markdown generation: {e}")
        return False

def show_configuration():
    """Show current Google Drive configuration"""
    print("Google Drive Configuration:")
    print(f"  Enabled: {Config.GOOGLE_DRIVE_ENABLED}")
    print(f"  Method: {Config.GOOGLE_DRIVE_METHOD}")
    print(f"  Sync Path: {Config.GOOGLE_DRIVE_SYNC_PATH}")
    print()
    
    if not Config.GOOGLE_DRIVE_ENABLED:
        print("❌ Google Drive is disabled")
        print()
        print("To enable:")
        print("1. Set environment variable: export GOOGLE_DRIVE_ENABLED=true")
        print("2. Set sync path: export GOOGLE_DRIVE_SYNC_PATH='/path/to/your/sync/folder'")
        print("3. Restart your Flask app")
        return False
    
    return True

def test_sync_folder_structure():
    """Test that the sync folder has the right structure"""
    print("\nTesting sync folder structure...")
    
    sync_path = Config.GOOGLE_DRIVE_SYNC_PATH
    
    if not os.path.exists(sync_path):
        print(f"❌ Sync path does not exist: {sync_path}")
        print()
        print("This means:")
        print("1. Google Drive desktop app is not installed/running, OR")
        print("2. The folder path in config is incorrect, OR") 
        print("3. The folder doesn't exist in your Google Drive")
        print()
        print("Expected structure: GoogleDrive/USV/My Calendar/My Daily Notes")
        return False
    
    # Check if we can write to it
    test_file = os.path.join(sync_path, '.automation_test')
    
    try:
        with open(test_file, 'w') as f:
            f.write("Test file for automation hub")
        
        os.remove(test_file)
        print(f"✅ Sync folder exists and is writable: {sync_path}")
        
        # List existing files
        existing_files = [f for f in os.listdir(sync_path) if f.endswith('.md')]
        print(f"📄 Found {len(existing_files)} existing markdown files")
        
        return True
        
    except Exception as e:
        print(f"❌ Cannot write to sync folder: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Google Drive Integration")
    print("=" * 50)
    
    # Show configuration
    if not show_configuration():
        return
    
    # Test components step by step
    tests = [
        ("Sync Folder Structure", test_sync_folder_structure),
        ("File System Drive Manager", test_file_system_drive_manager),
        ("Existing Markdown Upload", test_with_existing_markdown),
        ("Markdown Generation with Drive", test_markdown_generation_with_drive)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}...")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Google Drive integration is working.")
        print(f"📁 Files will sync to: {Config.GOOGLE_DRIVE_SYNC_PATH}")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\nCommon solutions:")
        print("1. Install Google Drive desktop app on your Pi")
        print("2. Make sure the folder path exists in Google Drive")
        print("3. Check environment variables are set correctly")

if __name__ == "__main__":
    main()