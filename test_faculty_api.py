#!/usr/bin/env python3
"""
Test script to verify the Faculty API endpoint is working correctly
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your backend runs on a different port
API_ENDPOINTS = [
    "/api/v1/public/health",
    "/api/v1/public/faculty",
    "/api/v1/teachers/public/faculty"  # Test the old endpoint too
]

def test_endpoint(url):
    """Test a single endpoint"""
    print(f"\n🔍 Testing: {url}")
    print("-" * 50)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ SUCCESS - Response received")
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                if 'teachers' in data:
                    print(f"Teachers count: {len(data.get('teachers', []))}")
                    if data.get('teachers'):
                        print(f"First teacher: {data['teachers'][0]}")
                
                return True, data
            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error: {e}")
                print(f"Raw response: {response.text[:200]}...")
                return False, None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error - Is the backend server running on {BASE_URL}?")
        return False, None
    except requests.exceptions.Timeout:
        print(f"❌ Timeout Error - Server took too long to respond")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False, None

def main():
    """Main test function"""
    print("🏫 SUNRISE SCHOOL - FACULTY API TEST")
    print("=" * 60)
    print(f"Testing backend at: {BASE_URL}")
    
    results = {}
    
    for endpoint in API_ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        success, data = test_endpoint(url)
        results[endpoint] = {"success": success, "data": data}
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for endpoint, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} - {endpoint}")
    
    # Check if any endpoint worked
    working_endpoints = [ep for ep, result in results.items() if result["success"]]
    
    if working_endpoints:
        print(f"\n🎯 WORKING ENDPOINTS: {len(working_endpoints)}")
        for ep in working_endpoints:
            print(f"  - {ep}")
    else:
        print(f"\n⚠️  NO WORKING ENDPOINTS FOUND")
        print("Possible issues:")
        print("  1. Backend server is not running")
        print("  2. Backend is running on a different port")
        print("  3. CORS issues")
        print("  4. Database connection problems")
        print("  5. Authentication middleware blocking public endpoints")
    
    return len(working_endpoints) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
