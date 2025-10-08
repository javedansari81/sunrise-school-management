"""
Database Deployment Endpoint
Provides API endpoints for complete database redeployment
"""
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import asyncpg
import os
from pathlib import Path
import logging

from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class DeploymentStep(BaseModel):
    """Model for deployment step status"""
    step: str
    status: str
    message: str
    error: str = None


class DeploymentResponse(BaseModel):
    """Model for deployment response"""
    success: bool
    message: str
    steps: List[DeploymentStep]
    total_steps: int
    completed_steps: int
    failed_steps: int


async def execute_sql_file(conn: asyncpg.Connection, file_path: Path, step_name: str, database_name: str = None) -> DeploymentStep:
    """
    Execute a SQL file and return the deployment step result
    
    Args:
        conn: Database connection
        file_path: Path to SQL file
        step_name: Name of the deployment step
        
    Returns:
        DeploymentStep with execution status
    """
    try:
        logger.info(f"Executing {step_name}: {file_path}")
        
        if not file_path.exists():
            return DeploymentStep(
                step=step_name,
                status="failed",
                message=f"File not found: {file_path}",
                error=f"File does not exist: {file_path}"
            )
        
        # Read SQL file
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Remove psql-specific commands that won't work with asyncpg
        # Remove \echo, \ir, and other psql meta-commands
        sql_lines = []
        for line in sql_content.split('\n'):
            stripped = line.strip()
            # Skip psql meta-commands
            if stripped.startswith('\\'):
                continue
            sql_lines.append(line)

        sql_content = '\n'.join(sql_lines)

        # Remove explicit BEGIN/COMMIT as asyncpg handles transactions
        # But keep the SQL statements between them
        sql_content = sql_content.replace('BEGIN;', '')
        sql_content = sql_content.replace('COMMIT;', '')

        # Replace hardcoded database name with actual database name if provided
        if database_name:
            sql_content = sql_content.replace('sunrise_school_db', database_name)

        # Execute SQL - asyncpg can handle multiple statements
        await conn.execute(sql_content)
        
        return DeploymentStep(
            step=step_name,
            status="success",
            message=f"Successfully executed {file_path.name}"
        )
        
    except Exception as e:
        logger.error(f"Error executing {step_name}: {str(e)}")
        return DeploymentStep(
            step=step_name,
            status="failed",
            message=f"Failed to execute {file_path.name}",
            error=str(e)
        )


