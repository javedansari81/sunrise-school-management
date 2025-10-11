# Test Scripts

This directory contains automated testing scripts and utilities for the Sunrise School Management System, including PowerShell API tests and web-based testing tools.

## 📁 Directory Structure

```
tests/scripts/
├── powershell/            # PowerShell API testing scripts
│   ├── api-tests/         # General API testing scripts
│   ├── leave-management/  # Leave management specific tests
│   │   ├── test_api_request.ps1
│   │   └── test_detailed_error.ps1
│   ├── student-management/ # Student management specific tests
│   │   ├── test_student_exists.ps1
│   │   └── test_students.ps1
│   └── README.md          # PowerShell testing guide
├── web/                   # Web-based test files
│   ├── test_leave_api.html         # HTML test for leave API
│   ├── test_login.html             # HTML login test
│   └── test_leave_management_fix.js # JavaScript test for leave management
└── README.md              # This file
```

## 🚀 Running Script Tests

### PowerShell API Tests
```powershell
# Navigate to PowerShell test directory
cd tests/scripts/powershell

# Run leave management tests
cd leave-management
.\test_api_request.ps1
.\test_detailed_error.ps1

# Run student management tests
cd ../student-management
.\test_student_exists.ps1
.\test_students.ps1
```

### Web-Based Tests
```bash
# Open HTML test files in browser
# Navigate to tests/scripts/web/
# Open test_login.html in browser for interactive testing
# Open test_leave_api.html for API testing interface
```

### JavaScript Console Tests
```javascript
// Load test_leave_management_fix.js in browser console
// On the Leave Management page, run:
window.leaveManagementTest.runAllTests();
```

## 🧪 Test Categories

### PowerShell API Tests (`powershell/`)
**Automated API endpoint testing via PowerShell:**

#### Leave Management Tests
- **`test_api_request.ps1`** - Leave request creation API testing
  - Authentication flow validation
  - Leave request payload testing
  - Response validation and error handling
  - Token management and refresh

- **`test_detailed_error.ps1`** - Enhanced error handling testing
  - Detailed error response analysis
  - HTTP status code validation
  - Error message verification
  - Debug information collection

#### Student Management Tests
- **`test_student_exists.ps1`** - Student existence validation
  - Student ID verification
  - Database connectivity testing
  - Response format validation
  - Error handling for missing students

- **`test_students.ps1`** - Student listing API testing
  - Student data retrieval
  - Pagination testing
  - Filter parameter validation
  - Response data structure verification

### Web-Based Tests (`web/`)
**Browser-based interactive testing:**

#### HTML Test Interfaces
- **`test_login.html`** - Interactive login testing interface
  - Manual login form testing
  - Token storage validation
  - Session management testing
  - Cross-browser compatibility

- **`test_leave_api.html`** - Leave API testing interface
  - Interactive API endpoint testing
  - Request/response visualization
  - Parameter customization
  - Real-time API validation

#### JavaScript Test Scripts
- **`test_leave_management_fix.js`** - Leave management page testing
  - Page load validation
  - Component rendering verification
  - API call monitoring
  - Error state detection
  - Debug information collection

## 🔧 Test Configuration

### PowerShell Configuration
Default configuration for PowerShell tests:
```powershell
# API Base URL
$baseUrl = "http://localhost:8000"

# Test Credentials
$testEmail = "admin@sunrise.com"
$testPassword = "admin123"

# Request Headers
$headers = @{
    "Content-Type" = "application/json"
    "Accept" = "application/json"
}
```

### Web Test Configuration
Configuration for web-based tests:
```javascript
// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
const TEST_CREDENTIALS = {
    email: 'admin@sunrise.com',
    password: 'admin123'
};

// Test Settings
const TEST_CONFIG = {
    timeout: 5000,
    retries: 3,
    verbose: true
};
```

## 📊 Test Execution Patterns

### PowerShell API Test Pattern
```powershell
# 1. Authentication
$loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method POST -Body $loginData

# 2. Extract Token
$token = $loginResponse.access_token

# 3. API Call with Authentication
$headers["Authorization"] = "Bearer $token"
$response = Invoke-RestMethod -Uri "$apiUrl" -Method GET -Headers $headers

# 4. Validation
if ($response.status -eq "success") {
    Write-Host "✅ Test Passed" -ForegroundColor Green
} else {
    Write-Host "❌ Test Failed" -ForegroundColor Red
}
```

### JavaScript Test Pattern
```javascript
// 1. Setup Test Environment
console.log('🧪 Starting Test Suite');

// 2. Test Execution
async function runTest() {
    try {
        const result = await testFunction();
        console.log('✅ Test Passed:', result);
        return true;
    } catch (error) {
        console.log('❌ Test Failed:', error.message);
        return false;
    }
}

// 3. Results Summary
function summarizeResults(results) {
    const passed = results.filter(r => r).length;
    const total = results.length;
    console.log(`📊 Results: ${passed}/${total} tests passed`);
}
```

## 🎯 Testing Scenarios

### Authentication Testing
- **Valid Credentials** - Successful login and token generation
- **Invalid Credentials** - Proper error handling for wrong credentials
- **Token Expiration** - Token refresh and re-authentication
- **Session Management** - Session persistence and cleanup

### API Endpoint Testing
- **CRUD Operations** - Create, Read, Update, Delete functionality
- **Data Validation** - Input validation and sanitization
- **Error Handling** - Proper error responses and status codes
- **Performance** - Response time and load testing

### Integration Testing
- **Frontend-Backend** - Complete workflow testing
- **Database Integration** - Data persistence and retrieval
- **Cross-Browser** - Compatibility across different browsers
- **Mobile Responsiveness** - Mobile device compatibility

## 🚨 Common Issues

### PowerShell Issues
```powershell
# Execution Policy Issues
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# SSL Certificate Issues
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}

# Encoding Issues
$PSDefaultParameterValues['*:Encoding'] = 'utf8'
```

### Web Test Issues
```javascript
// CORS Issues
// Ensure backend CORS is configured for test domain

// Browser Security
// Use HTTPS for production testing
// Handle browser security restrictions

// Async Issues
// Proper promise handling and error catching
```

## 📈 Test Automation

### Continuous Integration
```yaml
# Example CI configuration for script tests
test-scripts:
  runs-on: windows-latest
  steps:
    - name: Run PowerShell Tests
      run: |
        cd tests/scripts/powershell
        .\test_api_request.ps1
        .\test_student_exists.ps1
```

### Scheduled Testing
```powershell
# Schedule regular API health checks
# Windows Task Scheduler or cron jobs
# Automated reporting and alerting
```

## 🔗 Related Testing

- **Backend Tests**: [../backend/](../backend/)
- **Frontend Tests**: [../frontend/](../frontend/)
- **Testing Documentation**: [../../docs/testing/](../../docs/testing/)

## 📞 Support

### PowerShell Debugging
1. **Use `-Verbose` flag** for detailed output
2. **Check execution policy** if scripts won't run
3. **Verify network connectivity** to API endpoints
4. **Check authentication tokens** for expiration

### Web Test Debugging
1. **Open browser developer tools** for network inspection
2. **Check console logs** for JavaScript errors
3. **Verify API endpoints** are accessible
4. **Test in different browsers** for compatibility

### Writing New Scripts
1. **Follow existing patterns** in script files
2. **Include comprehensive error handling**
3. **Add detailed logging and output**
4. **Test with both valid and invalid data**
5. **Document script purpose and usage**
