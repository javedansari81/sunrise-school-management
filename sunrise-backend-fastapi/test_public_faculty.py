"""
Simple test script to verify the public faculty endpoint is working
"""
import requests
import json
from datetime import datetime

def test_public_faculty_endpoint():
    """Test the public faculty endpoint"""
    
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/public/faculty"
    full_url = f"{base_url}{endpoint}"
    
    print("🎓 Testing Public Faculty Endpoint")
    print("=" * 50)
    print(f"URL: {full_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Test the endpoint
        print("📡 Making request...")
        response = requests.get(full_url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            
            try:
                data = response.json()
                print("\n📋 Response Data:")
                print(f"   Teachers: {len(data.get('teachers', []))}")
                print(f"   Departments: {list(data.get('departments', {}).keys())}")
                print(f"   Total: {data.get('total', 0)}")
                print(f"   Message: {data.get('message', 'No message')}")
                
                if data.get('error'):
                    print(f"   ⚠️ Error: {data.get('error')}")
                
                # Show first teacher as example
                teachers = data.get('teachers', [])
                if teachers:
                    print(f"\n👤 Example Teacher:")
                    teacher = teachers[0]
                    print(f"   Name: {teacher.get('full_name')}")
                    print(f"   Position: {teacher.get('position')}")
                    print(f"   Department: {teacher.get('department')}")
                    print(f"   Subjects: {teacher.get('subjects', [])}")
                    print(f"   Experience: {teacher.get('experience_years')} years")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error: {e}")
                print(f"📄 Raw Response: {response.text[:200]}...")
                return False
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Cannot connect to server")
        print("💡 Make sure the server is running:")
        print("   cd sunrise-backend-fastapi")
        print("   python -m uvicorn main:app --reload")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False


def test_server_health():
    """Test if the server is running"""
    
    print("🏥 Testing Server Health")
    print("=" * 30)
    
    endpoints_to_test = [
        ("http://localhost:8000/", "Server Root"),
        ("http://localhost:8000/api/v1/public/health", "Public Health Check"),
    ]
    
    for url, description in endpoints_to_test:
        try:
            print(f"📡 Testing {description}: {url}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ {response.status_code} - OK")
            else:
                print(f"   ⚠️ {response.status_code} - {response.text[:50]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return True


def main():
    """Main test function"""
    
    print("🚀 Public Faculty Endpoint Test")
    print("=" * 60)
    
    # Test server health first
    if not test_server_health():
        print("\n❌ Server health check failed. Cannot proceed with faculty endpoint test.")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure the server is running: python -m uvicorn main:app --reload")
        print("2. Check if the server is accessible at http://localhost:8000")
        print("3. Verify the database connection is working")
        return
    
    print("\n" + "=" * 60)
    
    # Test the faculty endpoint
    success = test_public_faculty_endpoint()
    
    print("\n" + "=" * 60)
    
    if success:
        print("✅ PUBLIC FACULTY ENDPOINT TEST PASSED!")
        print("\n💡 Next Steps:")
        print("1. The endpoint is working correctly")
        print("2. Frontend should now be able to load faculty data")
        print("3. Check the Faculty page in the browser")
    else:
        print("❌ PUBLIC FACULTY ENDPOINT TEST FAILED!")
        print("\n🔧 Troubleshooting:")
        print("1. Check server logs for detailed error messages")
        print("2. Verify database connection and teacher data exists")
        print("3. Check if the public router is properly registered")
        print("4. Ensure CORS is configured correctly for frontend requests")


if __name__ == "__main__":
    main()
