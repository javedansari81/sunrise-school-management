#!/usr/bin/env python3
"""
Test runner script for the FastAPI application
"""
import asyncio
import sys
import subprocess
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))


def run_tests():
    """Run all tests"""
    print("🧪 Running FastAPI tests...")
    
    try:
        # Run pytest with coverage
        result = subprocess.run([
            "python", "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ], check=True, capture_output=True, text=True)
        
        print("✅ All tests passed!")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print("❌ Tests failed!")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest pytest-cov")
        sys.exit(1)


def run_auth_tests_only():
    """Run only authentication tests"""
    print("🔐 Running authentication tests...")
    
    try:
        result = subprocess.run([
            "python", "-m", "pytest",
            "tests/test_auth.py",
            "-v",
            "--tb=short"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Authentication tests passed!")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print("❌ Authentication tests failed!")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)


def run_linting():
    """Run code linting"""
    print("🔍 Running code linting...")
    
    try:
        # Run flake8 for linting
        result = subprocess.run([
            "python", "-m", "flake8",
            "app/",
            "--max-line-length=100",
            "--ignore=E203,W503"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Code linting passed!")
        
    except subprocess.CalledProcessError as e:
        print("❌ Code linting failed!")
        print(e.stdout)
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("⚠️  flake8 not found. Skipping linting.")
        return True
    
    return True


def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "auth":
            run_auth_tests_only()
        elif sys.argv[1] == "lint":
            run_linting()
        elif sys.argv[1] == "all":
            if run_linting():
                run_tests()
        else:
            print("Usage: python run_tests.py [auth|lint|all]")
            sys.exit(1)
    else:
        run_tests()


if __name__ == "__main__":
    main()
