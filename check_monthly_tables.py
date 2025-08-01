import asyncio
import sys
sys.path.append('sunrise-backend-fastapi')
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def check_tables():
    async with AsyncSessionLocal() as session:
        # Check for monthly tables
        result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'monthly%' AND table_schema = 'public'"))
        tables = result.fetchall()
        print('Monthly tables found:')
        for table in tables:
            print(f'  - {table[0]}')
        
        # Check if monthly_fee_tracking has data
        try:
            result = await session.execute(text('SELECT COUNT(*) FROM monthly_fee_tracking'))
            count = result.scalar()
            print(f'Monthly fee tracking records: {count}')
        except Exception as e:
            print(f'monthly_fee_tracking table does not exist: {e}')
        
        # Check if monthly_payment_allocations has data
        try:
            result = await session.execute(text('SELECT COUNT(*) FROM monthly_payment_allocations'))
            count = result.scalar()
            print(f'Monthly payment allocation records: {count}')
        except Exception as e:
            print(f'monthly_payment_allocations table does not exist: {e}')

if __name__ == "__main__":
    asyncio.run(check_tables())
