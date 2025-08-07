#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sunrise-backend-fastapi'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def debug_student_35():
    async with AsyncSessionLocal() as session:
        try:
            print("🔍 DEBUGGING STUDENT ID 35")
            print("=" * 50)
            
            # Check student details
            student_query = text("""
                SELECT s.id, s.first_name, s.last_name, s.admission_number, 
                       s.class_id, s.session_year_id,
                       c.name as class_name, sy.name as session_year_name
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.id
                LEFT JOIN session_years sy ON s.session_year_id = sy.id
                WHERE s.id = 35
            """)
            result = await session.execute(student_query)
            student = result.fetchone()
            
            if student:
                print(f"✅ Student Found:")
                print(f"   ID: {student[0]}")
                print(f"   Name: {student[1]} {student[2]}")
                print(f"   Admission Number: {student[3]}")
                print(f"   Class ID: {student[4]} ({student[6]})")
                print(f"   Session Year ID: {student[5]} ({student[7]})")
            else:
                print("❌ Student ID 35 not found!")
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
                
                print(f"📊 Fee Structures for Class ID {student[4]} ({student[6]}):")
                if fee_structures:
                    for fs in fee_structures:
                        print(f"   Session Year: {fs[5]} (ID: {fs[2]}) | Annual Fee: ₹{fs[3]:,}")
                else:
                    print(f"   ❌ No fee structures found for Class ID {student[4]}")
            
            print("\n" + "=" * 50)
            
            # Check for session year 4 specifically
            session_4_query = text("""
                SELECT fs.id, fs.class_id, fs.session_year_id, fs.total_annual_fee,
                       c.name as class_name, sy.name as session_year
                FROM fee_structures fs
                JOIN classes c ON fs.class_id = c.id
                JOIN session_years sy ON fs.session_year_id = sy.id
                WHERE fs.class_id = :class_id AND fs.session_year_id = 4
            """)
            result = await session.execute(session_4_query, {"class_id": student[4]})
            session_4_structure = result.fetchone()
            
            print(f"🎯 Fee Structure for Class ID {student[4]} and Session Year ID 4:")
            if session_4_structure:
                print(f"   ✅ Found: Session {session_4_structure[5]} | Annual Fee: ₹{session_4_structure[3]:,}")
            else:
                print(f"   ❌ No fee structure found for Class ID {student[4]} and Session Year ID 4")
            
            print("\n" + "=" * 50)
            
            # Check all available fee structures
            all_fee_structures_query = text("""
                SELECT fs.class_id, c.name as class_name, fs.session_year_id, 
                       sy.name as session_year, COUNT(*) as count
                FROM fee_structures fs
                JOIN classes c ON fs.class_id = c.id
                JOIN session_years sy ON fs.session_year_id = sy.id
                GROUP BY fs.class_id, c.name, fs.session_year_id, sy.name
                ORDER BY fs.class_id, fs.session_year_id
            """)
            result = await session.execute(all_fee_structures_query)
            all_structures = result.fetchall()
            
            print(f"📊 All Available Fee Structures ({len(all_structures)} combinations):")
            current_class = None
            for fs in all_structures:
                if fs[0] != current_class:
                    current_class = fs[0]
                    print(f"\n   {fs[1]} (Class ID: {fs[0]}):")
                print(f"     {fs[3]} (ID: {fs[2]})")
            
            print("\n" + "=" * 50)
            
            # Check session years table
            session_years_query = text("""
                SELECT id, name, is_current, is_active
                FROM session_years
                ORDER BY id
            """)
            result = await session.execute(session_years_query)
            session_years = result.fetchall()
            
            print(f"📅 Available Session Years:")
            for sy in session_years:
                current_marker = " (CURRENT)" if sy[2] else ""
                active_marker = " (ACTIVE)" if sy[3] else " (INACTIVE)"
                print(f"   ID: {sy[0]} | Name: {sy[1]}{current_marker}{active_marker}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(debug_student_35())
