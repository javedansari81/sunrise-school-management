#!/usr/bin/env python3
"""
Create test fee data for enhanced fee management testing
"""
import asyncio
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date, datetime

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.models.student import Student
from app.models.fee import FeeStructure, FeeRecord
from sqlalchemy import select
from sqlalchemy.orm import selectinload


async def create_fee_structures(session):
    """Create fee structures for different classes"""
    print("Creating fee structures...")
    
    # Check if fee structures already exist
    existing = await session.execute(select(FeeStructure).limit(1))
    if existing.scalar_one_or_none():
        print("✅ Fee structures already exist, skipping creation")
        return
    
    fee_structures = [
        {
            "class_id": 1,  # Assuming class ID 1 exists
            "session_year_id": 4,  # 2025-26
            "tuition_fee": Decimal('5000.00'),
            "admission_fee": Decimal('1000.00'),
            "development_fee": Decimal('500.00'),
            "activity_fee": Decimal('300.00'),
            "transport_fee": Decimal('800.00'),
            "library_fee": Decimal('200.00'),
            "lab_fee": Decimal('400.00'),
            "exam_fee": Decimal('300.00'),
            "other_fee": Decimal('500.00'),
            "total_annual_fee": Decimal('9000.00'),
            "created_at": datetime.now()
        },
        {
            "class_id": 2,  # Assuming class ID 2 exists
            "session_year_id": 4,  # 2025-26
            "tuition_fee": Decimal('5500.00'),
            "admission_fee": Decimal('1000.00'),
            "development_fee": Decimal('500.00'),
            "activity_fee": Decimal('300.00'),
            "transport_fee": Decimal('800.00'),
            "library_fee": Decimal('200.00'),
            "lab_fee": Decimal('400.00'),
            "exam_fee": Decimal('300.00'),
            "other_fee": Decimal('500.00'),
            "total_annual_fee": Decimal('9500.00'),
            "created_at": datetime.now()
        }
    ]
    
    for fee_data in fee_structures:
        fee_structure = FeeStructure(**fee_data)
        session.add(fee_structure)
    
    await session.commit()
    print("✅ Fee structures created successfully")


async def create_fee_records(session):
    """Create fee records for test students"""
    print("Creating fee records...")
    
    # Check if fee records already exist
    existing = await session.execute(select(FeeRecord).limit(1))
    if existing.scalar_one_or_none():
        print("✅ Fee records already exist, skipping creation")
        return
    
    # Get all students
    students_result = await session.execute(
        select(Student).options(selectinload(Student.class_ref))
        .where(Student.is_active == True)
    )
    students = students_result.scalars().all()
    
    if not students:
        print("❌ No students found. Please create students first.")
        return
    
    print(f"Found {len(students)} students")
    
    # Create fee records for each student
    for student in students:
        print(f"Creating fee record for {student.first_name} {student.last_name}")
        
        fee_record = FeeRecord(
            student_id=student.id,
            session_year_id=4,  # 2025-26
            payment_type_id=1,  # Monthly (assuming ID 1 exists)
            total_amount=Decimal('9000.00'),  # Annual fee
            paid_amount=Decimal('0.00'),
            balance_amount=Decimal('9000.00'),
            payment_status_id=1,  # Pending (assuming ID 1 exists)
            due_date=date(2025, 4, 30),  # April 30, 2025
            created_at=datetime.now()
        )
        session.add(fee_record)
    
    await session.commit()
    print("✅ Fee records created successfully")


async def main():
    """Main function to create fee test data"""
    print("🚀 Creating fee test data for enhanced fee management...")
    
    async with AsyncSessionLocal() as session:
        try:
            await create_fee_structures(session)
            await create_fee_records(session)
            
            print("\n🎉 Fee test data creation completed successfully!")
            print("\n📊 Created Data:")
            print("- Fee structures for different classes")
            print("- Fee records for all active students")
            print("- Annual fee amount: ₹9,000")
            print("- Monthly fee amount: ₹750")
            
        except Exception as e:
            print(f"❌ Fee test data creation failed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
