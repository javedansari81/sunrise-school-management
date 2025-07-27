#!/usr/bin/env python3
"""
Direct server runner for Sunrise School Management System
"""

import os
import sys
import uvicorn

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set environment variables
os.environ.setdefault('PYTHONPATH', current_dir)

if __name__ == "__main__":
    print("=" * 60)
    print("🏫 SUNRISE SCHOOL MANAGEMENT SYSTEM")
    print("=" * 60)
    print("🚀 Starting backend server...")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Alternative Docs: http://localhost:8000/redoc")
    print("\n💡 Default Admin Login:")
    print("   Email: admin@sunriseschool.edu")
    print("   Password: admin123")
    print("\n" + "=" * 60)
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to avoid import issues
        log_level="info"
    )
