"""
Simple test script to check the faculty API endpoint
"""
import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000/api/v1"

def test_server_health():
    """Test if the server is running"""
    print("🏥 Testing Server Health...")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"⚠️ Server returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        print("💡 Start the server with: python -m uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return False

def test_faculty_endpoint():
    """Test the public faculty endpoint"""
    print("\n🎓 Testing Faculty Endpoint...")
    
    endpoint_url = f"{API_BASE_URL}/public/faculty"
    print(f"📍 URL: {endpoint_url}")
    
    try:
        response = requests.get(endpoint_url, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                teachers = data.get('teachers', [])
                departments = data.get('departments', {})
                total = data.get('total', 0)
                message = data.get('message', '')
                error = data.get('error', '')
                
                print(f"✅ API Response Summary:")
                print(f"   Teachers count: {len(teachers)}")
                print(f"   Departments: {list(departments.keys())}")
                print(f"   Total: {total}")
                print(f"   Message: {message}")
                
                if error:
                    print(f"   ⚠️ Error in response: {error}")
                
                if teachers:
                    print(f"\n👤 First Teacher Example:")
                    teacher = teachers[0]
                    print(f"   Name: {teacher.get('full_name', 'N/A')}")
                    print(f"   Employee ID: {teacher.get('employee_id', 'N/A')}")
                    print(f"   Position: {teacher.get('position', 'N/A')}")
                    print(f"   Department: {teacher.get('department', 'N/A')}")
                    print(f"   Email: {teacher.get('email', 'N/A')}")
                    print(f"   Experience: {teacher.get('experience_years', 0)} years")
                    
                    print(f"\n📋 Available Fields:")
                    print(f"   {list(teacher.keys())}")
                    
                    return True, len(teachers)
                else:
                    print("❌ No teachers in response!")
                    print("   This means the Faculty page will show mock data")
                    return False, 0
                    
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"📄 Raw response: {response.text[:200]}...")
                return False, 0
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            return False, 0
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server not accessible")
        return False, 0
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False, 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, 0

def test_other_endpoints():
    """Test other related endpoints"""
    print("\n🔍 Testing Related Endpoints...")
    
    endpoints = [
        ("/teachers/test-public", "Teachers Test Public"),
        ("/public/health", "Public Health Check"),
    ]
    
    for path, name in endpoints:
        url = f"{API_BASE_URL}{path}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
            else:
                print(f"⚠️ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")

def simulate_frontend_call():
    """Simulate what the frontend Faculty.tsx does"""
    print("\n🖥️ Simulating Frontend Behavior...")
    
    try:
        # This is exactly what the frontend does
        response = requests.get(f"{API_BASE_URL}/public/faculty", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            teachers_data = data.get('teachers', [])
            departments_data = data.get('departments', {})
            
            print(f"📊 Frontend would receive:")
            print(f"   Teachers: {len(teachers_data)} items")
            print(f"   Departments: {list(departments_data.keys())}")
            
            if len(teachers_data) > 0:
                print("✅ Frontend would display REAL teacher data")
                print("   Faculty page should show actual teachers from database")
                return True
            else:
                print("❌ Frontend would display MOCK data")
                print("   Faculty page will show 'Amit Kumar' and 'Subham Kumar'")
                print("   Reason: API returned empty teachers array")
                return False
        else:
            print("❌ Frontend would display MOCK data")
            print(f"   Reason: API call failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print("❌ Frontend would display MOCK data")
        print(f"   Reason: API call exception - {e}")
        return False

def main():
    """Main test function"""
    print("🔍 FACULTY PAGE DATA INVESTIGATION")
    print("=" * 60)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API URL: {API_BASE_URL}")
    
    # Step 1: Check server
    if not test_server_health():
        print("\n❌ Cannot proceed - server is not running")
        return
    
    # Step 2: Test faculty endpoint
    api_working, teacher_count = test_faculty_endpoint()
    
    # Step 3: Test other endpoints
    test_other_endpoints()
    
    # Step 4: Simulate frontend
    frontend_would_work = simulate_frontend_call()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 INVESTIGATION RESULTS")
    print("=" * 60)
    
    print(f"🌐 API Endpoint Working: {'✅ Yes' if api_working else '❌ No'}")
    print(f"👥 Teachers Found: {teacher_count}")
    print(f"🖥️ Frontend Shows Real Data: {'✅ Yes' if frontend_would_work else '❌ No'}")
    
    print("\n🎯 CONCLUSION:")
    if frontend_would_work:
        print("✅ The Faculty page SHOULD display real teacher data")
        print("   If you're still seeing mock data, try:")
        print("   1. Hard refresh the browser (Ctrl+F5)")
        print("   2. Clear browser cache")
        print("   3. Check browser console for errors")
    else:
        print("❌ The Faculty page WILL display mock data")
        if teacher_count == 0:
            print("   Root cause: No teachers returned from API")
            print("   Solutions:")
            print("   1. Check if database has active teacher records")
            print("   2. Verify database connection")
            print("   3. Check server logs for errors")
        else:
            print("   Root cause: API endpoint not accessible")
            print("   Solutions:")
            print("   1. Verify server is running on correct port")
            print("   2. Check CORS configuration")
            print("   3. Verify API routing")

if __name__ == "__main__":
    main()
