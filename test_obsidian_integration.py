#!/usr/bin/env python3
import os
from datetime import date, datetime

print("Testing integration with your Obsidian vault...")

# Set the environment variables in code for this test
os.environ['GOOGLE_DRIVE_ENABLED'] = 'true'
os.environ['GOOGLE_DRIVE_SYNC_PATH'] = r'C:\Users\Victo\Documents\Growth\Ultimate Starter Vault 2.1\USV\My Calendar\My Daily Notes'

from config import Config
print(f"Config path: {Config.GOOGLE_DRIVE_SYNC_PATH}")
print(f"Google Drive enabled: {Config.GOOGLE_DRIVE_ENABLED}")

# Test the file system manager
try:
    from file_system import FileSystemDriveManager
    
    manager = FileSystemDriveManager(Config.GOOGLE_DRIVE_SYNC_PATH)
    
    # Test folder access
    test_result = manager.test_sync_folder_access()
    
    if test_result['success']:
        print("✅ Obsidian vault folder access successful!")
        print(f"📁 Existing files: {test_result['existing_files_count']}")
        if test_result.get('sample_files'):
            print(f"📄 Sample files: {test_result['sample_files'][:3]}")
        
        # Test with a real markdown generation (using mock data)
        print("\n🧪 Testing markdown generation and save to vault...")
        
        # Reload markdown generator to pick up new environment
        from importlib import reload
        import markdown_generator
        reload(markdown_generator)
        
        # Create mock daily entry
        mock_daily_entry = {
            'date': date.today(),
            'sod_data': {
                "What am I looking forward to the most today?": "Testing the automation with my real Obsidian vault!",
                "Today's Big 3": "1. Complete automation testing\n2. Verify file appears in Obsidian\n3. Set up for production use"
            },
            'sod_timestamp': datetime.now(),
            'eod_data': None,
            'eod_timestamp': None
        }
        
        # Generate markdown
        generator = markdown_generator.MarkdownGenerator()
        result = generator.generate_daily_template(mock_daily_entry)
        
        if result:
            filename = f"{date.today().strftime('%Y-%m-%d')}.md"
            vault_file = os.path.join(Config.GOOGLE_DRIVE_SYNC_PATH, filename)
            
            print(f"✅ Markdown generated: {result}")
            
            if os.path.exists(vault_file):
                print(f"✅ File exists in Obsidian vault: {vault_file}")
                
                # Check content
                with open(vault_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "Testing the automation with my real Obsidian vault!" in content:
                    print("✅ File contains correct test data")
                    print()
                    print("🎉 SUCCESS! The automation is working with your Obsidian vault!")
                    print(f"📝 Open Obsidian and check for today's note: {filename}")
                    print("   The file should appear in your My Calendar/My Daily Notes folder")
                else:
                    print("❌ File content doesn't match expected data")
            else:
                print(f"❌ File not found in vault: {vault_file}")
        else:
            print("❌ Markdown generation failed")
            
    else:
        print(f"❌ Vault folder access failed: {test_result['error']}")
        if test_result.get('suggestion'):
            print(f"💡 {test_result['suggestion']}")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n📋 Next steps:")
print("1. Check Obsidian - today's note should appear")
print("2. If successful, update your config permanently")
print("3. Test with real SOD/EOD form submissions")