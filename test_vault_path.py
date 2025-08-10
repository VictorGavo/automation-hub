#!/usr/bin/env python3
import os

print("Testing your Obsidian vault path...")

# Your vault path
vault_base = r"C:\Users\Victo\Documents\Growth\Ultimate Starter Vault 2.1\USV"
daily_notes_path = os.path.join(vault_base, "My Calendar", "My Daily Notes")

print(f"Vault base: {vault_base}")
print(f"Daily notes path: {daily_notes_path}")

# Check if paths exist
if os.path.exists(vault_base):
    print("✅ Vault base path exists")
    
    # Show vault structure
    try:
        vault_contents = os.listdir(vault_base)
        print(f"📁 Vault contents: {vault_contents}")
        
        # Look for calendar-related folders
        calendar_folders = [f for f in vault_contents if 'calendar' in f.lower() or 'daily' in f.lower()]
        if calendar_folders:
            print(f"📅 Calendar-related folders: {calendar_folders}")
        
    except Exception as e:
        print(f"Cannot list vault contents: {e}")
else:
    print("❌ Vault base path does not exist")

if os.path.exists(daily_notes_path):
    print("✅ Daily notes path exists")
    
    # Show existing daily notes
    try:
        daily_files = [f for f in os.listdir(daily_notes_path) if f.endswith('.md')]
        print(f"📄 Found {len(daily_files)} markdown files")
        if daily_files:
            # Show a few recent files
            daily_files.sort()
            recent_files = daily_files[-3:] if len(daily_files) >= 3 else daily_files
            print(f"📝 Recent files: {recent_files}")
    except Exception as e:
        print(f"Cannot list daily notes: {e}")
else:
    print("❌ Daily notes path does not exist")
    
    # Let's explore and find the correct structure
    print("\n🔍 Exploring vault structure to find daily notes folder...")
    
    def explore_directory(path, max_depth=2, current_depth=0):
        if current_depth >= max_depth:
            return
        
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                indent = "  " * current_depth
                
                if os.path.isdir(item_path):
                    print(f"{indent}📁 {item}/")
                    # Look for calendar or daily-related folders
                    if any(keyword in item.lower() for keyword in ['calendar', 'daily', 'notes']):
                        print(f"{indent}   ⭐ This looks promising!")
                        explore_directory(item_path, max_depth, current_depth + 1)
                    elif current_depth < 1:  # Only go one level deep for non-calendar folders
                        explore_directory(item_path, max_depth, current_depth + 1)
        except PermissionError:
            print(f"{indent}❌ Permission denied")
        except Exception as e:
            print(f"{indent}❌ Error: {e}")
    
    if os.path.exists(vault_base):
        explore_directory(vault_base)

print("\n💡 Please provide the exact path to your daily notes folder")
print("   (where you want the automation to save the markdown files)")
