# Test Suite for Sunrise School Management System

This directory contains the comprehensive test suite for the FastAPI backend of the Sunrise School Management System.

## Directory Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared pytest fixtures and configuration
├── run_tests.py               # Test runner script
├── README.md                  # This file
├── api/                       # API endpoint tests
│   ├── __init__.py
│   ├── auth/                  # Authentication tests
│   │   ├── __init__.py
│   │   └── test_authentication.py
│   └── teachers/              # Teacher management tests
│       ├── __init__.py
│       ├── test_endpoints.py
│       └── test_profile.py
├── unit/                      # Unit tests
│   ├── __init__.py
│   └── crud/                  # CRUD operation tests
│       ├── __init__.py
│       └── test_date_conversion.py
├── integration/               # Integration tests
│   ├── __init__.py
│   └── test_teacher_profile_workflow.py
└── fixtures/                  # Test data and fixtures
    ├── __init__.py
    └── sample_data.py
```

## Test Categories

### API Tests (`tests/api/`)
Tests for API endpoints, organized by functionality:
- **Authentication** (`auth/`): Login, logout, token validation
- **Teachers** (`teachers/`): Teacher management endpoints
- **Students** (`students/`): Student management endpoints (to be added)
- **Configuration** (`configuration/`): Configuration endpoints (to be added)

### Unit Tests (`tests/unit/`)
Tests for individual components:
- **CRUD** (`crud/`): Database operation tests
- **Models** (`models/`): Model validation tests (to be added)
- **Services** (`services/`): Service layer tests (to be added)
- **Utils** (`utils/`): Utility function tests (to be added)

### Integration Tests (`tests/integration/`)
End-to-end workflow tests:
- **Teacher Profile Workflow**: Complete login-to-profile-update workflow
- **Database Integration**: Database operation integration tests (to be added)

### Fixtures (`tests/fixtures/`)
Reusable test data and fixtures:
- **Sample Data**: Predefined test data objects
- **Factories**: Data generation utilities (to be added)
- **Mock Data**: Mock responses and objects (to be added)

## Running Tests

### Using the Test Runner Script

The easiest way to run tests is using the provided test runner:

```bash
# Run all tests
python tests/run_tests.py

# Run specific test types
python tests/run_tests.py --type api
python tests/run_tests.py --type unit
python tests/run_tests.py --type integration

# Run tests with coverage
python tests/run_tests.py --coverage

# Run tests in parallel
python tests/run_tests.py --parallel 4

# Skip slow tests
python tests/run_tests.py --fast

# Run specific module
python tests/run_tests.py --module api/teachers/test_profile.py

# Run specific function
python tests/run_tests.py --function test_get_my_profile_success
```

### Using pytest Directly

You can also run tests directly with pytest:

```bash
# Run all tests
pytest tests/

# Run specific test types using markers
pytest -m api
pytest -m unit
pytest -m integration
pytest -m auth
pytest -m profile
pytest -m crud

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/api/teachers/test_profile.py

# Run specific test function
pytest tests/api/teachers/test_profile.py::TestTeacherProfile::test_get_my_profile_success

# Run tests matching a pattern
pytest -k "profile"

# Skip slow tests
pytest -m "not slow"
```

## Test Markers

The test suite uses pytest markers to categorize tests:

- `@pytest.mark.api`: API endpoint tests
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.auth`: Authentication-related tests
- `@pytest.mark.profile`: Profile-related tests
- `@pytest.mark.crud`: CRUD operation tests
- `@pytest.mark.slow`: Tests that take longer to run

## Test Configuration

### pytest.ini
The main pytest configuration is in `pytest.ini` at the project root:
- Test discovery patterns
- Default markers
- Coverage settings
- Output formatting

### conftest.py
Shared fixtures and configuration:
- Database setup and teardown
- Test client creation
- Authentication helpers
- Sample data fixtures

## Writing New Tests

### Test File Naming
- Test files should be named `test_*.py` or `*_test.py`
- Place tests in the appropriate subdirectory based on functionality
- Use descriptive names that indicate what is being tested

### Test Class Organization
```python
@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.profile
class TestTeacherProfile:
    """Test class for teacher profile endpoints."""
    
    async def test_get_profile_success(self, async_client, auth_headers):
        """Test successful profile retrieval."""
        # Test implementation
```

### Using Fixtures
```python
async def test_example(
    self, 
    async_client: AsyncClient,
    auth_headers: dict,
    sample_teacher_data: dict
):
    """Example test using fixtures."""
    response = await async_client.post(
        "/api/v1/teachers/",
        json=sample_teacher_data,
        headers=auth_headers
    )
    assert response.status_code == 201
```

### Test Data
Use the fixtures in `tests/fixtures/sample_data.py` for consistent test data:
```python
from tests.fixtures.sample_data import SampleData

def test_example():
    teacher_data = SampleData.teacher_data()
    # Use teacher_data in test
```

## Best Practices

1. **Test Organization**: Group related tests in classes and modules
2. **Descriptive Names**: Use clear, descriptive test and function names
3. **Fixtures**: Use fixtures for common setup and test data
4. **Markers**: Apply appropriate markers to categorize tests
5. **Assertions**: Use specific assertions with clear error messages
6. **Documentation**: Document complex test scenarios
7. **Independence**: Tests should be independent and not rely on each other
8. **Performance**: Mark slow tests with `@pytest.mark.slow`

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:
- All tests should pass before merging
- Coverage reports are generated automatically
- Different test types can be run in parallel
- Slow tests can be skipped for faster feedback

## Troubleshooting

### Common Issues

1. **Database Connection**: Ensure test database is available
2. **Authentication**: Check that test credentials are valid
3. **Dependencies**: Install all test dependencies from requirements.txt
4. **Environment**: Set appropriate environment variables

### Debug Mode
Run tests with verbose output for debugging:
```bash
pytest -v -s tests/path/to/test.py
```

### Coverage Reports
Generate detailed coverage reports:
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

Open `htmlcov/index.html` to view the detailed coverage report.

## Contributing

When adding new features:
1. Write tests for new functionality
2. Update existing tests if behavior changes
3. Ensure all tests pass
4. Maintain good test coverage (aim for >80%)
5. Follow the established patterns and conventions
