#!/usr/bin/env python3
"""
Convenient test runner for the Bible Verse application.
Provides different test running options and reporting.
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('=' * 60)
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Bible Verse Application Test Runner")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--api", action="store_true", help="Run API tests only")
    parser.add_argument("--gui", action="store_true", help="Run GUI tests only")
    parser.add_argument("--database", action="store_true", help="Run database tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--selection", action="store_true", help="Run selection algorithm tests only")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    
    args = parser.parse_args()
    
    # Change to project directory
    project_dir = Path(__file__).parent
    import os
    os.chdir(project_dir)
    
    # Build base command
    base_cmd = [sys.executable, "-m", "pytest"]
    
    if args.verbose:
        base_cmd.append("-v")
    
    if args.fast:
        base_cmd.extend(["-m", "not slow"])
    
    if args.coverage:
        base_cmd.extend(["--cov=app", "--cov=gui", "--cov-report=html", "--cov-report=term"])
    
    # Determine which tests to run
    if args.all or not any([args.api, args.gui, args.database, args.integration, args.selection]):
        # Run all tests
        success = run_command(base_cmd + ["tests/"], "All Tests")
    else:
        success = True
        
        if args.api:
            success &= run_command(base_cmd + ["tests/test_api.py"], "API Tests")
        
        if args.gui:
            success &= run_command(base_cmd + ["tests/test_gui.py"], "GUI Tests")
        
        if args.database:
            success &= run_command(base_cmd + ["tests/test_database.py"], "Database Tests")
        
        if args.integration:
            success &= run_command(base_cmd + ["tests/test_integration.py"], "Integration Tests")
        
        if args.selection:
            success &= run_command(base_cmd + ["tests/test_selection.py"], "Selection Algorithm Tests")
    
    # Final summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("\nApplication is ready for use:")
        print("  python launch.py")
    else:
        print("❌ SOME TESTS FAILED!")
        print("\nPlease check the output above for details.")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())