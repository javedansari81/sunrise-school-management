#!/usr/bin/env python3
"""
Test runner script for the Sunrise School Management System.

This script provides convenient ways to run different types of tests:
- All tests
- API tests only
- Unit tests only
- Integration tests only
- Specific test modules or functions
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command: list, description: str) -> int:
    """Run a command and return the exit code."""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(command, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for Sunrise School Management System")
    parser.add_argument(
        "--type", 
        choices=["all", "api", "unit", "integration", "auth", "profile", "crud"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow tests"
    )
    parser.add_argument(
        "--parallel", "-n",
        type=int,
        help="Run tests in parallel (specify number of workers)"
    )
    parser.add_argument(
        "--module", "-m",
        help="Run specific test module"
    )
    parser.add_argument(
        "--function", "-f",
        help="Run specific test function"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test path based on type
    if args.type == "all":
        cmd.append("tests/")
    elif args.type == "api":
        cmd.append("tests/api/")
    elif args.type == "unit":
        cmd.append("tests/unit/")
    elif args.type == "integration":
        cmd.append("tests/integration/")
    elif args.type == "auth":
        cmd.extend(["-m", "auth"])
    elif args.type == "profile":
        cmd.extend(["-m", "profile"])
    elif args.type == "crud":
        cmd.extend(["-m", "crud"])
    
    # Add specific module or function
    if args.module:
        cmd.append(f"tests/{args.module}")
    
    if args.function:
        cmd.extend(["-k", args.function])
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term-missing"])
    
    # Add verbose mode
    if args.verbose:
        cmd.append("-v")
    
    # Skip slow tests if requested
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add other useful options
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    # Run the tests
    description = f"Running {args.type} tests"
    if args.module:
        description += f" for module {args.module}"
    if args.function:
        description += f" for function {args.function}"
    
    exit_code = run_command(cmd, description)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
