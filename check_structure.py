#!/usr/bin/env python3
"""
Quick Structure Check
Validates the basic directory structure before running full tests
"""

import os
import sys

def check_structure():
    """Check if the modular structure is properly set up"""
    print("🔍 Checking modular structure...")
    
    # Check if modules directory exists
    if not os.path.exists('modules'):
        print("❌ modules/ directory not found")
        print("   Run: python migrate_to_modular.py")
        return False
    
    print("✅ modules/ directory exists")
    
    # Check required module files
    required_files = [
        'modules/__init__.py',
        'modules/core.py',
        'modules/daily_books.py',
        'modules/daily_capture.py',
        'modules/webhook_handlers.py'
    ]
    
    missing_files = []
    placeholder_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} exists")
            
            # Check if it's a placeholder
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'placeholder' in content.lower() and len(content) < 200:
                        placeholder_files.append(file_path)
            except:
                try:
                    with open(file_path, 'r', encoding='latin1') as f:
                        content = f.read()
                        if 'placeholder' in content.lower() and len(content) < 200:
                            placeholder_files.append(file_path)
                except:
                    print(f"⚠️  Could not read {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    if placeholder_files:
        print(f"\n⚠️  Placeholder files found: {', '.join(placeholder_files)}")
        print("   Replace these with actual implementations before testing")
        return False
    
    # Check dependencies
    required_deps = ['config.py', 'database.py', 'markdown_generator.py']
    missing_deps = [dep for dep in required_deps if not os.path.exists(dep)]
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        return False
    
    for dep in required_deps:
        print(f"✅ {dep} exists")
    
    print("\n🎉 Structure looks good! Ready for testing.")
    return True

def main():
    """Main function"""
    if not check_structure():
        print("\n💡 Next steps:")
        print("1. Run: python migrate_to_modular.py (if modules/ doesn't exist)")
        print("2. Copy the module implementations from the artifacts")
        print("3. Run this check again")
        sys.exit(1)
    else:
        print("\n✅ Ready to run: python test_modular_structure.py")
        sys.exit(0)

if __name__ == '__main__':
    main()