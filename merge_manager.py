#!/usr/bin/env python3
"""
Merge Manager - Automated Branch Testing and Merging Tool

Usage:
    python merge_manager.py <branch_name>
    python merge_manager.py --status
    python merge_manager.py --list-branches
    python merge_manager.py --help

This tool automates the process of:
1. Creating/switching to test branch
2. Merging feature branch into test branch
3. Running comprehensive test suite
4. Merging to main if tests pass
5. Restarting the server
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

class Colors:
    """Terminal colors for better output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class MergeManager:
    def __init__(self):
        self.project_root = Path.cwd()
        self.test_log_file = self.project_root / "tests" / "logs" / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        dirs = [
            self.project_root / "tests",
            self.project_root / "tests" / "logs",
            self.project_root / "tests" / "unit",
            self.project_root / "tests" / "integration",
            self.project_root / "tests" / "fixtures"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(exist_ok=True)
    
    def log_and_print(self, message, color=Colors.OKBLUE):
        """Log message and print with color"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        # Print with color
        print(f"{color}{message}{Colors.ENDC}")
        
        # Log to file with UTF-8 encoding
        with open(self.test_log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + "\n")
    
    def run_command(self, command, check=True, capture_output=False):
        """Run shell command with error handling"""
        self.log_and_print(f"Running: {command}", Colors.OKCYAN)
        
        try:
            if capture_output:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    check=check, 
                    capture_output=True, 
                    text=True,
                    cwd=self.project_root
                )
                return result.stdout.strip()
            else:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    check=check, 
                    cwd=self.project_root
                )
                return result.returncode == 0
        except subprocess.CalledProcessError as e:
            self.log_and_print(f"Command failed: {e}", Colors.FAIL)
            if capture_output and e.stdout:
                self.log_and_print(f"STDOUT: {e.stdout}", Colors.WARNING)
            if capture_output and e.stderr:
                self.log_and_print(f"STDERR: {e.stderr}", Colors.FAIL)
            return False
    
    def check_git_status(self):
        """Check if we're in a git repository and working directory is clean"""
        if not (self.project_root / ".git").exists():
            self.log_and_print("Not a git repository! Please initialize git first.", Colors.FAIL)
            return False
        
        # Check for uncommitted changes
        status = self.run_command("git status --porcelain", capture_output=True)
        if status and status.strip():
            self.log_and_print("Working directory has uncommitted changes:", Colors.WARNING)
            self.run_command("git status")
            response = input("Continue anyway? [y/N]: ").lower().strip()
            if response != 'y':
                return False
        
        return True
    
    def get_current_branch(self):
        """Get current git branch"""
        return self.run_command("git branch --show-current", capture_output=True)
    
    def branch_exists(self, branch_name):
        """Check if branch exists locally or remotely - simple and reliable"""
        branches = self.run_command("git branch -a", capture_output=True)
        if not branches:
            return False
        
        # Simple substring search - debug shows this works
        return branch_name in branches
    
    def create_test_branch(self):
        """Create or switch to test branch"""
        self.log_and_print("Setting up test branch...", Colors.HEADER)
        
        # Always recreate test branch fresh from main to avoid conflicts
        self.log_and_print("Creating fresh test branch from main")
        self.run_command("git checkout main")
        
        # Delete existing test branch if it exists
        existing_test = self.run_command("git branch | grep -w test", capture_output=True)
        if existing_test.strip():
            self.run_command("git branch -D test")
        
        # Create new test branch
        self.run_command("git checkout -b test")
        
        return True
    
    def merge_feature_to_test(self, feature_branch):
        """Merge feature branch into test branch"""
        self.log_and_print(f"Merging {feature_branch} into test branch...", Colors.HEADER)
        
        # Check if branch exists (including remote branches)
        if not self.branch_exists(feature_branch):
            self.log_and_print(f"Feature branch '{feature_branch}' does not exist!", Colors.FAIL)
            self.log_and_print("Available branches:", Colors.OKBLUE)
            self.run_command("git branch -a")
            return False
        
        # Make sure we can access the feature branch - fetch if it's remote
        branches_output = self.run_command("git branch -a", capture_output=True)
        self.log_and_print(f"Debug: Available branches: {branches_output}", Colors.OKCYAN)
        
        if f"remotes/origin/{feature_branch}" in branches_output and feature_branch not in branches_output:
            self.log_and_print(f"Checking out remote branch: {feature_branch}")
            checkout_result = self.run_command(f"git checkout -b {feature_branch} origin/{feature_branch}")
            if not checkout_result:
                self.log_and_print("Failed to checkout remote branch", Colors.FAIL)
                return False
            # Switch back to test branch
            self.run_command("git checkout test")
        
        # Debug: Check current branch and working directory
        current_branch = self.run_command("git branch --show-current", capture_output=True)
        self.log_and_print(f"Debug: Current branch: {current_branch}", Colors.OKCYAN)
        
        # Check if target branch exists from current location
        branch_check = self.run_command(f"git show-ref --verify --quiet refs/heads/{feature_branch}")
        self.log_and_print(f"Debug: Branch ref check result: {branch_check}", Colors.OKCYAN)
        
        # Merge feature branch using array format to avoid shell parsing issues
        merge_cmd = ["git", "merge", feature_branch, "--no-ff", "-m", f"Test merge: {feature_branch}"]
        try:
            result = subprocess.run(
                merge_cmd,
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            self.log_and_print(f"Git merge output: {result.stdout}", Colors.OKCYAN)
        except subprocess.CalledProcessError as e:
            self.log_and_print(f"Merge failed with error: {e}", Colors.FAIL)
            self.log_and_print(f"Error output: {e.stderr}", Colors.FAIL)
            self.log_and_print("Merge failed! Please resolve conflicts manually.", Colors.FAIL)
            return False
        
        self.log_and_print(f"Successfully merged {feature_branch} into test branch", Colors.OKGREEN)
        return True
    
    def run_test_suite(self):
        """Run comprehensive test suite"""
        self.log_and_print("Running comprehensive test suite...", Colors.HEADER)
        
        # Test phases with different types of tests
        test_phases = [
            {
                "name": "Structure Validation",
                "command": "python check_structure.py",
                "critical": True
            },
            {
                "name": "Unit Tests",
                "command": "python -m pytest tests/unit/ -v",
                "critical": True
            },
            {
                "name": "Core Functionality Tests",
                "command": "python test_core_functionality.py",
                "critical": True
            },
            {
                "name": "Enhanced Processing Tests",
                "command": "python test_enhanced_processing.py",
                "critical": True
            },
            {
                "name": "Integration Tests",
                "command": "python test_full_integration.py",
                "critical": False  # Don't fail merge if integration tests fail
            },
            {
                "name": "Notion Integration Tests", 
                "command": "python test_notion.py",
                "critical": False
            }
        ]
        
        failed_tests = []
        critical_failure = False
        
        for phase in test_phases:
            self.log_and_print(f"\n--- Running {phase['name']} ---", Colors.BOLD)
            
            # Run the test
            result = self.run_command(phase['command'])
            
            if result:
                self.log_and_print(f"✅ {phase['name']} passed", Colors.OKGREEN)
            else:
                self.log_and_print(f"❌ {phase['name']} failed", Colors.FAIL)
                failed_tests.append(phase['name'])
                if phase['critical']:
                    critical_failure = True
        
        # Test summary
        self.log_and_print(f"\n--- Test Suite Summary ---", Colors.BOLD)
        if failed_tests:
            self.log_and_print(f"Failed tests: {', '.join(failed_tests)}", Colors.WARNING)
        
        if critical_failure:
            self.log_and_print("Critical tests failed! Merge blocked.", Colors.FAIL)
            return False
        elif failed_tests:
            self.log_and_print("Some non-critical tests failed, but merge can proceed.", Colors.WARNING)
            response = input("Continue with merge? [y/N]: ").lower().strip()
            if response != 'y':
                return False
        
        self.log_and_print("All critical tests passed!", Colors.OKGREEN)
        return True
    
    def merge_to_main(self, feature_branch):
        """Merge test branch to main"""
        self.log_and_print("Merging to main branch...", Colors.HEADER)
        
        # Switch to main
        self.run_command("git checkout main")
        
        # Merge test branch
        merge_message = f"Merge feature: {feature_branch} (tested)"
        result = self.run_command(f"git merge test --no-ff -m '{merge_message}'")
        
        if not result:
            self.log_and_print("Merge to main failed!", Colors.FAIL)
            return False
        
        self.log_and_print("Successfully merged to main!", Colors.OKGREEN)
        return True
    
    def restart_server(self):
        """Restart the application server"""
        self.log_and_print("Restarting server...", Colors.HEADER)
        
        # Try different restart methods based on deployment
        restart_methods = [
            # Systemd service (most common for Linux deployments)
            "sudo systemctl restart automation-hub",
            # PM2 (Node.js process manager, sometimes used for Python apps)
            "pm2 restart automation-hub",
            # Docker container restart
            "docker restart automation-hub",
            # Kill existing Python process and restart (fallback)
            "pkill -f 'python.*app.py' && nohup python app.py > server.log 2>&1 &"
        ]
        
        for method in restart_methods:
            self.log_and_print(f"Trying: {method}")
            result = self.run_command(method)
            if result:
                self.log_and_print("Server restart successful!", Colors.OKGREEN)
                return True
        
        self.log_and_print("Could not restart server automatically.", Colors.WARNING)
        self.log_and_print("Please restart manually with: python app.py", Colors.WARNING)
        return False
    
    def cleanup_test_branch(self, feature_branch):
        """Clean up after successful merge"""
        self.log_and_print("Cleaning up...", Colors.HEADER)
        
        # Delete the feature branch if requested
        response = input(f"Delete feature branch '{feature_branch}'? [y/N]: ").lower().strip()
        if response == 'y':
            self.run_command(f"git branch -d {feature_branch}")
            self.log_and_print(f"Deleted feature branch: {feature_branch}", Colors.OKGREEN)
        
        self.log_and_print(f"Test logs saved to: {self.test_log_file}", Colors.OKCYAN)
    
    def list_branches(self):
        """List all available branches"""
        self.log_and_print("Available branches:", Colors.HEADER)
        self.run_command("git branch -a")
    
    def show_status(self):
        """Show current git and project status"""
        self.log_and_print("Current Status:", Colors.HEADER)
        current_branch = self.get_current_branch()
        self.log_and_print(f"Current branch: {current_branch}", Colors.OKBLUE)
        self.run_command("git status")
        
        # Show recent commits
        self.log_and_print("\nRecent commits:", Colors.HEADER)
        self.run_command("git log --oneline -10")
    
    def merge_workflow(self, feature_branch):
        """Main merge workflow"""
        self.log_and_print(f"Starting merge workflow for: {feature_branch}", Colors.HEADER)
        
        # Pre-flight checks
        if not self.check_git_status():
            return False
        
        try:
            # Step 1: Create/switch to test branch
            if not self.create_test_branch():
                return False
            
            # Step 2: Merge feature branch to test
            if not self.merge_feature_to_test(feature_branch):
                return False
            
            # Step 3: Run tests
            if not self.run_test_suite():
                self.log_and_print("Tests failed. Merge aborted.", Colors.FAIL)
                return False
            
            # Step 4: Merge to main
            if not self.merge_to_main(feature_branch):
                return False
            
            # Step 5: Restart server
            self.restart_server()
            
            # Step 6: Cleanup
            self.cleanup_test_branch(feature_branch)
            
            self.log_and_print(f"Successfully merged {feature_branch} to main!", Colors.OKGREEN)
            return True
            
        except KeyboardInterrupt:
            self.log_and_print("\nMerge workflow interrupted by user.", Colors.WARNING)
            return False
        except Exception as e:
            self.log_and_print(f"Unexpected error: {e}", Colors.FAIL)
            return False

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print(f"""
{Colors.HEADER}Merge Manager - Automated Testing and Merging{Colors.ENDC}

Usage:
    {Colors.OKBLUE}python merge_manager.py <branch_name>{Colors.ENDC}     # Merge branch after testing
    {Colors.OKBLUE}python merge_manager.py --status{Colors.ENDC}         # Show current status  
    {Colors.OKBLUE}python merge_manager.py --list-branches{Colors.ENDC}  # List all branches
    {Colors.OKBLUE}python merge_manager.py --help{Colors.ENDC}           # Show this help

Examples:
    {Colors.OKCYAN}python merge_manager.py feature/new-notification-system{Colors.ENDC}
    {Colors.OKCYAN}python merge_manager.py bugfix/fix-eod-processing{Colors.ENDC}
        """)
        sys.exit(1)
    
    manager = MergeManager()
    
    if sys.argv[1] == "--help":
        main()  # Show help
    elif sys.argv[1] == "--status":
        manager.show_status()
    elif sys.argv[1] == "--list-branches":
        manager.list_branches()
    else:
        feature_branch = sys.argv[1]
        success = manager.merge_workflow(feature_branch)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()