#!/usr/bin/env python3
"""
Minimal working server for Sunrise School Management System
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta
import bcrypt

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Create FastAPI app
app = FastAPI(
    title="🏫 Sunrise School Management System",
    version="1.0.0",
    description="School Management System API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

# Mock user data (in production, this would come from database)
MOCK_ADMIN = {
    "id": 1,
    "email": "admin@sunriseschool.edu",
    "password_hash": "$2b$12$wq4BwIaHKkm5IPdmm9rvz.pyOmvDofmSGt9m5zJrRiv8Q6IuDM5tC",  # admin123
    "first_name": "Admin",
    "last_name": "User",
    "user_type": "admin",
    "is_active": True
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except:
        return False

def create_access_token(data: dict):
    """Create a simple access token (in production, use proper JWT)"""
    import base64
    import json
    token_data = {"sub": data["email"], "user_id": data["id"]}
    token = base64.b64encode(json.dumps(token_data).encode()).decode()
    return token

# Routes
@app.get("/")
async def root():
    return {
        "message": "🏫 Welcome to Sunrise School Management System!",
        "status": "running",
        "version": "1.0.0",
        "docs": "Visit /docs for API documentation"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Sunrise School Management System"}

@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 login endpoint"""
    # Check credentials
    if form_data.username == MOCK_ADMIN["email"]:
        if verify_password(form_data.password, MOCK_ADMIN["password_hash"]):
            access_token = create_access_token({"email": MOCK_ADMIN["email"], "id": MOCK_ADMIN["id"]})
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
                user={
                    "id": MOCK_ADMIN["id"],
                    "email": MOCK_ADMIN["email"],
                    "first_name": MOCK_ADMIN["first_name"],
                    "last_name": MOCK_ADMIN["last_name"],
                    "user_type": MOCK_ADMIN["user_type"]
                }
            )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password"
    )

@app.post("/api/v1/auth/login-json", response_model=LoginResponse)
async def login_json(login_data: LoginRequest):
    """JSON login endpoint"""
    # Check credentials
    if login_data.email == MOCK_ADMIN["email"]:
        if verify_password(login_data.password, MOCK_ADMIN["password_hash"]):
            access_token = create_access_token({"email": MOCK_ADMIN["email"], "id": MOCK_ADMIN["id"]})
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
                user={
                    "id": MOCK_ADMIN["id"],
                    "email": MOCK_ADMIN["email"],
                    "first_name": MOCK_ADMIN["first_name"],
                    "last_name": MOCK_ADMIN["last_name"],
                    "user_type": MOCK_ADMIN["user_type"]
                }
            )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password"
    )

@app.get("/api/v1/auth/me")
async def get_current_user():
    """Get current user info"""
    return {
        "id": MOCK_ADMIN["id"],
        "email": MOCK_ADMIN["email"],
        "first_name": MOCK_ADMIN["first_name"],
        "last_name": MOCK_ADMIN["last_name"],
        "user_type": MOCK_ADMIN["user_type"]
    }

# Basic endpoints for testing
@app.get("/api/v1/students/")
async def get_students():
    return {"students": [], "message": "Students endpoint working"}

@app.get("/api/v1/teachers/")
async def get_teachers():
    return {"teachers": [], "message": "Teachers endpoint working"}

@app.get("/api/v1/fees/")
async def get_fees():
    return {"fees": [], "message": "Fees endpoint working"}

@app.get("/api/v1/leaves/")
async def get_leaves():
    return {"leaves": [], "message": "Leaves endpoint working"}

@app.get("/api/v1/expenses/")
async def get_expenses():
    return {"expenses": [], "message": "Expenses endpoint working"}

if __name__ == "__main__":
    print("=" * 60)
    print("🏫 SUNRISE SCHOOL MANAGEMENT SYSTEM - MINIMAL VERSION")
    print("=" * 60)
    print("🚀 Starting minimal backend server...")
    print("\n🌐 Server starting on http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("\n💡 Admin Login:")
    print("   Email: admin@sunriseschool.edu")
    print("   Password: admin123")
    print("\n🔗 Available endpoints:")
    print("   - POST /api/v1/auth/login")
    print("   - POST /api/v1/auth/login-json")
    print("   - GET /api/v1/auth/me")
    print("   - GET /api/v1/students/")
    print("   - GET /api/v1/teachers/")
    print("   - GET /api/v1/fees/")
    print("   - GET /api/v1/leaves/")
    print("   - GET /api/v1/expenses/")
    print("\n" + "=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
