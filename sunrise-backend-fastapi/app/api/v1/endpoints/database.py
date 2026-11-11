"""
Database Endpoints
Database status (platform admin only).

Full database redeployment is no longer exposed over HTTP (it dropped the whole
schema without authentication). Use redeploy_database.py at the repository root
to redeploy a local database.
"""
from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
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
            payment_count = await conn.fetchval("SELECT COUNT(*) FROM payments")
            expense_count = await conn.fetchval("SELECT COUNT(*) FROM expenses")
            leave_count = await conn.fetchval("SELECT COUNT(*) FROM leave_requests")
        except:
            user_count = student_count = teacher_count = 0
            payment_count = expense_count = leave_count = 0

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
                "payments": payment_count,
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
