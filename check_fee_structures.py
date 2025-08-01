import asyncio
import sys
sys.path.append('sunrise-backend-fastapi')
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def check_fee_structures():
    async with AsyncSessionLocal() as session:
        # Check fee structures table
        result = await session.execute(text("SELECT * FROM fee_structures LIMIT 10"))
        fee_structures = result.fetchall()
        print(f"Fee structures found: {len(fee_structures)}")
        
        if fee_structures:
            print("\nExisting fee structures:")
            for fs in fee_structures:
                print(f"  ID: {fs[0]}, Class ID: {fs[1]}, Session Year ID: {fs[2]}, Total Annual Fee: {fs[12]}")
        else:
            print("No fee structures found in database!")
        
        # Check classes
        result = await session.execute(text("SELECT id, name FROM classes ORDER BY id LIMIT 15"))
        classes = result.fetchall()
        print(f"\nClasses found: {len(classes)}")
        for cls in classes:
            print(f"  Class ID: {cls[0]}, Name: {cls[1]}")
        
        # Check session years
        result = await session.execute(text("SELECT id, name FROM session_years ORDER BY id"))
        session_years = result.fetchall()
        print(f"\nSession years found: {len(session_years)}")
        for sy in session_years:
            print(f"  Session Year ID: {sy[0]}, Name: {sy[1]}")

asyncio.run(check_fee_structures())
