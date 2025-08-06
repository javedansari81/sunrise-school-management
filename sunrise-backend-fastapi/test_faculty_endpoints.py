"""
Test script to debug faculty endpoints and identify the 404 issue
"""
import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

async def test_endpoint(session, url, description):
    """Test a single endpoint and return results"""
    print(f"\n🔍 Testing: {description}")
    print(f"📍 URL: {url}")
    
    try:
        async with session.get(url) as response:
            status = response.status
            content_type = response.headers.get('content-type', 'unknown')
            
            print(f"📊 Status: {status}")
            print(f"📄 Content-Type: {content_type}")
            
            if status == 200:
                try:
                    data = await response.json()
                    print(f"✅ SUCCESS - Response received")
                    print(f"📝 Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    if isinstance(data, dict):
                        if 'teachers' in data:
                            print(f"👥 Teachers count: {len(data.get('teachers', []))}")
                        if 'departments' in data:
                            print(f"🏢 Departments: {list(data.get('departments', {}).keys())}")
                        if 'total' in data:
                            print(f"📊 Total: {data.get('total')}")
                        if 'message' in data:
                            print(f"💬 Message: {data.get('message')}")
                    
                    return True, data
                except json.JSONDecodeError as e:
                    text = await response.text()
                    print(f"❌ JSON decode error: {e}")
                    print(f"📄 Raw response: {text[:200]}...")
                    return False, text
            else:
                text = await response.text()
                print(f"❌ HTTP {status} Error")
                print(f"📄 Response: {text[:200]}...")
                return False, text
                
    except aiohttp.ClientError as e:
        print(f"❌ Connection error: {e}")
        return False, str(e)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, str(e)


async def test_server_health():
    """Test if the server is running"""
    print("🏥 Testing server health...")
    
    async with aiohttp.ClientSession() as session:
        # Test root endpoint
        success, _ = await test_endpoint(
            session, 
            "http://localhost:8000/", 
            "Server Root"
        )
        
        if not success:
            print("❌ Server appears to be down or not accessible")
            return False
        
        # Test API root
        success, _ = await test_endpoint(
            session, 
            f"{BASE_URL}/", 
            "API Root"
        )
        
        return success


async def test_faculty_endpoints():
    """Test both faculty endpoints"""
    print("\n" + "="*60)
    print("🎓 FACULTY ENDPOINTS TEST")
    print("="*60)
    
    # Check server health first
    if not await test_server_health():
        print("\n❌ Cannot proceed - server is not accessible")
        return
    
    async with aiohttp.ClientSession() as session:
        endpoints_to_test = [
            (f"{BASE_URL}/teachers/public/faculty", "Teachers Router - Public Faculty"),
            (f"{BASE_URL}/public/faculty", "Public Router - Faculty"),
            (f"{BASE_URL}/teachers/test-public", "Teachers Router - Test Public"),
            (f"{BASE_URL}/teachers/", "Teachers Router - List (requires auth)"),
        ]
        
        results = {}
        
        for url, description in endpoints_to_test:
            success, data = await test_endpoint(session, url, description)
            results[url] = {
                'success': success,
                'data': data,
                'description': description
            }
        
        # Summary
        print("\n" + "="*60)
        print("📋 SUMMARY")
        print("="*60)
        
        working_endpoints = []
        failing_endpoints = []
        
        for url, result in results.items():
            if result['success']:
                working_endpoints.append((url, result['description']))
                print(f"✅ {result['description']}: {url}")
            else:
                failing_endpoints.append((url, result['description'], result['data']))
                print(f"❌ {result['description']}: {url}")
        
        print(f"\n📊 Working: {len(working_endpoints)}, Failing: {len(failing_endpoints)}")
        
        # Recommendations
        print("\n🔧 RECOMMENDATIONS:")
        
        if any("/teachers/public/faculty" in url for url, _ in working_endpoints):
            print("✅ /teachers/public/faculty is working - frontend should use this")
        elif any("/public/faculty" in url for url, _ in working_endpoints):
            print("✅ /public/faculty is working - update frontend to use this")
            print("   Change: api.get('/teachers/public/faculty') → api.get('/public/faculty')")
        else:
            print("❌ Neither faculty endpoint is working")
            print("   Check:")
            print("   1. Database connection")
            print("   2. Teacher CRUD methods")
            print("   3. Router registration")
            print("   4. Authentication middleware")
        
        # Detailed error analysis
        if failing_endpoints:
            print("\n🔍 ERROR ANALYSIS:")
            for url, desc, error in failing_endpoints:
                print(f"\n❌ {desc}:")
                print(f"   URL: {url}")
                if isinstance(error, str):
                    if "404" in error:
                        print("   Issue: Endpoint not found - check router registration")
                    elif "500" in error:
                        print("   Issue: Server error - check logs and database")
                    elif "401" in error or "403" in error:
                        print("   Issue: Authentication required - endpoint may not be public")
                    else:
                        print(f"   Error: {error[:100]}...")


async def test_with_auth_token():
    """Test endpoints with authentication token"""
    print("\n🔐 Testing with authentication...")
    
    # This would require a valid token - for now just show the concept
    print("📝 To test with auth, you would need to:")
    print("1. Login via /api/v1/auth/login-json")
    print("2. Extract the access_token from response")
    print("3. Add Authorization: Bearer <token> header")
    print("4. Test the endpoints again")


async def main():
    """Main test function"""
    print("🚀 Faculty Endpoints Debugging Tool")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    
    try:
        await test_faculty_endpoints()
        await test_with_auth_token()
        
        print("\n" + "="*60)
        print("✅ Testing completed!")
        print("💡 If endpoints are failing, check:")
        print("   1. Server is running: python -m uvicorn main:app --reload")
        print("   2. Database is connected and has teacher data")
        print("   3. Router registration in app/api/v1/api.py")
        print("   4. CORS settings for frontend requests")
        
    except Exception as e:
        print(f"\n❌ Test script failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
