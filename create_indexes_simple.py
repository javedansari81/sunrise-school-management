import asyncio
import sys
sys.path.append('sunrise-backend-fastapi')
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def create_indexes():
    async with AsyncSessionLocal() as session:
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_monthly_fee_tracking_student_session ON monthly_fee_tracking(student_id, session_year_id, academic_month)",
            "CREATE INDEX IF NOT EXISTS idx_monthly_payment_allocations_tracking ON monthly_payment_allocations(monthly_tracking_id)",
            "CREATE INDEX IF NOT EXISTS idx_fee_payments_date ON fee_payments(payment_date)",
            "CREATE INDEX IF NOT EXISTS idx_fee_records_student_session ON fee_records(student_id, session_year_id)",
            "CREATE INDEX IF NOT EXISTS idx_students_class_session ON students(class_id, session_year_id)",
            "CREATE INDEX IF NOT EXISTS idx_monthly_fee_tracking_composite ON monthly_fee_tracking(student_id, session_year_id, academic_month, payment_status_id)"
        ]
        
        constraints = [
            "ALTER TABLE monthly_fee_tracking ADD CONSTRAINT IF NOT EXISTS chk_academic_month_valid CHECK (academic_month >= 1 AND academic_month <= 12)",
            "ALTER TABLE monthly_fee_tracking ADD CONSTRAINT IF NOT EXISTS chk_paid_amount_positive CHECK (paid_amount >= 0)",
            "ALTER TABLE monthly_fee_tracking ADD CONSTRAINT IF NOT EXISTS chk_monthly_amount_positive CHECK (monthly_amount > 0)",
            "ALTER TABLE monthly_payment_allocations ADD CONSTRAINT IF NOT EXISTS chk_allocation_amount_positive CHECK (amount > 0)"
        ]
        
        # Create indexes
        for i, index_sql in enumerate(indexes):
            try:
                print(f"Creating index {i+1}...")
                await session.execute(text(index_sql))
                await session.commit()
                print(f"✅ Index {i+1} created successfully")
            except Exception as e:
                print(f"❌ Error creating index {i+1}: {e}")
                await session.rollback()
        
        # Add constraints
        for i, constraint_sql in enumerate(constraints):
            try:
                print(f"Adding constraint {i+1}...")
                await session.execute(text(constraint_sql))
                await session.commit()
                print(f"✅ Constraint {i+1} added successfully")
            except Exception as e:
                print(f"❌ Error adding constraint {i+1}: {e}")
                await session.rollback()
        
        # Create view
        view_sql = """
        CREATE OR REPLACE VIEW v_student_payment_summary AS
        SELECT 
            s.id as student_id,
            s.first_name || ' ' || s.last_name as student_name,
            s.admission_number,
            c.name as class_name,
            sy.name as session_year,
            COUNT(mft.id) as total_months,
            COUNT(CASE WHEN mft.paid_amount >= mft.monthly_amount THEN 1 END) as paid_months,
            COUNT(CASE WHEN mft.paid_amount > 0 AND mft.paid_amount < mft.monthly_amount THEN 1 END) as partial_months,
            COUNT(CASE WHEN mft.paid_amount = 0 THEN 1 END) as pending_months,
            SUM(mft.monthly_amount) as total_annual_fee,
            SUM(mft.paid_amount) as total_paid,
            SUM(mft.monthly_amount - mft.paid_amount) as total_balance
        FROM students s
        LEFT JOIN classes c ON s.class_id = c.id
        LEFT JOIN session_years sy ON s.session_year_id = sy.id
        LEFT JOIN monthly_fee_tracking mft ON s.id = mft.student_id AND s.session_year_id = mft.session_year_id
        GROUP BY s.id, s.first_name, s.last_name, s.admission_number, c.name, sy.name
        """
        
        try:
            print("Creating payment summary view...")
            await session.execute(text(view_sql))
            await session.commit()
            print("✅ Payment summary view created successfully")
        except Exception as e:
            print(f"❌ Error creating view: {e}")
            await session.rollback()
        
        print("✅ Database optimization completed!")

if __name__ == "__main__":
    asyncio.run(create_indexes())
