"""
Script to apply the soft-delete unique constraint migration
This script applies the V1.5__fix_soft_delete_unique_constraints.sql migration
"""
import asyncio
import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def read_migration_file() -> str:
    """Read the migration SQL file"""
    migration_path = Path(__file__).parent.parent / "Database" / "Versioning" / "V1.5__fix_soft_delete_unique_constraints.sql"
    
    if not migration_path.exists():
        raise FileNotFoundError(f"Migration file not found: {migration_path}")
    
    with open(migration_path, 'r', encoding='utf-8') as f:
        return f.read()


async def apply_migration(db: AsyncSession, sql_content: str):
    """Apply the migration SQL"""
    
    # Split the SQL content into individual statements
    statements = []
    current_statement = []
    
    for line in sql_content.split('\n'):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('--'):
            continue
            
        current_statement.append(line)
        
        # If line ends with semicolon, it's the end of a statement
        if line.endswith(';'):
            statement = ' '.join(current_statement)
            if statement.strip():
                statements.append(statement)
            current_statement = []
    
    # Execute each statement
    for i, statement in enumerate(statements, 1):
        try:
            logger.info(f"Executing statement {i}/{len(statements)}: {statement[:100]}...")
            await db.execute(text(statement))
            await db.commit()
            logger.info(f"✓ Statement {i} executed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error executing statement {i}: {e}")
            logger.error(f"Statement: {statement}")
            await db.rollback()
            
            # Continue with other statements for non-critical errors
            if "already exists" in str(e).lower() or "does not exist" in str(e).lower():
                logger.warning(f"⚠️  Continuing with next statement (constraint may already be applied)")
                continue
            else:
                raise


async def verify_migration(db: AsyncSession):
    """Verify that the migration was applied correctly"""
    
    logger.info("Verifying migration...")
    
    try:
        # Check if the new partial unique indexes exist
        check_indexes_query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            indexdef
        FROM pg_indexes 
        WHERE tablename IN ('teachers', 'students') 
          AND indexname LIKE '%_active'
        ORDER BY tablename, indexname;
        """
        
        result = await db.execute(text(check_indexes_query))
        indexes = result.fetchall()
        
        expected_indexes = [
            'uk_teachers_employee_id_active',
            'uk_teachers_email_active',
            'uk_students_admission_number_active',
            'uk_students_email_active'
        ]
        
        found_indexes = [row[2] for row in indexes]  # indexname is the 3rd column
        
        logger.info(f"Found indexes: {found_indexes}")
        
        for expected_index in expected_indexes:
            if expected_index in found_indexes:
                logger.info(f"✓ Index {expected_index} exists")
            else:
                logger.warning(f"⚠️  Index {expected_index} not found")
        
        if len(found_indexes) >= 4:
            logger.info("✅ Migration verification PASSED - partial unique indexes are in place")
        else:
            logger.warning("⚠️  Migration verification INCOMPLETE - some indexes may be missing")
            
    except Exception as e:
        logger.error(f"❌ Error verifying migration: {e}")
        logger.info("Migration may have been applied but verification failed")


async def test_soft_delete_functionality(db: AsyncSession):
    """Test that soft-delete functionality works after migration"""
    
    logger.info("Testing soft-delete functionality...")
    
    try:
        # Test creating a teacher, soft-deleting, and creating another with same employee_id
        test_queries = [
            # Create a test teacher
            """
            INSERT INTO teachers (employee_id, first_name, last_name, email, phone, position, joining_date) 
            VALUES ('MIGRATION_TEST_001', 'Test', 'Teacher', 'test.migration@example.com', '1234567890', 'Test Teacher', CURRENT_DATE)
            """,
            
            # Soft delete the teacher
            """
            UPDATE teachers 
            SET is_deleted = TRUE, deleted_date = NOW() 
            WHERE employee_id = 'MIGRATION_TEST_001'
            """,
            
            # Create another teacher with the same employee_id (should work now)
            """
            INSERT INTO teachers (employee_id, first_name, last_name, email, phone, position, joining_date) 
            VALUES ('MIGRATION_TEST_001', 'New', 'Teacher', 'new.migration@example.com', '0987654321', 'New Test Teacher', CURRENT_DATE)
            """,
            
            # Clean up test data
            """
            DELETE FROM teachers WHERE employee_id = 'MIGRATION_TEST_001'
            """
        ]
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"Executing test query {i}/{len(test_queries)}...")
            await db.execute(text(query))
            await db.commit()
            
        logger.info("✅ Soft-delete functionality test PASSED")
        
    except Exception as e:
        logger.error(f"❌ Soft-delete functionality test FAILED: {e}")
        await db.rollback()
        raise


async def main():
    """Main function to apply the migration"""
    
    logger.info("🚀 Starting Soft-Delete Migration Application")
    logger.info("=" * 60)
    
    try:
        # Read migration file
        logger.info("Reading migration file...")
        sql_content = await read_migration_file()
        logger.info(f"✓ Migration file loaded ({len(sql_content)} characters)")
        
        # Get database session
        async for db in get_db():
            try:
                # Apply migration
                logger.info("Applying migration...")
                await apply_migration(db, sql_content)
                logger.info("✅ Migration applied successfully")
                
                # Verify migration
                await verify_migration(db)
                
                # Test functionality
                await test_soft_delete_functionality(db)
                
                logger.info("\n" + "=" * 60)
                logger.info("✅ MIGRATION COMPLETED SUCCESSFULLY!")
                logger.info("\nNext Steps:")
                logger.info("1. Run the test script: python tests/test_database_constraint_fix.py")
                logger.info("2. Test teacher/student creation in the UI")
                logger.info("3. Verify that soft-delete replacement messages appear correctly")
                
            except Exception as e:
                logger.error(f"❌ Migration failed: {e}")
                raise
            finally:
                await db.close()
                break
                
    except Exception as e:
        logger.error(f"❌ MIGRATION FAILED: {e}")
        logger.error("\n🔧 TROUBLESHOOTING:")
        logger.error("1. Check database connection settings")
        logger.error("2. Ensure you have database admin privileges")
        logger.error("3. Verify the migration file exists and is readable")
        logger.error("4. Check database logs for detailed error information")
        raise


if __name__ == "__main__":
    asyncio.run(main())
