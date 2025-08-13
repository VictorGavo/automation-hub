#!/usr/bin/env python3
"""
Check Module Content
See what's actually in the module files
"""

import os

def check_module_content():
    """Check the content of each module file"""
    module_files = [
        'modules/core.py',
        'modules/daily_books.py', 
        'modules/daily_capture.py',
        'modules/webhook_handlers.py'
    ]
    
    for module_file in module_files:
        print(f"\n{'='*50}")
        print(f"📄 {module_file}")
        print(f"{'='*50}")
        
        if not os.path.exists(module_file):
            print("❌ File does not exist")
            continue
            
        try:
            with open(module_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(module_file, 'r', encoding='latin1') as f:
                    content = f.read()
            except Exception as e:
                print(f"❌ Could not read file: {e}")
                continue
        
        # Check file size
        print(f"📏 Size: {len(content)} characters")
        
        # Check if it's a placeholder
        if 'placeholder' in content.lower():
            print("⚠️  This appears to be a placeholder file")
        
        # Show first few lines
        lines = content.split('\n')
        print(f"📝 First 10 lines:")
        for i, line in enumerate(lines[:10], 1):
            print(f"   {i:2}: {line}")
        
        # Check for key classes/functions
        if 'class ' in content:
            classes = [line.strip() for line in lines if line.strip().startswith('class ')]
            print(f"🏗️  Classes found: {len(classes)}")
            for cls in classes[:5]:  # Show first 5
                print(f"   - {cls}")
        
        if 'def ' in content:
            functions = [line.strip() for line in lines if line.strip().startswith('def ')]
            print(f"⚙️  Functions found: {len(functions)}")
            for func in functions[:5]:  # Show first 5
                print(f"   - {func}")

if __name__ == '__main__':
    check_module_content()