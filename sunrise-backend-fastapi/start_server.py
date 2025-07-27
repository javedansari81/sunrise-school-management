#!/usr/bin/env python3
"""
Start the Sunrise School Management System Backend Server
"""

import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

def create_app():
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Sunrise School Management System",
        version="1.0.0",
        description="Comprehensive School Management System API with role-based access control",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Basic health check
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

    # Import and include API routers
    try:
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
        
    except ImportError as e:
        print(f"❌ Warning: Could not import API routers: {e}")
        print("🔧 Running with basic endpoints only")
        
        # Add a simple test endpoint
        @app.get("/api/v1/test")
        async def test_api():
            return {
                "message": "API v1 is working!",
                "endpoint": "/api/v1/test",
                "note": "Full API routers not loaded due to import error"
            }

    return app

def main():
    """Main function to start the server"""
    print("=" * 60)
    print("🏫 SUNRISE SCHOOL MANAGEMENT SYSTEM")
    print("=" * 60)
    print("🚀 Starting backend server...")
    
    # Create the app
    app = create_app()
    
    # Start the server
    print("\n🌐 Server starting on http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Alternative Docs: http://localhost:8000/redoc")
    print("\n💡 Default Admin Login:")
    print("   Email: admin@sunriseschool.edu")
    print("   Password: admin123")
    print("\n" + "=" * 60)
    
    uvicorn.run(
        "start_server:create_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info",
        factory=True
    )

if __name__ == "__main__":
    main()
