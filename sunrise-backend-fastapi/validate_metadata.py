"""
Simple validation script for metadata-driven API
"""

def test_imports():
    """Test that all imports work correctly"""
    print("🔍 Testing imports...")
    
    try:
        # Test metadata models
        from app.models.metadata import UserType, Gender, Class, SessionYear
        print("✅ Metadata models imported")
        
        # Test updated models
        from app.models.user import User
        from app.models.student import Student
        from app.models.teacher import Teacher
        print("✅ Updated models imported")
        
        # Test schemas
        from app.schemas.metadata import ConfigurationResponse
        from app.schemas.user import User as UserSchema
        from app.schemas.student import Student as StudentSchema
        print("✅ Updated schemas imported")
        
        # Test CRUD
        from app.crud.metadata import get_all_metadata
        from app.crud.crud_user import CRUDUser
        from app.crud.crud_student import CRUDStudent
        print("✅ Updated CRUD imported")
        
        # Test endpoints
        from app.api.v1.endpoints.configuration import get_metadata_configuration
        from app.api.v1.endpoints.users import get_users
        from app.api.v1.endpoints.students import get_students
        print("✅ Updated endpoints imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_model_structure():
    """Test that models have the correct structure"""
    print("\n🔍 Testing model structure...")
    
    try:
        from app.models.user import User
        from app.models.student import Student
        from app.models.teacher import Teacher
        
        # Check User model has user_type_id
        user_columns = [col.name for col in User.__table__.columns]
        if 'user_type_id' in user_columns:
            print("✅ User model has user_type_id")
        else:
            print("❌ User model missing user_type_id")
            return False
        
        # Check Student model has metadata foreign keys
        student_columns = [col.name for col in Student.__table__.columns]
        required_student_fks = ['gender_id', 'class_id', 'session_year_id']
        for fk in required_student_fks:
            if fk in student_columns:
                print(f"✅ Student model has {fk}")
            else:
                print(f"❌ Student model missing {fk}")
                return False
        
        # Check Teacher model has metadata foreign keys
        teacher_columns = [col.name for col in Teacher.__table__.columns]
        required_teacher_fks = ['gender_id', 'qualification_id', 'employment_status_id']
        for fk in required_teacher_fks:
            if fk in teacher_columns:
                print(f"✅ Teacher model has {fk}")
            else:
                print(f"❌ Teacher model missing {fk}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Model structure error: {e}")
        return False


def test_schema_methods():
    """Test that schemas have the required methods"""
    print("\n🔍 Testing schema methods...")
    
    try:
        from app.schemas.user import User as UserSchema
        from app.schemas.student import Student as StudentSchema
        
        # Check if schemas have from_orm_with_metadata method
        if hasattr(UserSchema, 'from_orm_with_metadata'):
            print("✅ UserSchema has from_orm_with_metadata method")
        else:
            print("❌ UserSchema missing from_orm_with_metadata method")
            return False
        
        if hasattr(StudentSchema, 'from_orm_with_metadata'):
            print("✅ StudentSchema has from_orm_with_metadata method")
        else:
            print("❌ StudentSchema missing from_orm_with_metadata method")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Schema methods error: {e}")
        return False


def test_crud_methods():
    """Test that CRUD classes have the required methods"""
    print("\n🔍 Testing CRUD methods...")
    
    try:
        from app.crud.crud_user import CRUDUser
        from app.crud.crud_student import CRUDStudent
        
        user_crud = CRUDUser()
        student_crud = CRUDStudent()
        
        # Check if CRUD classes have metadata methods
        if hasattr(user_crud, 'get_with_metadata'):
            print("✅ CRUDUser has get_with_metadata method")
        else:
            print("❌ CRUDUser missing get_with_metadata method")
            return False
        
        if hasattr(student_crud, 'get_with_metadata'):
            print("✅ CRUDStudent has get_with_metadata method")
        else:
            print("❌ CRUDStudent missing get_with_metadata method")
            return False
        
        if hasattr(student_crud, 'create_with_validation'):
            print("✅ CRUDStudent has create_with_validation method")
        else:
            print("❌ CRUDStudent missing create_with_validation method")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ CRUD methods error: {e}")
        return False


def run_validation():
    """Run all validation tests"""
    print("🚀 Starting Metadata-Driven API Validation\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Model Structure", test_model_structure),
        ("Schema Methods", test_schema_methods),
        ("CRUD Methods", test_crud_methods),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 VALIDATION RESULTS")
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
        print("🎉 All validation tests passed!")
        print("✅ Metadata-driven API structure is correct!")
        print("\n📋 NEXT STEPS:")
        print("1. Run the database setup scripts to create metadata tables")
        print("2. Load initial data using Database/Init/02_load_initial_data_clean.sql")
        print("3. Start the FastAPI server: uvicorn app.main:app --reload")
        print("4. Test the /api/v1/configuration/ endpoint")
    else:
        print("⚠️  Some validation tests failed. Please fix the issues above.")
    
    return passed == total


if __name__ == "__main__":
    run_validation()
