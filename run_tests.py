#!/usr/bin/env python3
"""
Test runner for automation hub
"""
import subprocess
import sys
import os


def run_test(test_file):
    """Run a single test file and return success status"""
    print(f"\n{'='*60}")
    print(f"Running {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=False, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False


def main():
    """Run all test files"""
    # Core tests - always run these
    core_tests = [
        'test_core_functionality.py',
        'test_vault_path.py'
    ]
    
    # Integration tests - more comprehensive
    integration_tests = [
        'test_eod_webhook.py',
        'test_drive_integration.py', 
        'test_notion.py',
        'test_obsidian_goals.py',
        'test_full_integration.py'
    ]
    
    if len(sys.argv) > 1 and sys.argv[1] == '--core':
        tests_to_run = core_tests
        print("Running core tests only...")
    else:
        tests_to_run = core_tests + integration_tests
        print("Running all tests...")
    
    results = []
    for test_file in tests_to_run:
        if os.path.exists(test_file):
            results.append(run_test(test_file))
        else:
            print(f"⚠️  Test file not found: {test_file}")
            results.append(False)
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = sum(results)
    total = len(results)
    
    for i, test in enumerate(tests_to_run):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{status} {test}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
