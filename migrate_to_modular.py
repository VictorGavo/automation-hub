#!/usr/bin/env python3
"""
Migration Script for Modular Restructure
Helps safely transition from monolithic app.py to modular structure
"""

import os
import shutil
import sys
from datetime import datetime

class ModularMigration:
    """Handles the migration to modular structure"""
    
    def __init__(self):
        self.backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.modules_created = []
        self.files_backed_up = []
    
    def create_backup(self):
        """Create backup of current app.py"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        # Backup current app.py
        if os.path.exists('app.py'):
            backup_path = os.path.join(self.backup_dir, 'app.py.backup')
            shutil.copy2('app.py', backup_path)
            self.files_backed_up.append('app.py')
            print(f"✅ Backed up app.py to {backup_path}")
        
        # Backup any existing modules directory
        if os.path.exists('modules'):
            backup_modules_path = os.path.join(self.backup_dir, 'modules_old')
            shutil.copytree('modules', backup_modules_path)
            self.files_backed_up.append('modules/')
            print(f"✅ Backed up existing modules/ to {backup_modules_path}")
        
        return True
    
    def create_modules_structure(self):
        """Create the modules directory structure"""
        # Create modules directory
        modules_dir = "modules"
        if not os.path.exists(modules_dir):
            os.makedirs(modules_dir)
            print(f"✅ Created {modules_dir}/ directory")
        
        # Create __init__.py
        init_file = os.path.join(modules_dir, "__init__.py")
        with open(init_file, 'w') as f:
            f.write('"""Automation Hub Modules Package"""\n')
        self.modules_created.append(init_file)
        print(f"✅ Created {init_file}")
        
        # Create placeholder module files (will be replaced by artifacts)
        module_files = [
            ("core.py", "Core Module - Shared utilities and dependencies"),
            ("daily_books.py", "Daily Books Module - SOD and EOD form processing"),
            ("daily_capture.py", "Daily Capture Module - Notion integration and markdown"),
            ("webhook_handlers.py", "Webhook Handlers Module - Clean webhook routing")
        ]
        
        for module_file, description in module_files:
            module_path = os.path.join(modules_dir, module_file)
            with open(module_path, 'w') as f:
                f.write(f'"""{description}"""\n\n# This file will be replaced by the modular implementation\n')
            self.modules_created.append(module_path)
            print(f"✅ Created placeholder {module_path}")
        
        return True
    
    def validate_dependencies(self):
        """Validate that all required dependencies are available"""
        required_files = [
            'config.py',
            'database.py', 
            'markdown_generator.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing required files: {', '.join(missing_files)}")
            return False
        
        print("✅ All required dependencies found")
        return True
    
    def check_imports(self):
        """Check if optional imports will work"""
        optional_imports = [
            ('notion_manager', 'NotionManager'),
            ('obsidian_goal_manager', 'ObsidianGoalManager'),
            ('file_system', 'FileSystemDriveManager')
        ]
        
        available_imports = []
        missing_imports = []
        
        for module_name, class_name in optional_imports:
            try:
                module = __import__(module_name)
                if hasattr(module, class_name):
                    available_imports.append(f"{module_name}.{class_name}")
                else:
                    missing_imports.append(f"{module_name}.{class_name}")
            except ImportError:
                missing_imports.append(f"{module_name}.{class_name}")
        
        if available_imports:
            print(f"✅ Available optional imports: {', '.join(available_imports)}")
        
        if missing_imports:
            print(f"⚠️ Missing optional imports: {', '.join(missing_imports)}")
            print("   (These features will be disabled but won't cause errors)")
        
        return True
    
    def run_migration(self):
        """Run the complete migration process"""
        print("🔄 Starting modular migration...")
        print("=" * 50)
        
        # Step 1: Validate dependencies
        if not self.validate_dependencies():
            print("❌ Migration failed: Missing dependencies")
            return False
        
        # Step 2: Check imports
        self.check_imports()
        
        # Step 3: Create backup
        print("\n📦 Creating backup...")
        if not self.create_backup():
            print("❌ Migration failed: Could not create backup")
            return False
        
        # Step 4: Create modules structure
        print("\n🏗️ Creating modules structure...")
        if not self.create_modules_structure():
            print("❌ Migration failed: Could not create modules")
            return False
        
        print("\n🎉 Migration setup complete!")
        print("=" * 50)
        print("NEXT STEPS:")
        print("1. Replace placeholder module files with actual implementations")
        print("2. Replace app.py with the new modular version")
        print("3. Test the new structure with: python test_modular_structure.py")
        print("4. Run your existing tests to ensure compatibility")
        print(f"\nBackup created in: {self.backup_dir}/")
        print("You can rollback by copying files from backup if needed.")
        
        return True

def main():
    """Main migration function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
Modular Migration Script

This script helps migrate from the monolithic app.py to a modular structure.

Usage:
    python migrate_to_modular.py

What it does:
1. Creates backup of current app.py
2. Creates modules/ directory structure
3. Creates placeholder module files
4. Validates dependencies

After running this script, you'll need to:
1. Copy the modular implementations into the module files
2. Replace app.py with the new streamlined version
3. Test the new structure
        """)
        return
    
    migration = ModularMigration()
    success = migration.run_migration()
    
    if not success:
        print("\n💥 Migration failed. Check errors above.")
        sys.exit(1)
    else:
        print("\n✅ Migration setup successful!")
        sys.exit(0)

if __name__ == '__main__':
    main()