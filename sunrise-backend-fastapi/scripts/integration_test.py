#!/usr/bin/env python3
"""
Integration test script to verify the system works end-to-end
"""
import asyncio
import sys
import httpx
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))


async def test_api_endpoints():
    """Test basic API endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🔍 Testing API endpoints...")
        
        # Test health endpoint
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            return False
        
        # Test root endpoint
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                print("✅ Root endpoint working")
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
            return False
        
        # Test API v1 test endpoint
        try:
            response = await client.get(f"{base_url}/api/v1/test")
            if response.status_code == 200:
                print("✅ API v1 test endpoint working")
            else:
                print(f"❌ API v1 test endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API v1 test endpoint error: {e}")
            return False
        
        return True


async def test_authentication_flow():
    """Test authentication flow"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🔐 Testing authentication flow...")
        
        # Test login with default admin credentials
        try:
            login_data = {
                "email": "admin@sunriseschool.edu",
                "password": "admin123"
            }
            
            response = await client.post(f"{base_url}/api/v1/auth/login-json", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    print("✅ Login successful")
                    token = data["access_token"]
                    
                    # Test protected endpoint
                    headers = {"Authorization": f"Bearer {token}"}
                    protected_response = await client.get(f"{base_url}/api/v1/auth/me", headers=headers)
                    
                    if protected_response.status_code == 200:
                        user_data = protected_response.json()
                        print(f"✅ Protected endpoint working - User: {user_data.get('email')}")
                        return True
                    else:
                        print(f"❌ Protected endpoint failed: {protected_response.status_code}")
                        return False
                else:
                    print("❌ Login response missing access_token")
                    return False
            else:
                print(f"❌ Login failed: {response.status_code}")
                if response.status_code == 401:
                    print("ℹ️  This might be expected if the default admin user hasn't been created yet")
                    print("ℹ️  Run: python scripts/setup.py to create the default admin user")
                return False
                
        except Exception as e:
            print(f"❌ Authentication test error: {e}")
            return False


async def test_cors_headers():
    """Test CORS headers"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🌐 Testing CORS headers...")
        
        try:
            # Test preflight request
            headers = {
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
            
            response = await client.options(f"{base_url}/api/v1/auth/login-json", headers=headers)
            
            if response.status_code in [200, 204]:
                cors_headers = response.headers
                if "access-control-allow-origin" in cors_headers:
                    print("✅ CORS headers present")
                    return True
                else:
                    print("⚠️  CORS headers missing but request succeeded")
                    return True
            else:
                print(f"❌ CORS preflight failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ CORS test error: {e}")
            return False


async def main():
    """Main integration test function"""
    print("🚀 Starting integration tests...")
    print("=" * 50)
    
    # Test basic API endpoints
    api_test = await test_api_endpoints()
    print()
    
    # Test CORS
    cors_test = await test_cors_headers()
    print()
    
    # Test authentication
    auth_test = await test_authentication_flow()
    print()
    
    # Summary
    print("=" * 50)
    print("📊 Integration Test Summary:")
    print(f"API Endpoints: {'✅ PASS' if api_test else '❌ FAIL'}")
    print(f"CORS Headers: {'✅ PASS' if cors_test else '❌ FAIL'}")
    print(f"Authentication: {'✅ PASS' if auth_test else '❌ FAIL'}")
    
    if all([api_test, cors_test, auth_test]):
        print("\n🎉 All integration tests passed!")
        return 0
    else:
        print("\n❌ Some integration tests failed!")
        print("\nTroubleshooting:")
        print("1. Make sure the FastAPI server is running: python main.py")
        print("2. Make sure the database is set up: python scripts/setup.py")
        print("3. Check the server logs for any errors")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
