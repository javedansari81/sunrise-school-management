import asyncio
import sys
sys.path.append('sunrise-backend-fastapi')
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def debug_student_7():
    async with AsyncSessionLocal() as session:
        try:
            print("🔍 DEBUGGING STUDENT ID 7")
            print("=" * 50)
            
            # Check student details
            student_query = text("""
                SELECT s.id, s.first_name, s.last_name, s.admission_number, 
                       s.class_id, c.name as class_name
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.id
                WHERE s.id = 7
            """)
            result = await session.execute(student_query)
            student = result.fetchone()
            
            if student:
                print(f"✅ Student Found:")
                print(f"   ID: {student[0]}")
                print(f"   Name: {student[1]} {student[2]}")
                print(f"   Admission Number: {student[3]}")
                print(f"   Class ID: {student[4]}")
                print(f"   Class Name: {student[5]}")
            else:
                print("❌ Student ID 7 not found!")
                return
            
            print("\n" + "=" * 50)
            
            # Check fee structures for this class
            if student[4]:  # class_id
                fee_structure_query = text("""
                    SELECT fs.id, fs.class_id, fs.session_year_id, fs.total_annual_fee,
                           c.name as class_name, sy.name as session_year
                    FROM fee_structures fs
                    JOIN classes c ON fs.class_id = c.id
                    JOIN session_years sy ON fs.session_year_id = sy.id
                    WHERE fs.class_id = :class_id
                    ORDER BY fs.session_year_id DESC
                """)
                result = await session.execute(fee_structure_query, {"class_id": student[4]})
                fee_structures = result.fetchall()
                
                print(f"📊 Fee Structures for Class ID {student[4]} ({student[5]}):")
                if fee_structures:
                    for fs in fee_structures:
                        print(f"   Session Year: {fs[5]} | Annual Fee: ₹{fs[3]:,}")
                else:
                    print(f"   ❌ No fee structures found for Class ID {student[4]}")
            
            print("\n" + "=" * 50)
            
            # Check monthly fee tracking for this student
            tracking_query = text("""
                SELECT mft.id, mft.student_id, mft.session_year_id, mft.monthly_amount,
                       sy.name as session_year
                FROM monthly_fee_tracking mft
                JOIN session_years sy ON mft.session_year_id = sy.id
                WHERE mft.student_id = 7
                ORDER BY mft.session_year_id DESC
            """)
            result = await session.execute(tracking_query)
            tracking_records = result.fetchall()
            
            print(f"📋 Monthly Fee Tracking for Student ID 7:")
            if tracking_records:
                for track in tracking_records:
                    print(f"   Session Year: {track[4]} | Monthly Amount: ₹{track[3]:,}")
            else:
                print(f"   ❌ No monthly fee tracking found for Student ID 7")
            
            print("\n" + "=" * 50)
            
            # Check all available fee structures
            all_fee_structures_query = text("""
                SELECT fs.class_id, c.name as class_name, fs.session_year_id, 
                       sy.name as session_year, fs.total_annual_fee
                FROM fee_structures fs
                JOIN classes c ON fs.class_id = c.id
                JOIN session_years sy ON fs.session_year_id = sy.id
                ORDER BY fs.class_id, fs.session_year_id
            """)
            result = await session.execute(all_fee_structures_query)
            all_structures = result.fetchall()
            
            print(f"📊 All Available Fee Structures ({len(all_structures)} total):")
            current_class = None
            for fs in all_structures:
                if fs[0] != current_class:
                    current_class = fs[0]
                    print(f"\n   {fs[1]} (Class ID: {fs[0]}):")
                print(f"     {fs[3]}: ₹{fs[4]:,}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            raise

asyncio.run(debug_student_7())
