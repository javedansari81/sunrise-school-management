"""
Integration test script to demonstrate soft-delete validation functionality
This script shows the complete workflow of creating, soft-deleting, and recreating records
"""
import asyncio
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_teacher import teacher_crud
from app.crud.crud_student import student_crud
from app.schemas.teacher import TeacherCreate
from app.schemas.student import StudentCreate
from app.utils.soft_delete_helpers import (
    validate_teacher_creation_with_soft_delete_check,
    validate_student_creation_with_soft_delete_check
)


async def demonstrate_teacher_soft_delete_workflow():
    """Demonstrate the complete teacher soft-delete workflow"""
    print("\n=== TEACHER SOFT-DELETE WORKFLOW DEMONSTRATION ===")
    
    # Get database session
    async for db in get_db():
        try:
            print("\n1. Creating initial teacher...")
            
            # Create a teacher
            teacher_data = TeacherCreate(
                employee_id="DEMO_EMP_001",
                first_name="John",
                last_name="Doe",
                email="john.doe@demo.com",
                phone="1234567890",
                position="Math Teacher",
                joining_date=date.today()
            )
            
            teacher = await teacher_crud.create_with_user_account(db, obj_in=teacher_data)
            print(f"✓ Created teacher: {teacher.first_name} {teacher.last_name} (ID: {teacher.employee_id})")
            
            print("\n2. Verifying duplicate validation blocks creation...")
            
            # Try to create another teacher with same employee ID (should fail)
            can_create, success_msg, error_msg = await validate_teacher_creation_with_soft_delete_check(
                db, "DEMO_EMP_001", "different@email.com"
            )
            
            print(f"✓ Validation result: can_create={can_create}, error='{error_msg}'")
            assert can_create is False
            assert "already exists" in error_msg
            
            print("\n3. Soft-deleting the teacher...")
            
            # Soft delete the teacher
            deleted_teacher = await teacher_crud.remove(db, id=teacher.id)
            print(f"✓ Soft-deleted teacher: is_deleted={deleted_teacher.is_deleted}")
            
            print("\n4. Verifying teacher is excluded from normal queries...")
            
            # Try to find the teacher (should not be found)
            found_teacher = await teacher_crud.get_by_employee_id(db, employee_id="DEMO_EMP_001")
            print(f"✓ Teacher lookup result: {found_teacher}")
            assert found_teacher is None
            
            print("\n5. Creating new teacher with same employee ID...")
            
            # Now create a new teacher with the same employee ID (should succeed)
            can_create, success_msg, error_msg = await validate_teacher_creation_with_soft_delete_check(
                db, "DEMO_EMP_001", "jane.smith@demo.com"
            )
            
            print(f"✓ Validation result: can_create={can_create}")
            print(f"✓ Success message: '{success_msg}'")
            assert can_create is True
            assert success_msg is not None
            assert "John Doe" in success_msg
            assert "archived" in success_msg
            
            # Create the new teacher
            new_teacher_data = TeacherCreate(
                employee_id="DEMO_EMP_001",
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@demo.com",
                phone="0987654321",
                position="Science Teacher",
                joining_date=date.today()
            )
            
            new_teacher = await teacher_crud.create_with_user_account(db, obj_in=new_teacher_data)
            print(f"✓ Created new teacher: {new_teacher.first_name} {new_teacher.last_name}")
            print(f"✓ Same employee ID: {new_teacher.employee_id}")
            
            print("\n6. Cleanup...")
            # Clean up the demo data
            await teacher_crud.remove(db, id=new_teacher.id)
            print("✓ Cleaned up demo data")
            
        except Exception as e:
            print(f"❌ Error in teacher workflow: {e}")
            raise
        finally:
            await db.close()
            break


