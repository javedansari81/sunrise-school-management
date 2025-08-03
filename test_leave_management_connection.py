#!/usr/bin/env python3
"""
Leave Management System Connection Test
Tests the specific connection between frontend and backend for Leave Management
"""

import requests
import json
import sys
from urllib.parse import urljoin

# Configuration - Update these with your actual URLs
BACKEND_URL = "https://sunrise-school-backend-api.onrender.com"
FRONTEND_URL = "https://sunrise-school-frontend-web.onrender.com"

# Test credentials
TEST_CREDENTIALS = {
    "email": "admin@sunriseschool.edu",
    "password": "admin123"
}

def test_authentication():
    """Test authentication and get token"""
    print("🔐 Testing Authentication...")
    
    try:
        login_url = urljoin(BACKEND_URL, "/api/v1/auth/login-json")
        response = requests.post(
            login_url,
            json=TEST_CREDENTIALS,
            timeout=30
        )
        
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            if token:
                print("✅ Authentication successful")
                return token
            else:
                print("❌ No access token in response")
                print(f"Response: {data}")
                return None
        else:
            print(f"❌ Authentication failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def test_leave_endpoints(token):
    """Test Leave Management specific endpoints"""
    print("\n📋 Testing Leave Management Endpoints...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    endpoints = [
        ("/api/v1/leaves/", "GET", "Get leave requests"),
        ("/api/v1/leaves/pending", "GET", "Get pending leaves"),
        ("/api/v1/leaves/statistics", "GET", "Get leave statistics"),
        ("/api/v1/configuration/leave-management/", "GET", "Get leave configuration"),
    ]
    
    results = {}
    
    for endpoint, method, description in endpoints:
        try:
            url = urljoin(BACKEND_URL, endpoint)
            print(f"\n🔍 Testing: {description}")
            print(f"   URL: {url}")
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            else:
                response = requests.request(method, url, headers=headers, timeout=30)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Success: {len(str(data))} chars response")
                    results[endpoint] = True
                except:
                    print(f"   ✅ Success: Non-JSON response")
                    results[endpoint] = True
            elif response.status_code == 401:
                print(f"   ❌ Unauthorized - Token may be invalid")
                results[endpoint] = False
            elif response.status_code == 403:
                print(f"   ❌ Forbidden - Insufficient permissions")
                results[endpoint] = False
            elif response.status_code == 404:
                print(f"   ❌ Not Found - Endpoint doesn't exist")
                results[endpoint] = False
            else:
                print(f"   ❌ Error: {response.text[:200]}")
                results[endpoint] = False
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection Error - Backend not reachable")
            results[endpoint] = False
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout - Request took too long")
            results[endpoint] = False
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results[endpoint] = False
    
    return results

def test_cors_from_frontend():
    """Test CORS by simulating frontend request"""
    print("\n🔒 Testing CORS from Frontend Origin...")
    
    try:
        headers = {
            'Origin': FRONTEND_URL,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        url = urljoin(BACKEND_URL, "/api/v1/leaves/")
        response = requests.options(url, headers=headers, timeout=10)
        
        print(f"Preflight Status: {response.status_code}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        print("CORS Headers:")
        for header, value in cors_headers.items():
            print(f"   {header}: {value}")
        
        # Check if frontend origin is allowed
        allowed_origin = cors_headers['Access-Control-Allow-Origin']
        if allowed_origin == '*' or allowed_origin == FRONTEND_URL:
            print("✅ CORS configured correctly for frontend")
            return True
        else:
            print(f"❌ CORS issue: Frontend {FRONTEND_URL} not in allowed origins")
            return False
            
    except Exception as e:
        print(f"❌ CORS test error: {str(e)}")
        return False

def test_frontend_config():
    """Test if frontend can reach backend"""
    print("\n🌐 Testing Frontend Configuration...")
    
    try:
        # Try to access frontend
        response = requests.get(FRONTEND_URL, timeout=10)
        print(f"Frontend Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            
            # Check if the HTML contains the API URL
            html_content = response.text
            if BACKEND_URL in html_content:
                print(f"✅ Backend URL found in frontend build")
            else:
                print(f"⚠️  Backend URL not found in frontend build")
                print(f"   Expected: {BACKEND_URL}")
                
            return True
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend test error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 Leave Management System Connection Test")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print("=" * 60)
    
    # Test 1: Authentication
    token = test_authentication()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Test 2: Leave Management Endpoints
    endpoint_results = test_leave_endpoints(token)
    
    # Test 3: CORS Configuration
    cors_result = test_cors_from_frontend()
    
    # Test 4: Frontend Configuration
    frontend_result = test_frontend_config()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    
    print(f"Authentication: {'✅ PASS' if token else '❌ FAIL'}")
    print(f"CORS Configuration: {'✅ PASS' if cors_result else '❌ FAIL'}")
    print(f"Frontend Access: {'✅ PASS' if frontend_result else '❌ FAIL'}")
    
    print("\nEndpoint Tests:")
    for endpoint, success in endpoint_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {endpoint}: {status}")
    
    # Diagnosis
    print("\n🔍 DIAGNOSIS")
    print("=" * 60)
    
    if all(endpoint_results.values()) and cors_result and frontend_result:
        print("✅ All tests passed! Leave Management should work correctly.")
        print("\n💡 If you're still seeing 'Backend server not running' error:")
        print("   1. Clear browser cache and cookies")
        print("   2. Try logging out and logging back in")
        print("   3. Check browser console for specific errors")
    else:
        print("❌ Issues detected:")
        
        if not cors_result:
            print("   - CORS configuration needs fixing")
        
        failed_endpoints = [ep for ep, success in endpoint_results.items() if not success]
        if failed_endpoints:
            print("   - Failed endpoints:", ", ".join(failed_endpoints))
        
        if not frontend_result:
            print("   - Frontend configuration issues")
        
        print("\n🔧 Recommended Actions:")
        print("   1. Check Render.com service logs")
        print("   2. Verify environment variables")
        print("   3. Redeploy services if needed")

if __name__ == "__main__":
    main()
