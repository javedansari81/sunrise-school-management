# Sunrise School Management System - Test Suite

This directory contains the complete test suite for the Sunrise School Management System, organized by test type and functionality for easy navigation and execution.

## 📁 Directory Structure

```
tests/
├── backend/                # Backend Python tests
│   ├── unit/              # Unit tests (pytest)
│   ├── integration/       # Integration tests
│   ├── api/               # API-specific tests
│   ├── validation/        # Validation and verification scripts
│   ├── utilities/         # Test utilities and helper scripts
│   └── README.md          # Backend testing guide
├── frontend/              # Frontend React tests
│   ├── contexts-tests/    # Context testing
│   ├── tests/             # Component tests
│   ├── leave-management/  # Feature-specific test documentation
│   └── README.md          # Frontend testing guide
├── scripts/               # Test automation scripts
│   ├── powershell/        # PowerShell API testing scripts
│   ├── web/               # Web-based test files (HTML/JS)
│   └── README.md          # Script testing guide
└── README.md              # This file
```

## 🎯 Test Categories

### 🔧 Backend Tests (`backend/`)
**Python-based testing for FastAPI backend:**

- **Unit Tests** - Individual component testing with pytest
- **Integration Tests** - End-to-end system testing
- **API Tests** - Specific API endpoint testing
- **Validation Tests** - Data validation and system verification
- **Utilities** - Test helpers, data creation, and debugging tools

### ⚛️ Frontend Tests (`frontend/`)
**React/TypeScript testing for frontend application:**

- **Component Tests** - Individual React component testing
- **Context Tests** - React context and state management testing
- **Feature Tests** - Feature-specific testing documentation
- **Integration Tests** - Frontend-backend integration testing

### 📜 Script Tests (`scripts/`)
**Automated testing scripts and utilities:**

- **PowerShell Scripts** - API endpoint testing via PowerShell
- **Web Scripts** - Browser-based testing (HTML/JavaScript)
- **Automation** - Test execution and validation scripts

## 🚀 Quick Start Testing

### Prerequisites
- **Backend**: Python 3.8+, FastAPI server running on `http://localhost:8000`
- **Frontend**: Node.js 16+, React development server on `http://localhost:3000`
- **Scripts**: PowerShell 5.0+ (Windows), Modern web browser

### Run All Backend Tests
```bash
cd sunrise-backend-fastapi
python scripts/run_tests.py
```

### Run All Frontend Tests
```bash
cd sunrise-school-frontend
npm test
```

### Run PowerShell API Tests
```powershell
cd tests/scripts/powershell/leave-management
.\test_api_request.ps1
```

## 🧪 Test Execution Workflows

### 1. Development Testing
**For active development and debugging:**
```bash
# Backend unit tests
cd sunrise-backend-fastapi
python -m pytest ../tests/backend/unit/ -v

# Frontend component tests
cd sunrise-school-frontend
npm test -- --watch

# API integration tests
python ../tests/backend/integration/test_simple_backend.py
```

### 2. Feature Testing
**For specific feature validation:**
```bash
# Test expense management
python ../tests/backend/integration/test_expense_system.py

# Test leave management
python ../tests/backend/integration/test_leave_system_integration.py

# Test authentication
python -m pytest ../tests/backend/unit/test_auth.py -v
```

### 3. Pre-Deployment Testing
**Complete system validation before deployment:**
```bash
# Run all backend tests
cd sunrise-backend-fastapi
python scripts/run_tests.py all

# Run all frontend tests
cd ../sunrise-school-frontend
npm test -- --coverage

# Validate system integration
cd ../tests/backend/validation
python validate_leave_system.py
python validate_metadata.py
```

### 4. Production Validation
**Post-deployment verification:**
```bash
# Test production endpoints
python ../tests/backend/validation/validate_backend_deployment.py

# PowerShell production tests
cd tests/scripts/powershell
# Update URLs to production in scripts, then run
.\test_api_request.ps1
```

## 📊 Test Coverage Goals

### Backend Coverage Targets
- **Unit Tests**: 90%+ code coverage
- **API Endpoints**: 95%+ endpoint coverage
- **Integration Tests**: All major workflows covered
- **Validation Tests**: All business rules verified

### Frontend Coverage Targets
- **Components**: 80%+ component coverage
- **Contexts**: 90%+ context coverage
- **Integration**: All user workflows covered
- **E2E Tests**: Critical paths validated

## 🔧 Test Configuration

### Backend Test Configuration
- **Test Database**: Separate test database or in-memory SQLite
- **Test Data**: Automated test data creation and cleanup
- **Mocking**: External service mocking for isolated testing
- **Fixtures**: Reusable test fixtures in `conftest.py`

### Frontend Test Configuration
- **Test Environment**: Jest with React Testing Library
- **Mocking**: API mocking with MSW (Mock Service Worker)
- **Test Data**: Mock data generators for components
- **Setup**: Test configuration in `setupTests.ts`

### Script Test Configuration
- **Authentication**: Test credentials for API access
- **Environment**: Configurable URLs for different environments
- **Error Handling**: Comprehensive error reporting
- **Logging**: Detailed test execution logs

## 🚨 Common Testing Issues

### Backend Testing Issues
- **Database Connection**: Ensure test database is accessible
- **Import Errors**: Check Python path and virtual environment
- **Authentication**: Verify test user credentials
- **Port Conflicts**: Ensure backend server is running on correct port

### Frontend Testing Issues
- **Node Modules**: Clear and reinstall if tests fail to run
- **API Mocking**: Verify mock service worker configuration
- **Component Rendering**: Check for missing providers or contexts
- **Async Testing**: Proper handling of async operations

### Script Testing Issues
- **PowerShell Execution Policy**: May need to set execution policy
- **Network Access**: Ensure backend server is accessible
- **Authentication Tokens**: Check token expiration and refresh
- **CORS Issues**: Verify CORS configuration for cross-origin requests

## 📈 Test Reporting

### Coverage Reports
```bash
# Backend coverage
cd sunrise-backend-fastapi
python -m pytest ../tests/backend/unit/ --cov=app --cov-report=html

# Frontend coverage
cd sunrise-school-frontend
npm test -- --coverage --watchAll=false
```

### Test Results
- **Unit Test Results**: Detailed pass/fail reports with timing
- **Integration Test Results**: End-to-end workflow validation
- **Coverage Reports**: HTML reports with line-by-line coverage
- **Performance Metrics**: Response time and load testing results

## 🔗 Related Documentation

- **Setup Guides**: [../docs/setup/](../docs/setup/)
- **Testing Documentation**: [../docs/testing/](../docs/testing/)
- **Feature Documentation**: [../docs/features/](../docs/features/)
- **Deployment Guides**: [../docs/deployment/](../docs/deployment/)

## 📞 Testing Support

### Getting Help
1. **Backend Issues**: Check [backend/README.md](./backend/README.md)
2. **Frontend Issues**: Check [frontend/README.md](./frontend/README.md)
3. **Script Issues**: Check [scripts/README.md](./scripts/README.md)
4. **General Testing**: Review [../docs/testing/](../docs/testing/)

### Best Practices
- **Run tests frequently** during development
- **Write tests first** for new features (TDD approach)
- **Keep tests isolated** and independent
- **Use descriptive test names** that explain what is being tested
- **Mock external dependencies** for reliable testing
- **Clean up test data** after test execution

### Contributing Tests
1. **Follow existing patterns** in the test suite
2. **Add tests for new features** and bug fixes
3. **Update documentation** when adding new test categories
4. **Ensure tests pass** before submitting changes
5. **Include both positive and negative test cases**
