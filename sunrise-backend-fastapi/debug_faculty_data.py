"""
Debug script to investigate Faculty page data issues
This script will check:
1. Database connection and teacher records
2. API endpoint response
3. Data formatting and processing
"""
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/sunrise_school")
API_BASE_URL = "http://localhost:8000/api/v1"

async def check_database_teachers():
    """Check teacher records directly in the database"""
    print("🗄️  CHECKING DATABASE TEACHERS")
    print("=" * 50)
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check total teacher count
        total_count = await conn.fetchval("SELECT COUNT(*) FROM teachers")
        print(f"📊 Total teachers in database: {total_count}")
        
        # Check active teacher count
        active_count = await conn.fetchval("""
            SELECT COUNT(*) FROM teachers 
            WHERE is_active = true AND (is_deleted IS NULL OR is_deleted = false)
        """)
        print(f"✅ Active teachers: {active_count}")
        
        # Check soft-deleted teacher count
        deleted_count = await conn.fetchval("""
            SELECT COUNT(*) FROM teachers 
            WHERE is_deleted = true
        """)
        print(f"🗑️  Soft-deleted teachers: {deleted_count}")
        
        if active_count > 0:
            print(f"\n👥 Sample Active Teachers:")
            teachers = await conn.fetch("""
                SELECT 
                    id, employee_id, first_name, last_name, position, 
                    department, subjects, experience_years, is_active,
                    email, phone, joining_date, qualification_id
                FROM teachers 
                WHERE is_active = true AND (is_deleted IS NULL OR is_deleted = false)
                ORDER BY first_name, last_name
                LIMIT 5
            """)
            
            for i, teacher in enumerate(teachers, 1):
                print(f"   {i}. {teacher['first_name']} {teacher['last_name']} ({teacher['employee_id']})")
                print(f"      Position: {teacher['position']}")
                print(f"      Department: {teacher['department']}")
                print(f"      Email: {teacher['email']}")
                print(f"      Subjects: {teacher['subjects']}")
                print(f"      Experience: {teacher['experience_years']} years")
                print(f"      Active: {teacher['is_active']}")
                print()
        else:
            print("❌ No active teachers found in database!")
            
            # Check if there are any teachers at all
            if total_count > 0:
                print("📋 All teachers (including inactive/deleted):")
                all_teachers = await conn.fetch("""
                    SELECT employee_id, first_name, last_name, is_active, is_deleted
                    FROM teachers 
                    ORDER BY first_name, last_name
                    LIMIT 10
                """)
                
                for teacher in all_teachers:
                    status = "Active" if teacher['is_active'] else "Inactive"
                    if teacher['is_deleted']:
                        status += " (Deleted)"
                    print(f"   - {teacher['first_name']} {teacher['last_name']} ({teacher['employee_id']}) - {status}")
        
        await conn.close()
        return active_count > 0
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


