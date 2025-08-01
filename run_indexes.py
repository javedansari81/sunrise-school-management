import asyncio
import sys
sys.path.append('sunrise-backend-fastapi')
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def run_indexes():
    async with AsyncSessionLocal() as session:
        # Read the SQL file
        with open('Database/Versioning/07_enhanced_monthly_payment_indexes.sql', 'r') as f:
            sql_content = f.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        for i, statement in enumerate(statements):
            if statement:
                try:
                    print(f"Executing statement {i+1}: {statement[:50]}...")
                    await session.execute(text(statement))
                    await session.commit()
                    print(f"✅ Statement {i+1} executed successfully")
                except Exception as e:
                    print(f"❌ Error in statement {i+1}: {e}")
                    await session.rollback()
        
        print("✅ All index creation completed!")

if __name__ == "__main__":
    asyncio.run(run_indexes())
