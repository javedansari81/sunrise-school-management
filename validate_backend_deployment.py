#!/usr/bin/env python3
"""
Backend Deployment Validation Script
Validates that the Render.com backend deployment is working correctly
"""

import requests
import json
import sys
from urllib.parse import urljoin

# Configuration
BACKEND_URLS = [
    "https://sunrise-school-backend-api.onrender.com",
    # Add your actual backend URL here if different
]

FRONTEND_URLS = [
    "https://sunrise-school-frontend-web.onrender.com",
    # Add your actual frontend URL here if different
]

def test_endpoint(url, endpoint, expected_status=200):
    """Test a specific endpoint"""
    full_url = urljoin(url, endpoint)
    try:
        print(f"🔍 Testing: {full_url}")
        response = requests.get(full_url, timeout=30)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            try:
                data = response.json()
                print(f"   ✅ Response: {json.dumps(data, indent=2)}")
                return True, data
            except json.JSONDecodeError:
                print(f"   ✅ Response: {response.text[:200]}...")
                return True, response.text
        else:
            print(f"   ❌ Expected {expected_status}, got {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection Error: {str(e)}")
        return False, None

def validate_backend(backend_url):
    """Validate backend service"""
    print(f"\n🚀 Validating Backend: {backend_url}")
    print("=" * 60)
    
    results = {}
    
    # Test root endpoint
    success, data = test_endpoint(backend_url, "/")
    results['root'] = success
    
    # Test health endpoint
    success, data = test_endpoint(backend_url, "/health")
    results['health'] = success
    if success and isinstance(data, dict):
        print(f"   Environment: {data.get('environment', 'unknown')}")
        print(f"   Database: {data.get('database', 'unknown')}")
        print(f"   CORS Origins: {data.get('cors_origins', 'unknown')}")
    
    # Test API test endpoint
    success, data = test_endpoint(backend_url, "/api/v1/test")
    results['api_test'] = success
    
    # Test API docs
    success, data = test_endpoint(backend_url, "/docs")
    results['docs'] = success
    
    # Test Leave Management endpoints
    print(f"\n📋 Testing Leave Management Endpoints:")
    
    # Test leaves endpoint (might require auth)
    success, data = test_endpoint(backend_url, "/api/v1/leaves/", expected_status=401)
    if success or (not success and "401" in str(data)):
        print(f"   ✅ Leaves endpoint exists (401 expected without auth)")
        results['leaves'] = True
    else:
        results['leaves'] = False
    
    # Test configuration endpoint
    success, data = test_endpoint(backend_url, "/api/v1/configuration/leave-management/", expected_status=401)
    if success or (not success and "401" in str(data)):
        print(f"   ✅ Leave config endpoint exists (401 expected without auth)")
        results['leave_config'] = True
    else:
        results['leave_config'] = False
    
    return results

def validate_cors(backend_url, frontend_url):
    """Validate CORS configuration"""
    print(f"\n🔒 Validating CORS Configuration")
    print("=" * 60)
    
    try:
        # Test preflight request
        headers = {
            'Origin': frontend_url,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        response = requests.options(
            urljoin(backend_url, "/api/v1/test"),
            headers=headers,
            timeout=10
        )
        
        print(f"Preflight Status: {response.status_code}")
        print(f"CORS Headers: {dict(response.headers)}")
        
        # Check CORS headers
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        cors_methods = response.headers.get('Access-Control-Allow-Methods')
        cors_headers = response.headers.get('Access-Control-Allow-Headers')
        
        if cors_origin == '*' or cors_origin == frontend_url:
            print(f"   ✅ CORS Origin: {cors_origin}")
            return True
        else:
            print(f"   ❌ CORS Origin: {cors_origin} (expected {frontend_url} or *)")
            return False
            
    except Exception as e:
        print(f"   ❌ CORS Test Error: {str(e)}")
        return False

def main():
    """Main validation function"""
    print("🔍 Backend Deployment Validation")
    print("=" * 60)
    
    all_results = {}
    
    # Test each backend URL
    for backend_url in BACKEND_URLS:
        results = validate_backend(backend_url)
        all_results[backend_url] = results
        
        # Test CORS with each frontend URL
        for frontend_url in FRONTEND_URLS:
            cors_result = validate_cors(backend_url, frontend_url)
            results[f'cors_{frontend_url}'] = cors_result
    
    # Summary
    print(f"\n📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    for backend_url, results in all_results.items():
        print(f"\nBackend: {backend_url}")
        for test, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {test}: {status}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("=" * 60)
    
    failed_tests = []
    for backend_url, results in all_results.items():
        for test, success in results.items():
            if not success:
                failed_tests.append(f"{backend_url} - {test}")
    
    if failed_tests:
        print("❌ Issues found:")
        for test in failed_tests:
            print(f"  - {test}")
        print("\n🔧 Next Steps:")
        print("1. Check Render.com service status")
        print("2. Verify environment variables")
        print("3. Redeploy services if needed")
        print("4. Check service logs in Render dashboard")
    else:
        print("✅ All tests passed! Backend should be working correctly.")

if __name__ == "__main__":
    main()
