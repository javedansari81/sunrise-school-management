# Backend Unit Tests

This directory contains unit tests for the Sunrise School Management System backend, using pytest for comprehensive testing of individual components, models, and business logic.

## 📋 Available Test Files

### Core Tests
- **`conftest.py`** - Test configuration, fixtures, and shared utilities
- **`test_auth.py`** - Authentication and authorization testing
- **`test_main.py`** - Main application and core functionality tests
- **`test_users.py`** - User management and profile testing

### Feature Tests
- **`test_fees.py`** - Fee management system testing
- **`test_leave_management.py`** - Leave request and approval testing
- **`test_expense_management.py`** - Expense tracking and management testing

## 🚀 Running Unit Tests

### Run All Unit Tests
```bash
cd sunrise-backend-fastapi
python -m pytest ../tests/backend/unit/ -v
```

### Run Specific Test Files
```bash
# Authentication tests only
python -m pytest ../tests/backend/unit/test_auth.py -v

# Fee management tests only
python -m pytest ../tests/backend/unit/test_fees.py -v

# Leave management tests only
python -m pytest ../tests/backend/unit/test_leave_management.py -v
```

### Run Tests with Coverage
```bash
# Generate coverage report
python -m pytest ../tests/backend/unit/ --cov=app --cov-report=html

# View coverage in browser
# Open htmlcov/index.html in your browser
```

### Run Tests with Specific Markers
```bash
# Run only fast tests
python -m pytest ../tests/backend/unit/ -m "not slow"

# Run only database tests
python -m pytest ../tests/backend/unit/ -m "database"

# Run only API tests
python -m pytest ../tests/backend/unit/ -m "api"
```

## 🧪 Test Categories

### Authentication Tests (`test_auth.py`)
- **User Registration**: Account creation and validation
- **Login/Logout**: Authentication flow testing
- **Token Management**: JWT token creation and validation
- **Password Security**: Hashing and verification
- **Role-Based Access**: Permission and authorization testing

### User Management Tests (`test_users.py`)
- **User CRUD Operations**: Create, read, update, delete users
- **Profile Management**: User profile updates and validation
- **User Types**: Admin, teacher, student role testing
- **Data Validation**: Input validation and error handling

### Fee Management Tests (`test_fees.py`)
- **Fee Structure**: Fee creation and management
- **Payment Processing**: Payment recording and validation
- **Balance Calculations**: Outstanding balance computations
- **Payment Methods**: Multiple payment method support
- **Monthly Tracking**: Month-wise payment tracking

### Leave Management Tests (`test_leave_management.py`)
- **Leave Requests**: Leave request creation and validation
- **Approval Workflow**: Leave approval and rejection processes
- **Leave Types**: Different leave type handling
- **Date Validation**: Leave date range validation
- **Business Rules**: Leave policy enforcement

### Expense Management Tests (`test_expense_management.py`)
- **Expense Creation**: Expense record creation and validation
- **Categorization**: Expense category management
- **Soft Delete**: Logical deletion functionality
- **Statistics**: Expense reporting and analytics
- **Vendor Management**: Vendor tracking and management

## 🔧 Test Configuration

### Test Database
Unit tests use an in-memory SQLite database for fast, isolated testing:
```python
# In conftest.py
@pytest.fixture
def test_db():
    # Creates temporary test database
    # Automatically cleaned up after tests
```

### Test Fixtures
Common fixtures available in all tests:
- **`test_db`** - Clean test database session
- **`test_client`** - FastAPI test client
- **`test_user`** - Sample user for testing
- **`auth_headers`** - Authentication headers for API calls

### Test Data
Test data is created using factory functions:
```python
def create_test_user(db, **kwargs):
    """Create a test user with default or custom attributes"""
    
def create_test_student(db, **kwargs):
    """Create a test student with default or custom attributes"""
```

## 📊 Test Patterns

### Database Testing Pattern
```python
def test_create_user(test_db):
    # Arrange
    user_data = {"email": "test@example.com", "password": "password123"}
    
    # Act
    user = create_user(test_db, user_data)
    
    # Assert
    assert user.email == "test@example.com"
    assert user.id is not None
```

### API Testing Pattern
```python
def test_login_endpoint(test_client):
    # Arrange
    login_data = {"username": "admin@example.com", "password": "admin123"}
    
    # Act
    response = test_client.post("/api/v1/auth/login", data=login_data)
    
    # Assert
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### Error Testing Pattern
```python
def test_invalid_login(test_client):
    # Arrange
    invalid_data = {"username": "wrong@example.com", "password": "wrong"}
    
    # Act
    response = test_client.post("/api/v1/auth/login", data=invalid_data)
    
    # Assert
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]
```

## 🚨 Common Issues

### Import Errors
```bash
# Ensure you're in the correct directory
cd sunrise-backend-fastapi

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Database Connection Issues
```bash
# Check if test database is properly configured
# Verify conftest.py database fixture setup
```

### Authentication Issues
```bash
# Verify test user credentials
# Check JWT token configuration in tests
```

## 📈 Coverage Goals

### Target Coverage
- **Overall**: 90%+ code coverage
- **Models**: 95%+ coverage
- **API Endpoints**: 95%+ coverage
- **Business Logic**: 90%+ coverage
- **Utilities**: 85%+ coverage

### Coverage Reports
```bash
# Generate detailed coverage report
python -m pytest ../tests/backend/unit/ --cov=app --cov-report=term-missing

# Generate HTML coverage report
python -m pytest ../tests/backend/unit/ --cov=app --cov-report=html
```

## 🔗 Related Testing

- **Integration Tests**: [../integration/](../integration/)
- **API Tests**: [../api/](../api/)
- **Validation Tests**: [../validation/](../validation/)
- **Test Utilities**: [../utilities/](../utilities/)

## 📞 Support

### Debugging Tests
1. **Use pytest verbose mode**: `-v` flag for detailed output
2. **Use pytest debug mode**: `--pdb` flag to drop into debugger on failure
3. **Check test logs**: Review test output for error details
4. **Isolate failing tests**: Run individual test files or functions

### Writing New Tests
1. **Follow existing patterns** in the test files
2. **Use descriptive test names** that explain what is being tested
3. **Include both positive and negative test cases**
4. **Mock external dependencies** for isolated testing
5. **Clean up test data** using fixtures and teardown methods
