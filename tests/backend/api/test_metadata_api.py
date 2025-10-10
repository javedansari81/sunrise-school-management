"""
Test script to validate the metadata-driven API changes
"""

import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Add the parent directory to the path to access app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.core.database import get_db
from app.models.metadata import UserType, Gender, Class, SessionYear
from app.models.user import User
from app.models.student import Student
from app.crud.metadata import get_all_metadata
from app.crud.crud_user import CRUDUser
from app.crud.crud_student import CRUDStudent


async def test_metadata_tables():
    """Test that metadata tables exist and have data"""
    print("🔍 Testing metadata tables...")
    
    async for db in get_db():
        try:
            # Test UserType
            result = await db.execute(select(UserType))
            user_types = result.scalars().all()
            print(f"✅ UserTypes: {len(user_types)} records")
            for ut in user_types:
                print(f"   - {ut.id}: {ut.name}")
            
            # Test Gender
            result = await db.execute(select(Gender))
            genders = result.scalars().all()
            print(f"✅ Genders: {len(genders)} records")
            for g in genders:
                print(f"   - {g.id}: {g.name}")
            
            # Test Class
            result = await db.execute(select(Class))
            classes = result.scalars().all()
            print(f"✅ Classes: {len(classes)} records")
            for c in classes:
                print(f"   - {c.id}: {c.name} ({c.description})")
            
            # Test SessionYear
            result = await db.execute(select(SessionYear))
            session_years = result.scalars().all()
            print(f"✅ SessionYears: {len(session_years)} records")
            for sy in session_years:
                print(f"   - {sy.id}: {sy.name} (Current: {sy.is_current})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing metadata tables: {e}")
            return False
        finally:
            await db.close()


async def test_metadata_crud():
    """Test metadata CRUD operations"""
    print("\n🔍 Testing metadata CRUD operations...")
    
    async for db in get_db():
        try:
            metadata = get_all_metadata(db)
            
            print(f"✅ Metadata CRUD working:")
            print(f"   - User Types: {len(metadata['user_types'])}")
            print(f"   - Genders: {len(metadata['genders'])}")
            print(f"   - Classes: {len(metadata['classes'])}")
            print(f"   - Session Years: {len(metadata['session_years'])}")
            print(f"   - Payment Types: {len(metadata['payment_types'])}")
            print(f"   - Payment Statuses: {len(metadata['payment_statuses'])}")
            print(f"   - Payment Methods: {len(metadata['payment_methods'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing metadata CRUD: {e}")
            return False
        finally:
            await db.close()


async def test_user_with_metadata():
    """Test user model with metadata relationships"""
    print("\n🔍 Testing user with metadata relationships...")
    
    async for db in get_db():
        try:
            user_crud = CRUDUser()
            
            # Get first user
            result = await db.execute(select(User).limit(1))
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ No users found in database")
                return False
            
            # Get user with metadata
            user_with_metadata = await user_crud.get_with_metadata(db, id=user.id)
            
            if user_with_metadata:
                print(f"✅ User with metadata:")
                print(f"   - ID: {user_with_metadata.id}")
                print(f"   - Email: {user_with_metadata.email}")
                print(f"   - Name: {user_with_metadata.first_name} {user_with_metadata.last_name}")
                print(f"   - User Type ID: {user_with_metadata.user_type_id}")
                if user_with_metadata.user_type:
                    print(f"   - User Type Name: {user_with_metadata.user_type.name}")
                else:
                    print("   - User Type: Not loaded")
                
                return True
            else:
                print("❌ Could not load user with metadata")
                return False
            
        except Exception as e:
            print(f"❌ Error testing user with metadata: {e}")
            return False
        finally:
            await db.close()


async def test_student_with_metadata():
    """Test student model with metadata relationships"""
    print("\n🔍 Testing student with metadata relationships...")
    
    async for db in get_db():
        try:
            student_crud = CRUDStudent()
            
            # Get first student
            result = await db.execute(select(Student).limit(1))
            student = result.scalar_one_or_none()
            
            if not student:
                print("❌ No students found in database")
                return False
            
            # Get student with metadata
            student_with_metadata = await student_crud.get_with_metadata(db, id=student.id)
            
            if student_with_metadata:
                print(f"✅ Student with metadata:")
                print(f"   - ID: {student_with_metadata.id}")
                print(f"   - Admission Number: {student_with_metadata.admission_number}")
                print(f"   - Name: {student_with_metadata.first_name} {student_with_metadata.last_name}")
                print(f"   - Gender ID: {student_with_metadata.gender_id}")
                if student_with_metadata.gender:
                    print(f"   - Gender Name: {student_with_metadata.gender.name}")
                print(f"   - Class ID: {student_with_metadata.class_id}")
                if student_with_metadata.class_ref:
                    print(f"   - Class Name: {student_with_metadata.class_ref.description}")
                print(f"   - Session Year ID: {student_with_metadata.session_year_id}")
                if student_with_metadata.session_year:
                    print(f"   - Session Year: {student_with_metadata.session_year.name}")
                
                return True
            else:
                print("❌ Could not load student with metadata")
                return False
            
        except Exception as e:
            print(f"❌ Error testing student with metadata: {e}")
            return False
        finally:
            await db.close()


async def test_schema_conversion():
    """Test schema conversion with metadata"""
    print("\n🔍 Testing schema conversion with metadata...")
    
    async for db in get_db():
        try:
            from app.schemas.user import User as UserSchema
            from app.schemas.student import Student as StudentSchema
            
            user_crud = CRUDUser()
            student_crud = CRUDStudent()
            
            # Test user schema conversion
            result = await db.execute(select(User).limit(1))
            user = result.scalar_one_or_none()
            
            if user:
                user_with_metadata = await user_crud.get_with_metadata(db, id=user.id)
                user_schema = UserSchema.from_orm_with_metadata(user_with_metadata)
                print(f"✅ User schema conversion:")
                print(f"   - User Type Name: {user_schema.user_type_name}")
            
            # Test student schema conversion
            result = await db.execute(select(Student).limit(1))
            student = result.scalar_one_or_none()
            
            if student:
                student_with_metadata = await student_crud.get_with_metadata(db, id=student.id)
                student_schema = StudentSchema.from_orm_with_metadata(student_with_metadata)
                print(f"✅ Student schema conversion:")
                print(f"   - Gender Name: {student_schema.gender_name}")
                print(f"   - Class Name: {student_schema.class_name}")
                print(f"   - Session Year: {student_schema.session_year_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing schema conversion: {e}")
            return False
        finally:
            await db.close()


async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Metadata-Driven API Tests\n")
    
    tests = [
        ("Metadata Tables", test_metadata_tables),
        ("Metadata CRUD", test_metadata_crud),
        ("User with Metadata", test_user_with_metadata),
        ("Student with Metadata", test_student_with_metadata),
        ("Schema Conversion", test_schema_conversion),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Metadata-driven API is working correctly!")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(run_all_tests())
