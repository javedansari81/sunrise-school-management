"""
Database Endpoints
Database status and function deployment.

Full database redeployment is no longer exposed over HTTP (it dropped the whole
schema without authentication). Use redeploy_database.py at the repository root
to redeploy a local database.
"""
from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
import os
from pathlib import Path
import logging

from app.api.deps import get_current_platform_admin
from app.core.config import settings
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status")
async def get_database_status(admin: User = Depends(get_current_platform_admin)):
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

        conn = await asyncpg.connect(
            settings.ASYNCPG_DSN, ssl=settings.DB_SSL, server_settings={"search_path": settings.DB_SCHEMA}
        )

        # Check if the application schema exists
        schema_exists = await conn.fetchval("""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.schemata
                WHERE schema_name = $1
            )
        """, settings.DB_SCHEMA)

        if not schema_exists:
            await conn.close()
            return {
                "status": "not_deployed",
                "message": f"Schema {settings.DB_SCHEMA} does not exist. Database needs to be deployed.",
                "schema_exists": False
            }

        # Get table count
        table_count = await conn.fetchval("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = $1
        """, settings.DB_SCHEMA)

        # Get record counts
        try:
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            student_count = await conn.fetchval("SELECT COUNT(*) FROM students")
            teacher_count = await conn.fetchval("SELECT COUNT(*) FROM teachers")
            fee_count = await conn.fetchval("SELECT COUNT(*) FROM fee_records")
            expense_count = await conn.fetchval("SELECT COUNT(*) FROM expenses")
            leave_count = await conn.fetchval("SELECT COUNT(*) FROM leave_requests")
        except:
            user_count = student_count = teacher_count = 0
            fee_count = expense_count = leave_count = 0

        # Get last deployment version
        try:
            last_version = await conn.fetchrow("""
                SELECT version, description, applied_at, applied_by
                FROM schema_migrations
                ORDER BY id DESC
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
async def deploy_monthly_tracking_function(admin: User = Depends(get_current_platform_admin)):
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
        conn = await asyncpg.connect(
            settings.ASYNCPG_DSN, ssl=settings.DB_SSL, server_settings={"search_path": settings.DB_SCHEMA}
        )

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
                AND n.nspname = $1
            )
        """, settings.DB_SCHEMA)

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
