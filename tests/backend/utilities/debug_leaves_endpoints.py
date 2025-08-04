#!/usr/bin/env python3
"""
Debug script to test the leaves endpoints and identify 422 errors
"""
import asyncio
import sys
import os
from datetime import date, timedelta

# Add the parent directory to Python path to access app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

async def test_leaves_endpoints():
    """Test the leaves endpoints that are failing with 422 errors"""
    print("🔍 Testing Leaves Endpoints for 422 Errors...")
    
    try:
        # Import required modules
        from app.core.database import get_db
        from app.crud.crud_leave import leave_request_crud
        from app.api.deps import get_current_active_user
        from app.core.security import verify_token
        from app.crud.crud_user import CRUDUser
        from sqlalchemy.ext.asyncio import AsyncSession
        
        print("✅ All imports successful")
        
        # Test database connection
        async for db in get_db():
            print("✅ Database connection successful")
            
            # Test get_pending_requests method
            try:
                pending_requests = await leave_request_crud.get_pending_requests(db)
                print(f"✅ get_pending_requests works: Found {len(pending_requests)} pending requests")
            except Exception as e:
                print(f"❌ get_pending_requests failed: {e}")
                import traceback
                traceback.print_exc()
            
            # Test get_leave_statistics method
            try:
                stats = await leave_request_crud.get_leave_statistics(db, year=None)
                print(f"✅ get_leave_statistics works: {stats}")
            except Exception as e:
                print(f"❌ get_leave_statistics failed: {e}")
                import traceback
                traceback.print_exc()
            
            # Test authentication dependency
            try:
                user_crud = CRUDUser()
                # Try to get a user (assuming user ID 1 exists)
                user = await user_crud.get_with_metadata(db, id=1)
                if user:
                    print(f"✅ User authentication test: Found user {user.email}")
                else:
                    print("⚠️ No users found in database - this could cause auth issues")
            except Exception as e:
                print(f"❌ User authentication test failed: {e}")
                import traceback
                traceback.print_exc()
            
            break
        
        print("\n🔍 Checking for common 422 error causes:")
        
        # Check if required tables exist
        try:
            async for db in get_db():
                # Test if leave_requests table exists and has data
                from sqlalchemy import text
                result = await db.execute(text("SELECT COUNT(*) FROM leave_requests"))
                count = result.scalar()
                print(f"✅ leave_requests table exists with {count} records")
                
                # Test if users table exists and has data
                result = await db.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                print(f"✅ users table exists with {count} records")
                
                # Test if leave_types table exists
                result = await db.execute(text("SELECT COUNT(*) FROM leave_types"))
                count = result.scalar()
                print(f"✅ leave_types table exists with {count} records")
                
                # Test if leave_statuses table exists
                result = await db.execute(text("SELECT COUNT(*) FROM leave_statuses"))
                count = result.scalar()
                print(f"✅ leave_statuses table exists with {count} records")
                
                break
        except Exception as e:
            print(f"❌ Database table check failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n✅ Debug test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_leaves_endpoints())