@router.post("/deploy", response_model=DeploymentResponse)
async def deploy_database():
    """
    Complete database redeployment endpoint
    
    This endpoint will:
    1. Drop and recreate the sunrise schema (WARNING: This deletes all data!)
    2. Create all database objects in the correct order:
       - Schema initialization
       - Metadata tables
       - Core tables
       - Fee management tables
       - Expense management tables
       - Leave management tables
       - Functions
       - Views
       - Load metadata
       - Create admin user
    
    ⚠️ WARNING: This will DELETE ALL existing data in the sunrise schema!
    Only use this endpoint when you want to completely rebuild the database.
    
    Returns:
        DeploymentResponse with detailed status of each deployment step
    """
    steps: List[DeploymentStep] = []
    conn = None
    
    try:
        # Get database URL from settings
        database_url = settings.DATABASE_URL
        
        if not database_url or database_url.startswith("sqlite"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This endpoint only works with PostgreSQL databases"
            )
        
        # Extract database name from URL
        # Format: postgresql://user:pass@host:port/database_name
        database_name = database_url.split('/')[-1].split('?')[0]
        logger.info(f"Database name: {database_name}")

        # Connect to database
        logger.info("Connecting to database...")
        conn = await asyncpg.connect(database_url)

        # Get the workspace root
        # Current file: sunrise-backend-fastapi/app/api/v1/endpoints/database.py
        # Need to go up 5 levels to reach workspace root
        # database.py -> endpoints -> v1 -> api -> app -> sunrise-backend-fastapi -> workspace_root
        current_file = Path(__file__).resolve()
        workspace_root = current_file.parent.parent.parent.parent.parent.parent
        database_folder = workspace_root / "Database"

        logger.info(f"Current file: {current_file}")
        logger.info(f"Workspace root: {workspace_root}")
        logger.info(f"Looking for Database folder at: {database_folder}")

        if not database_folder.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database folder not found at {database_folder}"
            )

        logger.info(f"Using database scripts from: {database_folder}")
        
        # =====================================================
        # STEP 0: Drop and recreate sunrise schema
        # =====================================================
        try:
            logger.info("Dropping existing sunrise schema...")
            await conn.execute("DROP SCHEMA IF EXISTS sunrise CASCADE;")
            steps.append(DeploymentStep(
                step="Drop Schema",
                status="success",
                message="Successfully dropped existing sunrise schema"
            ))
        except Exception as e:
            steps.append(DeploymentStep(
                step="Drop Schema",
                status="failed",
                message="Failed to drop existing schema",
                error=str(e)
            ))
            raise
        
        # =====================================================
        # STEP 1: Schema Initialization
        # =====================================================
        step = await execute_sql_file(
            conn,
            database_folder / "Schema" / "00_create_schema.sql",
            "Schema Initialization",
            database_name
        )
        steps.append(step)
        if step.status == "failed":
            raise Exception(f"Schema initialization failed: {step.error}")
        
        # =====================================================
        # STEP 2: Create Metadata Tables
        # =====================================================
        metadata_tables = [
            "T100_user_types.sql",
            "T110_session_years.sql",
            "T120_genders.sql",
            "T130_classes.sql",
            "T140_payment_types.sql",
            "T150_payment_statuses.sql",
            "T160_payment_methods.sql",
            "T170_leave_types.sql",
            "T180_leave_statuses.sql",
            "T190_expense_categories.sql",
            "T200_expense_statuses.sql",
            "T210_employment_statuses.sql",
            "T220_qualifications.sql",
        ]
        
        for table_file in metadata_tables:
            step = await execute_sql_file(
                conn,
                database_folder / "Tables" / table_file,
                f"Metadata Table: {table_file}"
            )
            steps.append(step)
            if step.status == "failed":
                raise Exception(f"Failed to create metadata table {table_file}: {step.error}")
        
        # =====================================================
        # STEP 3: Create Core Tables
        # =====================================================
        core_tables = [
            "T300_users.sql",
            "T310_students.sql",
            "T320_teachers.sql",
        ]
        
        for table_file in core_tables:
            step = await execute_sql_file(
                conn,
                database_folder / "Tables" / table_file,
                f"Core Table: {table_file}"
            )
            steps.append(step)
            if step.status == "failed":
                raise Exception(f"Failed to create core table {table_file}: {step.error}")
        
        # =====================================================
        # STEP 4: Create Fee Management Tables
        # =====================================================
        fee_tables = [
            "T400_fee_structures.sql",
            "T410_fee_records.sql",
            "T420_monthly_fee_tracking.sql",
            "T430_monthly_payment_allocations.sql",
        ]
        
        for table_file in fee_tables:
            step = await execute_sql_file(
                conn,
                database_folder / "Tables" / table_file,
                f"Fee Management Table: {table_file}"
            )
            steps.append(step)
            if step.status == "failed":
                raise Exception(f"Failed to create fee table {table_file}: {step.error}")
        
        # =====================================================
        # STEP 5: Create Expense Management Tables
        # =====================================================
        expense_tables = [
            "T500_expenses.sql",
            "T510_vendors.sql",
        ]
        
        for table_file in expense_tables:
            step = await execute_sql_file(
                conn,
                database_folder / "Tables" / table_file,
                f"Expense Management Table: {table_file}"
            )
            steps.append(step)
            if step.status == "failed":
                raise Exception(f"Failed to create expense table {table_file}: {step.error}")
        
        # =====================================================
        # STEP 6: Create Leave Management Tables
        # =====================================================
        step = await execute_sql_file(
            conn,
            database_folder / "Tables" / "T600_leave_requests.sql",
            "Leave Management Table: T600_leave_requests.sql"
        )
        steps.append(step)
        if step.status == "failed":
            raise Exception(f"Failed to create leave table: {step.error}")

        # =====================================================
        # STEP 7: Create Functions
        # =====================================================
        functions = [
            "F100_calculate_age.sql",
            "F110_get_academic_year.sql",
            "F120_calculate_fee_balance.sql",
            "F130_enable_monthly_tracking_complete.sql",
        ]

        for function_file in functions:
            step = await execute_sql_file(
                conn,
                database_folder / "Functions" / function_file,
                f"Function: {function_file}"
            )
            steps.append(step)
            if step.status == "failed":
                raise Exception(f"Failed to create function {function_file}: {step.error}")

        # =====================================================
        # STEP 8: Create Views
        # =====================================================
        views = [
            "V100_student_summary.sql",
            "V110_teacher_summary.sql",
            "V120_fee_collection_summary.sql",
            "V130_enhanced_student_fee_status.sql",
        ]

        for view_file in views:
            step = await execute_sql_file(
                conn,
                database_folder / "Views" / view_file,
                f"View: {view_file}"
            )
            steps.append(step)
            if step.status == "failed":
                raise Exception(f"Failed to create view {view_file}: {step.error}")

        # =====================================================
        # STEP 9: Load Metadata
        # =====================================================
        step = await execute_sql_file(
            conn,
            database_folder / "Init" / "01_load_metadata.sql",
            "Load Metadata"
        )
        steps.append(step)
        if step.status == "failed":
            raise Exception(f"Failed to load metadata: {step.error}")

        # =====================================================
        # STEP 10: Create Admin User
        # =====================================================
        step = await execute_sql_file(
            conn,
            database_folder / "Init" / "02_create_admin_user.sql",
            "Create Admin User"
        )
        steps.append(step)
        if step.status == "failed":
            raise Exception(f"Failed to create admin user: {step.error}")

        # =====================================================
        # Verify Deployment
        # =====================================================
        try:
            # Count tables
            table_count = await conn.fetchval("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'sunrise'
            """)

            # Count users
            user_count = await conn.fetchval("SELECT COUNT(*) FROM sunrise.users")

            # Count metadata records
            metadata_count = await conn.fetchval("""
                SELECT
                    (SELECT COUNT(*) FROM sunrise.user_types) +
                    (SELECT COUNT(*) FROM sunrise.session_years) +
                    (SELECT COUNT(*) FROM sunrise.genders) +
                    (SELECT COUNT(*) FROM sunrise.classes) +
                    (SELECT COUNT(*) FROM sunrise.payment_types) +
                    (SELECT COUNT(*) FROM sunrise.payment_statuses) +
                    (SELECT COUNT(*) FROM sunrise.payment_methods) +
                    (SELECT COUNT(*) FROM sunrise.leave_types) +
                    (SELECT COUNT(*) FROM sunrise.leave_statuses) +
                    (SELECT COUNT(*) FROM sunrise.expense_categories) +
                    (SELECT COUNT(*) FROM sunrise.expense_statuses) +
                    (SELECT COUNT(*) FROM sunrise.employment_statuses) +
                    (SELECT COUNT(*) FROM sunrise.qualifications)
            """)

            steps.append(DeploymentStep(
                step="Verification",
                status="success",
                message=f"Deployment verified: {table_count} tables, {user_count} users, {metadata_count} metadata records"
            ))

        except Exception as e:
            steps.append(DeploymentStep(
                step="Verification",
                status="warning",
                message="Deployment completed but verification failed",
                error=str(e)
            ))

        # Close connection
        await conn.close()

        # Calculate statistics
        total_steps = len(steps)
        completed_steps = sum(1 for s in steps if s.status == "success")
        failed_steps = sum(1 for s in steps if s.status == "failed")

        return DeploymentResponse(
            success=True,
            message=f"Database deployment completed successfully! {completed_steps}/{total_steps} steps completed.",
            steps=steps,
            total_steps=total_steps,
            completed_steps=completed_steps,
            failed_steps=failed_steps
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database deployment failed: {str(e)}")
        if conn:
            await conn.close()

        return DeploymentResponse(
            success=False,
            message=f"Database deployment failed: {str(e)}",
            steps=steps,
            total_steps=len(steps),
            completed_steps=sum(1 for s in steps if s.status == "success"),
            failed_steps=sum(1 for s in steps if s.status == "failed")
        )


@router.get("/status")
async def get_database_status():
    """
    Get current database status and statistics

    Returns information about:
    - Database connection status
    - Schema existence
    - Table counts
    - Record counts
    - Last deployment version
    """
    try:
        database_url = settings.DATABASE_URL

        if not database_url or database_url.startswith("sqlite"):
            return {
                "status": "not_applicable",
                "message": "Database status endpoint only works with PostgreSQL"
            }

        conn = await asyncpg.connect(database_url)

        # Check if sunrise schema exists
        schema_exists = await conn.fetchval("""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.schemata
                WHERE schema_name = 'sunrise'
            )
        """)

        if not schema_exists:
            await conn.close()
            return {
                "status": "not_deployed",
                "message": "Sunrise schema does not exist. Database needs to be deployed.",
                "schema_exists": False
            }

        # Get table count
        table_count = await conn.fetchval("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'sunrise'
        """)

        # Get record counts
        try:
            user_count = await conn.fetchval("SELECT COUNT(*) FROM sunrise.users")
            student_count = await conn.fetchval("SELECT COUNT(*) FROM sunrise.students")
            teacher_count = await conn.fetchval("SELECT COUNT(*) FROM sunrise.teachers")
            fee_count = await conn.fetchval("SELECT COUNT(*) FROM sunrise.fee_records")
            expense_count = await conn.fetchval("SELECT COUNT(*) FROM sunrise.expenses")
            leave_count = await conn.fetchval("SELECT COUNT(*) FROM sunrise.leave_requests")
        except:
            user_count = student_count = teacher_count = 0
            fee_count = expense_count = leave_count = 0

        # Get last deployment version
        try:
            last_version = await conn.fetchrow("""
                SELECT version, description, applied_at, applied_by
                FROM sunrise.schema_versions
                ORDER BY applied_at DESC
                LIMIT 1
            """)
        except:
            last_version = None

        await conn.close()

        return {
            "status": "deployed",
            "message": "Database is deployed and operational",
            "schema_exists": True,
            "statistics": {
                "tables": table_count,
                "users": user_count,
                "students": student_count,
                "teachers": teacher_count,
                "fee_records": fee_count,
                "expenses": expense_count,
                "leave_requests": leave_count
            },
            "last_deployment": {
                "version": last_version["version"] if last_version else None,
                "description": last_version["description"] if last_version else None,
                "applied_at": last_version["applied_at"].isoformat() if last_version else None,
                "applied_by": last_version["applied_by"] if last_version else None
            } if last_version else None
        }

    except Exception as e:
        logger.error(f"Error getting database status: {str(e)}")
        return {
            "status": "error",
            "message": f"Error getting database status: {str(e)}"
        }


