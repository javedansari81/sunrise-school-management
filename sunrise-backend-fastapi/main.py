from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Sunrise Backend FastAPI",
    version="1.0.0",
    description="Sunrise School Management System API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
import sys
import os

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
        "docs": "Visit /docs for API documentation"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Sunrise Backend FastAPI"}

@app.get("/api/v1/test")
async def test_api():
    return {
        "message": "API v1 is working!",
        "endpoint": "/api/v1/test",
        "timestamp": "2025-01-26"
    }



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
