#!/usr/bin/env python3
import os
import platform

print("Finding Google Drive path on your system...")
print(f"Operating System: {platform.system()}")

# Check common Google Drive locations on Windows
possible_paths = [
    "G:\\",  # Your network drive
    "G:\\USV",
    "G:\\USV\\My Calendar",
    "G:\\USV\\My Calendar\\My Daily Notes",
    os.path.expanduser("~\\Google Drive"),
    os.path.expanduser("~\\GoogleDrive"),
    "C:\\Users\\Victo\\Google Drive",
    "C:\\Users\\Victo\\GoogleDrive",
]

print("\nChecking possible Google Drive locations:")

for path in possible_paths:
    if os.path.exists(path):
        print(f"✅ Found: {path}")
        try:
            contents = os.listdir(path)
            print(f"   Contents: {contents[:5]}...")  # Show first 5 items
        except Exception as e:
            print(f"   Cannot list contents: {e}")
    else:
        print(f"❌ Not found: {path}")

print("\nLet's explore the G: drive structure:")

# Explore G: drive if it exists
if os.path.exists("G:\\"):
    try:
        print("\nG:\\ contents:")
        contents = os.listdir("G:\\")
        for item in contents:
            item_path = os.path.join("G:\\", item)
            if os.path.isdir(item_path):
                print(f"📁 {item}/")
                try:
                    # Look one level deeper
                    sub_contents = os.listdir(item_path)
                    for sub_item in sub_contents[:3]:  # Show first 3 items
                        print(f"   📄 {sub_item}")
                    if len(sub_contents) > 3:
                        print(f"   ... and {len(sub_contents) - 3} more items")
                except:
                    print("   (Cannot access)")
            else:
                print(f"📄 {item}")
    except Exception as e:
        print(f"Cannot access G:\\: {e}")

print("\nPlease manually check:")
print("1. Open File Explorer")
print("2. Navigate to G:\\ drive") 
print("3. Look for USV or any folder that might contain your daily notes")
print("4. Share the full path you find")