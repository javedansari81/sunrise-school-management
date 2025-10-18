from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os

from app.core.logging import setup_logging
from app.core.config import settings

# Initialize logging
setup_logging("INFO")
logger = logging.getLogger("sunrise_app")

# Create FastAPI app
app = FastAPI(
    title="Sunrise Backend FastAPI",
    version="1.0.0",
    description="Sunrise School Management System API",
    redirect_slashes=False  # Disable automatic trailing slash redirects
)

# Configure CORS based on environment
environment = os.getenv("ENVIRONMENT", "development")
cors_origins = settings.BACKEND_CORS_ORIGINS

logger.info(f"Environment: {environment}")
logger.info(f"CORS Origins: {cors_origins}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if environment == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
import sys
import os
import asyncpg

# Ensure proper path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    # Force import with explicit path
    from app.api.v1.api import api_router
    app.include_router(api_router, prefix="/api/v1")
    print("✅ All API routers loaded successfully with PostgreSQL database!")
    print("🔗 Available endpoints:")
    print("   - Authentication: /api/v1/auth/")
    print("   - Fee Management: /api/v1/fees/")
    print("   - Student Management: /api/v1/students/")
    print("   - Teacher Management: /api/v1/teachers/")
    print("   - Leave Management: /api/v1/leaves/")
    print("   - Expense Management: /api/v1/expenses/")
    print("   - Transport Management: /api/v1/transport/")

except ImportError as e:
    print(f"❌ Warning: Could not import routers: {e}")
    print("🔧 Running with basic endpoints only")

    # Add basic test endpoints
    @app.get("/api/v1/test")
    async def test_api():
        return {
            "message": "API v1 is working!",
            "endpoint": "/api/v1/test",
            "note": "Full API routers not loaded due to import error",
            "error": str(e)
        }

# Basic routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to Sunrise Backend FastAPI!",
        "status": "running",
        "docs": "Visit /docs for API documentation",
        "environment": environment,
        "cors_origins": cors_origins
    }

@app.get("/health")
async def health_check():
    import asyncpg
    from app.core.config import settings

    # Test database connectivity
    db_status = "unknown"
    try:
        # Use the original DATABASE_URL for asyncpg connection
        conn = await asyncpg.connect(settings.DATABASE_URL)
        schema = await conn.fetchval("SELECT current_schema()")
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        await conn.close()
        db_status = f"connected (schema: {schema}, users: {user_count})"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "service": "Sunrise Backend FastAPI",
        "environment": environment,
        "database": db_status,
        "cors_origins": cors_origins
    }

@app.get("/api/v1/test")
async def test_api():
    return {
        "message": "API v1 is working!",
        "endpoint": "/api/v1/test",
        "timestamp": "2025-01-26"
    }

@app.post("/setup-database")
async def setup_database():
    """One-time database setup endpoint"""
    import asyncpg
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        return {"error": "DATABASE_URL not found"}

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        # Check if already setup
        try:
            count = await conn.fetchval("SELECT COUNT(*) FROM users")
            if count > 0:
                await conn.close()
                return {"message": "Database already setup", "users": count}
        except:
            pass

        # Setup database
        with open('database_schema.sql', 'r') as f:
            await conn.execute(f.read())
        with open('sample_data.sql', 'r') as f:
            await conn.execute(f.read())

        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        await conn.close()

        return {
            "message": "Database setup complete!",
            "users": user_count,
            "login": "admin@sunrise.com / admin123"
        }
    except Exception as e:
        return {"error": str(e)}



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
