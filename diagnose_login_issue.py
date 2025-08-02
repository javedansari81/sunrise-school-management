#!/usr/bin/env python3
"""
Comprehensive login API diagnosis script
Tests various aspects of the login system to identify the root cause
"""

import json
import sys
import requests
from datetime import datetime


class LoginDiagnostics:
    """Comprehensive login system diagnostics"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.test_results = []
    
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:<8} {test_name}")
        if details:
            print(f"         {details}")
        self.test_results.append((test_name, success, details))
    
    def test_server_connectivity(self):
        """Test if the server is running and accessible"""
        print("\n🔍 Testing Server Connectivity...")
        
        try:
            response = requests.get(f"{self.api_base}/test", timeout=5)
            if response.status_code == 200:
                self.log_result("Server Connectivity", True, f"Server responding on {self.base_url}")
                return True
            else:
                self.log_result("Server Connectivity", False, f"Server returned {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_result("Server Connectivity", False, "Connection refused - server not running")
            return False
        except requests.exceptions.Timeout:
            self.log_result("Server Connectivity", False, "Connection timeout")
            return False
        except Exception as e:
            self.log_result("Server Connectivity", False, f"Unexpected error: {e}")
            return False
    
    def test_auth_endpoints_exist(self):
        """Test if authentication endpoints exist"""
        print("\n🔍 Testing Authentication Endpoints...")
        
        endpoints = [
            ("/auth/login-json", "POST"),
            ("/auth/login", "POST"),
            ("/auth/me", "GET"),
        ]
        
        all_exist = True
        for endpoint, method in endpoints:
            try:
                url = f"{self.api_base}{endpoint}"
                if method == "POST":
                    # Send empty POST to check if endpoint exists (will return 422 for validation error)
                    response = requests.post(url, json={}, timeout=5)
                    # 422 means endpoint exists but validation failed (expected)
                    # 404 means endpoint doesn't exist
                    if response.status_code in [422, 401, 400]:
                        self.log_result(f"Endpoint {endpoint}", True, f"Endpoint exists (returned {response.status_code})")
                    elif response.status_code == 404:
                        self.log_result(f"Endpoint {endpoint}", False, "Endpoint not found (404)")
                        all_exist = False
                    else:
                        self.log_result(f"Endpoint {endpoint}", True, f"Endpoint exists (returned {response.status_code})")
                else:
                    # GET request without auth (will return 401)
                    response = requests.get(url, timeout=5)
                    if response.status_code in [401, 403]:
                        self.log_result(f"Endpoint {endpoint}", True, f"Endpoint exists (returned {response.status_code})")
                    elif response.status_code == 404:
                        self.log_result(f"Endpoint {endpoint}", False, "Endpoint not found (404)")
                        all_exist = False
                    else:
                        self.log_result(f"Endpoint {endpoint}", True, f"Endpoint exists (returned {response.status_code})")
            except Exception as e:
                self.log_result(f"Endpoint {endpoint}", False, f"Error: {e}")
                all_exist = False
        
        return all_exist
    
    def test_login_with_test_credentials(self):
        """Test login with known test credentials"""
        print("\n🔍 Testing Login with Test Credentials...")
        
        # Test credentials from the database sample data
        test_credentials = [
            {"email": "admin@sunriseschool.edu", "password": "admin123", "type": "Admin"},
            {"email": "teacher@sunriseschool.edu", "password": "admin123", "type": "Teacher"},
            {"email": "student@sunriseschool.edu", "password": "admin123", "type": "Student"},
            {"email": "admin@sunrise.com", "password": "admin123", "type": "Admin Alt"},
            {"email": "john@sunrise.com", "password": "user123", "type": "User"},
            {"email": "test@example.com", "password": "testpassword", "type": "Test User"},
        ]
        
        login_success = False
        for creds in test_credentials:
            try:
                response = requests.post(
                    f"{self.api_base}/auth/login-json",
                    json={"email": creds["email"], "password": creds["password"]},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        self.log_result(f"Login {creds['type']}", True, f"Successfully logged in as {creds['email']}")
                        login_success = True
                        
                        # Test the token by calling /auth/me
                        token = data["access_token"]
                        me_response = requests.get(
                            f"{self.api_base}/auth/me",
                            headers={"Authorization": f"Bearer {token}"},
                            timeout=5
                        )
                        
                        if me_response.status_code == 200:
                            user_data = me_response.json()
                            self.log_result(f"Token Validation {creds['type']}", True, f"Token valid, user: {user_data.get('first_name', 'Unknown')}")
                        else:
                            self.log_result(f"Token Validation {creds['type']}", False, f"Token invalid: {me_response.status_code}")
                        
                        break  # Stop after first successful login
                    else:
                        self.log_result(f"Login {creds['type']}", False, "No access_token in response")
                elif response.status_code == 401:
                    self.log_result(f"Login {creds['type']}", False, "Invalid credentials (401)")
                elif response.status_code == 500:
                    error_detail = response.json().get("detail", "Unknown server error")
                    self.log_result(f"Login {creds['type']}", False, f"Server error (500): {error_detail}")
                else:
                    self.log_result(f"Login {creds['type']}", False, f"Unexpected status: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                self.log_result(f"Login {creds['type']}", False, "Connection error")
            except requests.exceptions.Timeout:
                self.log_result(f"Login {creds['type']}", False, "Request timeout")
            except Exception as e:
                self.log_result(f"Login {creds['type']}", False, f"Error: {e}")
        
        return login_success
    
    def test_database_connectivity(self):
        """Test if database is accessible by checking a simple endpoint"""
        print("\n🔍 Testing Database Connectivity...")
        
        try:
            # Try to access configuration endpoint which requires database
            response = requests.get(f"{self.api_base}/configuration/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and len(data) > 0:
                    self.log_result("Database Connectivity", True, f"Configuration endpoint returned {len(data)} items")
                    return True
                else:
                    self.log_result("Database Connectivity", False, "Configuration endpoint returned empty data")
                    return False
            elif response.status_code == 500:
                error_detail = response.json().get("detail", "Unknown error")
                self.log_result("Database Connectivity", False, f"Database error (500): {error_detail}")
                return False
            else:
                self.log_result("Database Connectivity", False, f"Unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Database Connectivity", False, f"Error: {e}")
            return False
    
    def test_frontend_api_configuration(self):
        """Test frontend API configuration"""
        print("\n🔍 Testing Frontend API Configuration...")
        
        # Check if frontend is configured to use the correct API URL
        frontend_config_issues = []
        
        # This would normally check the frontend build, but we'll check common issues
        expected_api_url = "http://localhost:8000/api/v1"
        
        print(f"         Expected API URL: {expected_api_url}")
        print(f"         Testing against: {self.api_base}")
        
        if self.api_base == expected_api_url:
            self.log_result("API URL Configuration", True, "API URL matches expected configuration")
        else:
            self.log_result("API URL Configuration", False, f"API URL mismatch: expected {expected_api_url}, testing {self.api_base}")
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n🔍 Testing CORS Configuration...")
        
        try:
            # Make a preflight request
            response = requests.options(
                f"{self.api_base}/auth/login-json",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                },
                timeout=5
            )
            
            if response.status_code in [200, 204]:
                cors_headers = response.headers
                if "Access-Control-Allow-Origin" in cors_headers:
                    self.log_result("CORS Configuration", True, f"CORS enabled: {cors_headers.get('Access-Control-Allow-Origin')}")
                else:
                    self.log_result("CORS Configuration", False, "CORS headers missing")
            else:
                self.log_result("CORS Configuration", False, f"Preflight failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("CORS Configuration", False, f"Error: {e}")
    
    def print_summary(self):
        """Print diagnostic summary"""
        print("\n" + "="*60)
        print("🔍 LOGIN API DIAGNOSTIC SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"✓ Successful tests: {passed}/{total}")
        
        failed_tests = [(name, details) for name, success, details in self.test_results if not success]
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for name, details in failed_tests:
                print(f"  • {name}: {details}")
        
        print("-"*60)
        
        if passed == total:
            print("🎉 All diagnostics passed! Login API should be working.")
            return True
        else:
            print("❌ Some diagnostics failed. See issues above.")
            print("\n💡 TROUBLESHOOTING RECOMMENDATIONS:")
            
            # Provide specific recommendations based on failures
            if any("Server Connectivity" in name for name, success, _ in self.test_results if not success):
                print("   1. Start the backend server: cd sunrise-backend-fastapi && python main.py")
                print("   2. Check if port 8000 is available")
                print("   3. Verify firewall settings")
            
            if any("Database" in name for name, success, _ in self.test_results if not success):
                print("   4. Check database connection settings")
                print("   5. Ensure database is running and accessible")
                print("   6. Run database migrations if needed")
            
            if any("Login" in name for name, success, _ in self.test_results if not success):
                print("   7. Check if test users exist in database")
                print("   8. Verify password hashing is working correctly")
                print("   9. Check authentication logic in backend")
            
            return False


def main():
    """Main diagnostic runner"""
    print("🚀 Starting Login API Diagnostics")
    print("="*60)
    
    diagnostics = LoginDiagnostics()
    
    # Run all diagnostic tests
    diagnostics.test_server_connectivity()
    diagnostics.test_auth_endpoints_exist()
    diagnostics.test_database_connectivity()
    diagnostics.test_login_with_test_credentials()
    diagnostics.test_frontend_api_configuration()
    diagnostics.test_cors_configuration()
    
    # Print summary and recommendations
    success = diagnostics.print_summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Diagnostics interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Diagnostic error: {e}")
        sys.exit(1)