async def test_api_endpoint():
    """Test the public faculty API endpoint"""
    print("\n🌐 TESTING API ENDPOINT")
    print("=" * 50)
    
    endpoint_url = f"{API_BASE_URL}/public/faculty"
    print(f"📍 URL: {endpoint_url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint_url) as response:
                status = response.status
                print(f"📊 Status: {status}")
                
                if status == 200:
                    try:
                        data = await response.json()
                        print(f"✅ API Response received")
                        
                        teachers = data.get('teachers', [])
                        departments = data.get('departments', {})
                        total = data.get('total', 0)
                        message = data.get('message', '')
                        error = data.get('error', '')
                        
                        print(f"📊 Response Summary:")
                        print(f"   Teachers count: {len(teachers)}")
                        print(f"   Departments: {list(departments.keys())}")
                        print(f"   Total: {total}")
                        print(f"   Message: {message}")
                        
                        if error:
                            print(f"   ⚠️ Error: {error}")
                        
                        if teachers:
                            print(f"\n👤 Sample Teacher Data:")
                            teacher = teachers[0]
                            print(f"   Name: {teacher.get('full_name')}")
                            print(f"   Employee ID: {teacher.get('employee_id')}")
                            print(f"   Position: {teacher.get('position')}")
                            print(f"   Department: {teacher.get('department')}")
                            print(f"   Subjects: {teacher.get('subjects', [])}")
                            print(f"   Experience: {teacher.get('experience_years')} years")
                            print(f"   Email: {teacher.get('email')}")
                            print(f"   Phone: {teacher.get('phone')}")
                            
                            # Show raw data structure
                            print(f"\n📋 Raw Teacher Data Structure:")
                            print(f"   Keys: {list(teacher.keys())}")
                        else:
                            print("❌ No teachers in API response!")
                        
                        return len(teachers) > 0, data
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error: {e}")
                        text = await response.text()
                        print(f"📄 Raw response: {text[:300]}...")
                        return False, None
                else:
                    text = await response.text()
                    print(f"❌ HTTP {status} error")
                    print(f"📄 Response: {text[:300]}...")
                    return False, None
                    
    except aiohttp.ClientError as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure the server is running:")
        print("   cd sunrise-backend-fastapi")
        print("   python -m uvicorn main:app --reload")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, None


async def test_frontend_behavior():
    """Simulate frontend behavior"""
    print("\n🖥️  SIMULATING FRONTEND BEHAVIOR")
    print("=" * 50)
    
    # This simulates what the Faculty.tsx component does
    try:
        print("📡 Making API call (like Faculty.tsx does)...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/public/faculty") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract data like the frontend does
                    teachers_data = data.get('teachers', [])
                    departments_data = data.get('departments', {})
                    
                    print(f"✅ Frontend would receive:")
                    print(f"   Teachers: {len(teachers_data)} items")
                    print(f"   Departments: {list(departments_data.keys())}")
                    
                    if len(teachers_data) > 0:
                        print("✅ Frontend would display real data")
                        return True
                    else:
                        print("❌ Frontend would fall back to mock data")
                        print("   Reason: Empty teachers array")
                        return False
                else:
                    print(f"❌ Frontend would fall back to mock data")
                    print(f"   Reason: API returned {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Frontend would fall back to mock data")
        print(f"   Reason: API call failed - {e}")
        return False


async def check_server_health():
    """Check if the server is running and healthy"""
    print("\n🏥 CHECKING SERVER HEALTH")
    print("=" * 30)
    
    endpoints = [
        (f"{API_BASE_URL.replace('/api/v1', '')}/", "Server Root"),
        (f"{API_BASE_URL}/public/health", "Public Health"),
    ]
    
    for url, name in endpoints:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        print(f"✅ {name}: OK")
                    else:
                        print(f"⚠️ {name}: {response.status}")
        except Exception as e:
            print(f"❌ {name}: {e}")
            return False
    
    return True


async def main():
    """Main debugging function"""
    print("🔍 FACULTY PAGE DATA DEBUGGING TOOL")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Base URL: {API_BASE_URL}")
    print(f"🗄️ Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Not configured'}")
    
    # Step 1: Check server health
    server_healthy = await check_server_health()
    if not server_healthy:
        print("\n❌ Server is not healthy. Cannot proceed with debugging.")
        return
    
    # Step 2: Check database
    db_has_teachers = await check_database_teachers()
    
    # Step 3: Test API endpoint
    api_working, api_data = await test_api_endpoint()
    
    # Step 4: Test frontend behavior
    frontend_would_work = await test_frontend_behavior()
    
    # Summary and recommendations
    print("\n" + "=" * 60)
    print("📋 DEBUGGING SUMMARY")
    print("=" * 60)
    
    print(f"🗄️ Database has active teachers: {'✅ Yes' if db_has_teachers else '❌ No'}")
    print(f"🌐 API endpoint working: {'✅ Yes' if api_working else '❌ No'}")
    print(f"🖥️ Frontend would show real data: {'✅ Yes' if frontend_would_work else '❌ No'}")
    
    print("\n🔧 RECOMMENDATIONS:")
    
    if not db_has_teachers:
        print("❌ ISSUE: No active teachers in database")
        print("   Solutions:")
        print("   1. Add sample teacher data to database")
        print("   2. Check if existing teachers are marked as inactive")
        print("   3. Run database initialization scripts")
        
    elif not api_working:
        print("❌ ISSUE: API endpoint not working")
        print("   Solutions:")
        print("   1. Check server logs for errors")
        print("   2. Verify database connection in backend")
        print("   3. Test teacher CRUD methods")
        
    elif not frontend_would_work:
        print("❌ ISSUE: API returns empty data")
        print("   Solutions:")
        print("   1. Check API endpoint data formatting")
        print("   2. Verify teacher CRUD query filters")
        print("   3. Check if teachers have required fields")
        
    else:
        print("✅ Everything looks good!")
        print("   The Faculty page should display real teacher data")
        print("   If it's still showing mock data, check:")
        print("   1. Browser cache (hard refresh)")
        print("   2. Frontend console for errors")
        print("   3. Network tab in developer tools")


if __name__ == "__main__":
    asyncio.run(main())
