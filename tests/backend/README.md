# API Tests

This directory contains all test files for the Sunrise School Management System backend API.

## Directory Structure

```
tests/backend/
├── unit/                   # Unit tests using pytest
│   ├── conftest.py        # Test configuration and fixtures
│   ├── test_auth.py       # Authentication tests
│   ├── test_fees.py       # Fee management tests
│   └── ...                # Other unit tests
├── integration/           # Integration test scripts
│   ├── test_expense_system.py           # Expense system integration tests
│   ├── test_leave_management_connection.py  # Leave management connection tests
│   ├── test_leave_system_integration.py     # Leave system integration tests
│   └── test_simple_backend.py              # Basic backend functionality tests
├── validation/            # Validation and verification scripts
│   ├── validate_expense_system.py      # Expense system validation
│   ├── validate_leave_frontend.py      # Leave frontend validation
│   └── test_leave_validation.py        # Leave validation tests
├── api/                   # API-specific test scripts
│   ├── test_trailing_slash_fix.py      # Trailing slash fix tests
│   ├── test_friendly_leave_request.py  # Friendly leave request tests
│   └── test_leave_request_fix.py       # Leave request fix tests
├── utilities/             # Test utilities and helper scripts
│   ├── debug_leaves_endpoints.py       # Debug utilities
│   └── ...                # Other utility scripts
└── README.md              # This file
```

## Running Tests

### Unit Tests (pytest)
```bash
cd sunrise-backend-fastapi
python scripts/run_tests.py
```

### Specific Test Categories
```bash
# Authentication tests only
python scripts/run_tests.py auth

# All tests with linting
python scripts/run_tests.py all

# Specific test file
python -m pytest ../tests/backend/unit/test_auth.py -v
```

### Integration Tests
```bash
# Expense system integration
python ../tests/backend/integration/test_expense_system.py

# Leave management connection
python ../tests/backend/integration/test_leave_management_connection.py

# Simple backend functionality
python ../tests/backend/integration/test_simple_backend.py
```

### Validation Scripts
```bash
# Validate expense system
python api-tests/validation/validate_expense_system.py

# Validate leave frontend
python api-tests/validation/validate_leave_frontend.py
```

### Deployment Tests
```bash
# Validate backend deployment
python api-tests/deployment/validate_backend_deployment.py
```

## Test Categories

### Unit Tests (`tests/`)
- **Authentication Tests** - User login, token validation, permissions
- **API Endpoint Tests** - CRUD operations for all entities
- **Database Tests** - Model validation and database operations
- **Business Logic Tests** - Validation rules and workflows

### Integration Tests (`integration/`)
- **System Integration** - End-to-end workflow testing
- **API Integration** - Cross-service communication testing
- **Database Integration** - Full database workflow testing

### Validation Tests (`validation/`)
- **System Validation** - Comprehensive system health checks
- **Data Validation** - Data integrity and consistency checks
- **Frontend Validation** - Frontend-backend integration validation

### Deployment Tests (`deployment/`)
- **Production Validation** - Live deployment health checks
- **Environment Testing** - Multi-environment compatibility
- **Performance Testing** - Load and stress testing

### Web Tests (`web-tests/`)
- **Browser Testing** - HTML/JavaScript based tests
- **UI Integration** - Frontend API integration tests
- **Manual Testing** - Interactive test interfaces

## Prerequisites

- Python 3.8+
- FastAPI backend server running
- Required Python packages: `pytest`, `httpx`, `aiohttp`, `requests`
- For deployment tests: Valid production URLs

## Configuration

Most test scripts use these default configurations:
- **Local Backend**: `http://localhost:8000`
- **Production Backend**: `https://sunrise-school-backend-api.onrender.com`
- **Test Credentials**: admin@sunriseschool.edu / admin123

Update URLs and credentials in individual test files as needed for your environment.
