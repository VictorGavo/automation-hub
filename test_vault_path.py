#!/usr/bin/env python3
"""
Test vault path configuration and daily notes directory
"""
import os
from config import Config


def test_vault_configuration():
    """Test current vault path configuration"""
    print("Testing Obsidian vault path configuration...")
    
    # Check if Google Drive sync is configured
    if Config.GOOGLE_DRIVE_ENABLED:
        vault_path = Config.GOOGLE_DRIVE_SYNC_PATH
        print(f"✅ Google Drive sync enabled")
        print(f"📁 Configured path: {vault_path}")
        
        if os.path.exists(vault_path):
            print("✅ Vault path exists")
            return test_directory_structure(vault_path)
        else:
            print("❌ Vault path does not exist")
            print(f"   Please ensure the path exists: {vault_path}")
            return False
    else:
        print("❌ Google Drive sync not enabled")
        print("   Set GOOGLE_DRIVE_ENABLED=true and GOOGLE_DRIVE_SYNC_PATH")
        return False


def test_directory_structure(vault_path):
    """Test the structure of the vault directory"""
    print(f"\nTesting directory structure...")
    
    try:
        contents = os.listdir(vault_path)
        print(f"📁 Directory contents: {len(contents)} items")
        
        # Check for existing markdown files
        md_files = [f for f in contents if f.endswith('.md')]
        if md_files:
            print(f"📄 Found {len(md_files)} markdown files")
            # Show most recent files
            md_files.sort()
            recent_files = md_files[-3:] if len(md_files) > 3 else md_files
            for file in recent_files:
                print(f"   - {file}")
        
        return True
        
    except PermissionError:
        print("❌ Permission denied accessing vault directory")
        return False
    except Exception as e:
        print(f"❌ Error accessing vault: {e}")
        return False


def test_write_permissions():
    """Test write permissions in the vault directory"""
    if not Config.GOOGLE_DRIVE_ENABLED:
        return False
        
    vault_path = Config.GOOGLE_DRIVE_SYNC_PATH
    if not os.path.exists(vault_path):
        return False
    
    print(f"\nTesting write permissions...")
    test_file = os.path.join(vault_path, "test_write_permissions.tmp")
    
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✅ Write permissions confirmed")
        return True
    except Exception as e:
        print(f"❌ Write permission test failed: {e}")
        return False


def run_vault_tests():
    """Run all vault-related tests"""
    print("=" * 50)
    print("VAULT PATH TESTS")
    print("=" * 50)
    
    tests = [
        test_vault_configuration,
        test_write_permissions
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Vault tests passed: {passed}/{total}")
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = run_vault_tests()
    sys.exit(0 if success else 1)