async def demonstrate_student_soft_delete_workflow():
    """Demonstrate the complete student soft-delete workflow"""
    print("\n=== STUDENT SOFT-DELETE WORKFLOW DEMONSTRATION ===")
    
    # Get database session
    async for db in get_db():
        try:
            print("\n1. Creating initial student...")
            
            # Create a student
            student_data = StudentCreate(
                admission_number="DEMO_ADM_001",
                first_name="Alice",
                last_name="Johnson",
                date_of_birth=date(2010, 5, 15),
                gender_id=1,  # Assuming 1 = Female
                class_id=1,   # Assuming class exists
                session_year_id=1,  # Assuming session year exists
                father_name="Robert Johnson",
                mother_name="Mary Johnson",
                admission_date=date.today(),
                email="alice.johnson@demo.com"
            )
            
            student = await student_crud.create_with_validation(db, obj_in=student_data)
            print(f"✓ Created student: {student.first_name} {student.last_name} (Admission: {student.admission_number})")
            
            print("\n2. Verifying duplicate validation blocks creation...")
            
            # Try to create another student with same admission number (should fail)
            can_create, success_msg, error_msg = await validate_student_creation_with_soft_delete_check(
                db, "DEMO_ADM_001", "different@email.com"
            )
            
            print(f"✓ Validation result: can_create={can_create}, error='{error_msg}'")
            assert can_create is False
            assert "already exists" in error_msg
            
            print("\n3. Soft-deleting the student...")
            
            # Soft delete the student
            deleted_student = await student_crud.remove(db, id=student.id)
            print(f"✓ Soft-deleted student: is_deleted={deleted_student.is_deleted}")
            
            print("\n4. Verifying student is excluded from normal queries...")
            
            # Try to find the student (should not be found)
            found_student = await student_crud.get_by_admission_number(db, admission_number="DEMO_ADM_001")
            print(f"✓ Student lookup result: {found_student}")
            assert found_student is None
            
            print("\n5. Creating new student with same admission number...")
            
            # Now create a new student with the same admission number (should succeed)
            can_create, success_msg, error_msg = await validate_student_creation_with_soft_delete_check(
                db, "DEMO_ADM_001", "bob.wilson@demo.com"
            )
            
            print(f"✓ Validation result: can_create={can_create}")
            print(f"✓ Success message: '{success_msg}'")
            assert can_create is True
            assert success_msg is not None
            assert "Alice Johnson" in success_msg
            assert "archived" in success_msg
            
            # Create the new student
            new_student_data = StudentCreate(
                admission_number="DEMO_ADM_001",
                first_name="Bob",
                last_name="Wilson",
                date_of_birth=date(2011, 3, 20),
                gender_id=2,  # Assuming 2 = Male
                class_id=2,   # Different class
                session_year_id=1,
                father_name="David Wilson",
                mother_name="Sarah Wilson",
                admission_date=date.today(),
                email="bob.wilson@demo.com"
            )
            
            new_student = await student_crud.create_with_validation(db, obj_in=new_student_data)
            print(f"✓ Created new student: {new_student.first_name} {new_student.last_name}")
            print(f"✓ Same admission number: {new_student.admission_number}")
            
            print("\n6. Cleanup...")
            # Clean up the demo data
            await student_crud.remove(db, id=new_student.id)
            print("✓ Cleaned up demo data")
            
        except Exception as e:
            print(f"❌ Error in student workflow: {e}")
            raise
        finally:
            await db.close()
            break


async def demonstrate_email_validation_workflow():
    """Demonstrate email validation with soft-deleted records"""
    print("\n=== EMAIL VALIDATION WORKFLOW DEMONSTRATION ===")
    
    # Get database session
    async for db in get_db():
        try:
            print("\n1. Creating teacher with specific email...")
            
            teacher_data = TeacherCreate(
                employee_id="DEMO_EMAIL_001",
                first_name="Email",
                last_name="Test",
                email="email.test@demo.com",
                phone="5555555555",
                position="Test Teacher",
                joining_date=date.today()
            )
            
            teacher = await teacher_crud.create_with_user_account(db, obj_in=teacher_data)
            print(f"✓ Created teacher with email: {teacher.email}")
            
            print("\n2. Soft-deleting teacher...")
            deleted_teacher = await teacher_crud.remove(db, id=teacher.id)
            print(f"✓ Soft-deleted teacher")
            
            print("\n3. Creating new teacher with same email...")
            
            # Validate creation with same email (should succeed)
            can_create, success_msg, error_msg = await validate_teacher_creation_with_soft_delete_check(
                db, "DEMO_EMAIL_002", "email.test@demo.com"
            )
            
            print(f"✓ Validation result: can_create={can_create}")
            print(f"✓ Success message: '{success_msg}'")
            assert can_create is True
            assert "email email.test@demo.com" in success_msg
            
            print("\n4. Cleanup...")
            print("✓ Demo completed successfully")
            
        except Exception as e:
            print(f"❌ Error in email workflow: {e}")
            raise
        finally:
            await db.close()
            break


async def main():
    """Run all demonstration workflows"""
    print("🚀 Starting Soft-Delete Validation Demonstration")
    print("=" * 60)
    
    try:
        await demonstrate_teacher_soft_delete_workflow()
        await demonstrate_student_soft_delete_workflow()
        await demonstrate_email_validation_workflow()
        
        print("\n" + "=" * 60)
        print("✅ ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("\nKey Features Demonstrated:")
        print("• Soft-deleted records are excluded from duplicate validation")
        print("• New records can be created with same identifiers as soft-deleted ones")
        print("• Appropriate success messages are generated when replacing archived records")
        print("• Email validation also considers soft-deleted records")
        print("• Both teacher and student workflows work correctly")
        
    except Exception as e:
        print(f"\n❌ DEMONSTRATION FAILED: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