@router.post("/deploy-function")
async def deploy_monthly_tracking_function():
    """
    Deploy only the enable_monthly_tracking_complete function

    This endpoint will:
    1. Create/update the enable_monthly_tracking_complete function
    2. NOT drop any existing data

    Use this to add the missing function to an existing database.

    Returns:
        Status of the function deployment
    """
    conn = None

    try:
        # Get database URL from settings
        database_url = settings.DATABASE_URL

        if not database_url or database_url.startswith("sqlite"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This endpoint only works with PostgreSQL databases. SQLite does not support PL/pgSQL functions."
            )

        # Connect to database
        logger.info("Connecting to database...")
        conn = await asyncpg.connect(database_url)

        # Get the workspace root
        current_file = Path(__file__).resolve()
        workspace_root = current_file.parent.parent.parent.parent.parent.parent
        database_folder = workspace_root / "Database"

        if not database_folder.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database folder not found at {database_folder}"
            )

        function_file = database_folder / "Functions" / "F130_enable_monthly_tracking_complete.sql"

        if not function_file.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Function file not found at {function_file}"
            )

        # Read and execute the function file
        logger.info(f"Deploying function from: {function_file}")

        with open(function_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Execute the SQL
        await conn.execute(sql_content)

        # Verify the function was created
        function_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1
                FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE p.proname = 'enable_monthly_tracking_complete'
                AND n.nspname = 'public'
            )
        """)

        await conn.close()

        if function_exists:
            return {
                "success": True,
                "message": "Function enable_monthly_tracking_complete deployed successfully",
                "function_name": "enable_monthly_tracking_complete",
                "status": "deployed"
            }
        else:
            return {
                "success": False,
                "message": "Function deployment completed but verification failed",
                "function_name": "enable_monthly_tracking_complete",
                "status": "unknown"
            }

    except Exception as e:
        logger.error(f"Error deploying function: {str(e)}")
        if conn:
            await conn.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deploy function: {str(e)}"
        )
