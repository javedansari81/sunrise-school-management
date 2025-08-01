import asyncio
import sys
sys.path.append('sunrise-backend-fastapi')
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

# Fee structure data for 2025-26 session year
fee_structures_data = [
    # Class ID, Session Year ID, Tuition Fee, Admission Fee, Development Fee, Activity Fee, Transport Fee, Library Fee, Lab Fee, Exam Fee, Other Fee
    (1, 4, 8000, 1000, 2000, 1000, 3000, 500, 0, 1000, 500),      # PG - ₹17,000
    (2, 4, 10000, 1000, 2000, 1000, 3000, 500, 0, 1000, 500),     # NURSERY - ₹19,000
    (3, 4, 12000, 1000, 2000, 1000, 3000, 500, 0, 1000, 500),     # LKG - ₹21,000
    (4, 4, 14000, 1000, 2000, 1000, 3000, 500, 0, 1000, 500),     # UKG - ₹23,000
    (5, 4, 16000, 1000, 2000, 1000, 3000, 500, 0, 1000, 500),     # CLASS_1 - ₹25,000
    (6, 4, 18000, 1000, 2000, 1000, 3000, 500, 0, 1000, 500),     # CLASS_2 - ₹27,000
    (7, 4, 20000, 1000, 2000, 1000, 3000, 500, 0, 1000, 500),     # CLASS_3 - ₹29,000
    (8, 4, 22000, 1000, 2000, 1000, 3000, 500, 0, 1000, 500),     # CLASS_4 - ₹31,000
    (9, 4, 24000, 1000, 2000, 1000, 3000, 500, 0, 1000, 500),     # CLASS_5 - ₹33,000
    (10, 4, 26000, 1000, 2000, 1000, 3000, 500, 500, 1000, 500),  # CLASS_6 - ₹35,500
    (11, 4, 28000, 1000, 2000, 1000, 3000, 500, 500, 1000, 500),  # CLASS_7 - ₹37,500
    (12, 4, 30000, 1000, 2000, 1000, 3000, 500, 500, 1000, 500),  # CLASS_8 - ₹39,500
    (13, 4, 32000, 1000, 2000, 1000, 3000, 500, 1000, 1000, 500), # CLASS_9 - ₹42,000
    (14, 4, 34000, 1000, 2000, 1000, 3000, 500, 1000, 1000, 500), # CLASS_10 - ₹44,000
    (15, 4, 36000, 1000, 2000, 1000, 3000, 500, 1000, 1000, 500), # CLASS_11 - ₹46,000
]

async def create_fee_structures():
    async with AsyncSessionLocal() as session:
        try:
            print("Creating fee structures for 2025-26 session year...")
            
            for data in fee_structures_data:
                class_id, session_year_id, tuition_fee, admission_fee, development_fee, activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee = data
                
                # Calculate total annual fee
                total_annual_fee = tuition_fee + admission_fee + development_fee + activity_fee + transport_fee + library_fee + lab_fee + exam_fee + other_fee
                
                # Check if fee structure already exists
                check_query = text("""
                    SELECT id FROM fee_structures 
                    WHERE class_id = :class_id AND session_year_id = :session_year_id
                """)
                result = await session.execute(check_query, {
                    "class_id": class_id,
                    "session_year_id": session_year_id
                })
                existing = result.fetchone()
                
                if existing:
                    print(f"  Fee structure already exists for Class ID {class_id}, Session Year ID {session_year_id}")
                    continue
                
                # Insert new fee structure
                insert_query = text("""
                    INSERT INTO fee_structures (
                        class_id, session_year_id, tuition_fee, admission_fee, development_fee,
                        activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee,
                        total_annual_fee, created_at, updated_at
                    ) VALUES (
                        :class_id, :session_year_id, :tuition_fee, :admission_fee, :development_fee,
                        :activity_fee, :transport_fee, :library_fee, :lab_fee, :exam_fee, :other_fee,
                        :total_annual_fee, NOW(), NOW()
                    )
                """)
                
                await session.execute(insert_query, {
                    "class_id": class_id,
                    "session_year_id": session_year_id,
                    "tuition_fee": tuition_fee,
                    "admission_fee": admission_fee,
                    "development_fee": development_fee,
                    "activity_fee": activity_fee,
                    "transport_fee": transport_fee,
                    "library_fee": library_fee,
                    "lab_fee": lab_fee,
                    "exam_fee": exam_fee,
                    "other_fee": other_fee,
                    "total_annual_fee": total_annual_fee
                })
                
                # Get class name
                class_query = text("SELECT name FROM classes WHERE id = :class_id")
                class_result = await session.execute(class_query, {"class_id": class_id})
                class_name = class_result.scalar()
                
                print(f"  ✅ Created fee structure for {class_name}: ₹{total_annual_fee:,}")
            
            await session.commit()
            print("\n🎉 Fee structures created successfully!")
            
            # Show summary
            summary_query = text("""
                SELECT c.name, fs.total_annual_fee 
                FROM fee_structures fs
                JOIN classes c ON fs.class_id = c.id
                WHERE fs.session_year_id = 4
                ORDER BY c.id
            """)
            result = await session.execute(summary_query)
            fee_structures = result.fetchall()
            
            print(f"\n📊 Fee Structures for 2025-26 Session Year:")
            for class_name, total_fee in fee_structures:
                monthly_fee = total_fee / 12
                print(f"  {class_name}: ₹{total_fee:,}/year (₹{monthly_fee:,.0f}/month)")
                
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating fee structures: {e}")
            raise

asyncio.run(create_fee_structures())
