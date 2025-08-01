#!/usr/bin/env python3
"""
Create test data for monthly fee tracking
"""
import asyncio
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date, datetime

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.models.fee import FeeRecord, MonthlyFeeTracking
from app.models.student import Student
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload


async def enable_monthly_tracking_for_students():
    """Enable monthly tracking for test students and create monthly records"""
    print("🚀 Creating monthly tracking test data...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Get all fee records for 2025-26 session
            fee_records_result = await session.execute(
                select(FeeRecord)
                .options(selectinload(FeeRecord.student))
                .where(FeeRecord.session_year_id == 4)  # 2025-26
            )
            fee_records = fee_records_result.scalars().all()
            
            if not fee_records:
                print("❌ No fee records found for 2025-26 session")
                return
            
            print(f"Found {len(fee_records)} fee records for 2025-26")
            
            # Enable monthly tracking for all fee records
            for fee_record in fee_records:
                print(f"Enabling monthly tracking for {fee_record.student.first_name} {fee_record.student.last_name}")
                
                # Update fee record to enable monthly tracking
                await session.execute(
                    update(FeeRecord)
                    .where(FeeRecord.id == fee_record.id)
                    .values(is_monthly_tracked=True)
                )
                
                # Create monthly tracking records (April to March)
                monthly_amount = Decimal('750.00')  # ₹750 per month (₹9000 / 12)
                
                months_data = [
                    (4, 2025, 'April', date(2025, 4, 30)),
                    (5, 2025, 'May', date(2025, 5, 31)),
                    (6, 2025, 'June', date(2025, 6, 30)),
                    (7, 2025, 'July', date(2025, 7, 31)),
                    (8, 2025, 'August', date(2025, 8, 31)),
                    (9, 2025, 'September', date(2025, 9, 30)),
                    (10, 2025, 'October', date(2025, 10, 31)),
                    (11, 2025, 'November', date(2025, 11, 30)),
                    (12, 2025, 'December', date(2025, 12, 31)),
                    (1, 2026, 'January', date(2026, 1, 31)),
                    (2, 2026, 'February', date(2026, 2, 28)),
                    (3, 2026, 'March', date(2026, 3, 31)),
                ]
                
                for month, year, month_name, due_date in months_data:
                    # Check if monthly record already exists
                    existing_record = await session.execute(
                        select(MonthlyFeeTracking)
                        .where(
                            MonthlyFeeTracking.fee_record_id == fee_record.id,
                            MonthlyFeeTracking.academic_month == month,
                            MonthlyFeeTracking.academic_year == year
                        )
                    )
                    
                    if existing_record.scalar_one_or_none():
                        continue  # Skip if already exists
                    
                    # Determine payment status and amounts based on month
                    payment_status_id = 1  # Default: Pending
                    paid_amount = Decimal('0.00')
                    
                    # Make some months paid for testing
                    if month in [4, 5]:  # April and May paid
                        payment_status_id = 3  # Paid
                        paid_amount = monthly_amount
                    elif month == 6:  # June partially paid
                        payment_status_id = 2  # Partial
                        paid_amount = Decimal('400.00')
                    elif month == 7 and due_date < date.today():  # July overdue
                        payment_status_id = 4  # Overdue
                    
                    monthly_record = MonthlyFeeTracking(
                        fee_record_id=fee_record.id,
                        student_id=fee_record.student_id,
                        session_year_id=fee_record.session_year_id,
                        academic_month=month,
                        academic_year=year,
                        month_name=month_name,
                        monthly_amount=monthly_amount,
                        paid_amount=paid_amount,
                        due_date=due_date,
                        payment_status_id=payment_status_id,
                        late_fee=Decimal('50.00') if payment_status_id == 4 else Decimal('0.00'),
                        discount_amount=Decimal('0.00'),
                        created_at=datetime.now()
                    )
                    
                    session.add(monthly_record)
            
            await session.commit()
            
            print("\n✅ Monthly tracking test data created successfully!")
            
            # Verify the data
            verification_query = await session.execute(
                select(MonthlyFeeTracking)
                .options(selectinload(MonthlyFeeTracking.fee_record))
                .where(MonthlyFeeTracking.session_year_id == 4)
            )
            monthly_records = verification_query.scalars().all()
            
            print(f"\n📊 Created {len(monthly_records)} monthly tracking records")
            
            # Group by student and show summary
            student_summaries = {}
            for record in monthly_records:
                student_id = record.student_id
                if student_id not in student_summaries:
                    student_summaries[student_id] = {
                        'total_months': 0,
                        'paid_months': 0,
                        'partial_months': 0,
                        'overdue_months': 0,
                        'pending_months': 0,
                        'total_paid': Decimal('0.00')
                    }
                
                student_summaries[student_id]['total_months'] += 1
                student_summaries[student_id]['total_paid'] += record.paid_amount
                
                if record.payment_status_id == 3:  # Paid
                    student_summaries[student_id]['paid_months'] += 1
                elif record.payment_status_id == 2:  # Partial
                    student_summaries[student_id]['partial_months'] += 1
                elif record.payment_status_id == 4:  # Overdue
                    student_summaries[student_id]['overdue_months'] += 1
                else:  # Pending
                    student_summaries[student_id]['pending_months'] += 1
            
            print("\n📈 Student Summary:")
            for student_id, summary in student_summaries.items():
                print(f"  Student {student_id}: {summary['total_months']} months, "
                      f"{summary['paid_months']} paid, {summary['partial_months']} partial, "
                      f"{summary['overdue_months']} overdue, {summary['pending_months']} pending, "
                      f"₹{summary['total_paid']} collected")
            
        except Exception as e:
            print(f"❌ Error creating monthly tracking test data: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(enable_monthly_tracking_for_students())
