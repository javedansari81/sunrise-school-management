# Shell Script Tests

This directory contains PowerShell scripts for testing various API endpoints and functionality of the Sunrise School Management System.

## Directory Structure

```
tests/scripts/powershell/
├── api-tests/              # General API testing scripts
├── leave-management/       # Leave management specific tests
│   ├── test_api_request.ps1        # Tests leave request API endpoint
│   └── test_detailed_error.ps1     # Tests leave request with detailed error handling
├── student-management/     # Student management specific tests
│   ├── test_student_exists.ps1     # Tests student existence API
│   └── test_students.ps1           # Tests students listing API
└── README.md              # This file
```

## Prerequisites

- PowerShell 5.0 or later
- Backend server running on `http://localhost:8000`
- Valid admin credentials (admin@sunriseschool.edu / admin123)

## Usage

### Leave Management Tests

**Test Leave Request API:**
```powershell
cd tests/scripts/powershell/leave-management
.\test_api_request.ps1
```

**Test Leave Request with Detailed Error Handling:**
```powershell
cd tests/scripts/powershell/leave-management
.\test_detailed_error.ps1
```

### Student Management Tests

**Test Student Existence:**
```powershell
cd tests/scripts/powershell/student-management
.\test_student_exists.ps1
```

**Test Students Listing:**
```powershell
cd tests/scripts/powershell/student-management
.\test_students.ps1
```

## Script Descriptions

### Leave Management Scripts

- **`test_api_request.ps1`**: Tests the leave request creation API endpoint with authentication
- **`test_detailed_error.ps1`**: Similar to above but with enhanced error handling and detailed output

### Student Management Scripts

- **`test_student_exists.ps1`**: Checks if a specific student (ID: 5) exists in the system
- **`test_students.ps1`**: Retrieves and displays all available students from the API

## Authentication

All scripts use the following test credentials:
- **Email**: admin@sunriseschool.edu
- **Password**: admin123

The scripts automatically:
1. Authenticate with the backend API
2. Retrieve an access token
3. Use the token for subsequent API calls

## Error Handling

Each script includes comprehensive error handling that displays:
- HTTP status codes
- Error messages
- Response bodies for debugging

## Notes

- Ensure the backend server is running before executing any scripts
- Scripts are configured for local development (localhost:8000)
- For production testing, update the URLs in each script accordingly
- All scripts use JSON format for API communication
