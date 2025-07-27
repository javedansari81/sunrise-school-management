#!/usr/bin/env python3
"""
Fresh server start for Sunrise School Management System
"""

import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Create FastAPI app
app = FastAPI(
    title="🏫 Sunrise School Management System",
    version="1.0.0",
    description="Comprehensive School Management System with Role-based Access Control",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic routes
@app.get("/")
async def root():
    return {
        "message": "🏫 Welcome to Sunrise School Management System!",
        "status": "running",
        "version": "1.0.0",
        "docs": "Visit /docs for API documentation",
        "features": [
            "Fee Management System",
            "Student Profile Management", 
            "Teacher Profile Management",
            "Leave Management System",
            "Expense Management System",
            "Role-based Authentication"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Sunrise School Management System"}

# Import API routers
print("🔄 Loading API routers...")

try:
    # Import all required modules first
    import psycopg2
    import asyncpg
    print("✅ Database drivers loaded")
    
    # Import API router
    from app.api.v1.api import api_router
    app.include_router(api_router, prefix="/api/v1")
    
    print("✅ All API routers loaded successfully!")
    print("🔗 Available endpoints:")
    print("   - Authentication: /api/v1/auth/")
    print("   - Fee Management: /api/v1/fees/")
    print("   - Student Management: /api/v1/students/")
    print("   - Teacher Management: /api/v1/teachers/")
    print("   - Leave Management: /api/v1/leaves/")
    print("   - Expense Management: /api/v1/expenses/")
    
    API_LOADED = True
    
except Exception as e:
    print(f"❌ Error loading API routers: {e}")
    print("🔧 Running with basic endpoints only")
    
    # Add basic test endpoint
    @app.get("/api/v1/test")
    async def test_api():
        return {
            "message": "Basic API is working!",
            "endpoint": "/api/v1/test",
            "note": "Full API routers not loaded",
            "error": str(e)
        }
    
    API_LOADED = False

if __name__ == "__main__":
    print("=" * 60)
    print("🏫 SUNRISE SCHOOL MANAGEMENT SYSTEM")
    print("=" * 60)
    print("🚀 Starting backend server...")
    
    if API_LOADED:
        print("✅ Full API loaded with all features")
    else:
        print("⚠️  Running with limited functionality")
    
    print("\n🌐 Server starting on http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Alternative Docs: http://localhost:8000/redoc")
    print("\n💡 Default Admin Login:")
    print("   Email: admin@sunriseschool.edu")
    print("   Password: admin123")
    print("\n" + "=" * 60)
    
    # Start server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
