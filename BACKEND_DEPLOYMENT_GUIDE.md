# ⚙️ Backend Deployment Guide - Sunrise School Management System

## 📋 **Complete FastAPI Backend Service Deployment**

This guide provides comprehensive instructions for deploying the FastAPI backend service for the Sunrise National Public School Management System to Render.com cloud platform.

---

## 🎯 **Prerequisites**

### **Required Tools**
- **Python 3.11+** - Latest Python version
- **Git** - For repository access
- **Render.com Account** - Free tier available
- **PostgreSQL Database** - Must be deployed first (see `DATABASE_DEPLOYMENT_GUIDE.md`)

### **Required Knowledge**
- Python and FastAPI fundamentals
- RESTful API concepts
- Environment variable configuration
- Cloud deployment basics

---

## 🏗️ **Backend Architecture Overview**

### **FastAPI Application Structure**
```
sunrise-backend-fastapi/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/          # API route handlers
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── configuration.py # Service-specific config endpoints
│   │   │   ├── students.py     # Student management
│   │   │   ├── teachers.py     # Teacher management
│   │   │   ├── fees.py         # Enhanced fee management
│   │   │   ├── leaves.py       # Leave management
│   │   │   ├── expenses.py     # Expense management
│   │   │   └── public.py       # Public endpoints (no auth)
│   │   └── api.py              # Router configuration
│   ├── core/
│   │   ├── config.py           # Application configuration
│   │   ├── database.py         # Database connection
│   │   ├── security.py         # JWT and password handling
│   │   └── permissions.py      # Role-based access control
│   ├── crud/                   # Database operations
│   ├── models/                 # SQLAlchemy models
│   └── schemas/                # Pydantic schemas
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
└── Dockerfile                  # Container configuration
```

### **Key Features**
- **Async/Await Support** - High-performance asynchronous operations
- **JWT Authentication** - Secure token-based auth with 8-day expiration
- **Role-Based Access Control** - Admin, Teacher, Student, Staff, Parent roles
- **Service-Specific Configuration** - Optimized metadata endpoints (60-80% smaller payloads)
- **Metadata-Driven Architecture** - Foreign key relationships with reference tables
- **Enhanced Monthly Fee System** - Advanced payment tracking and allocation
- **Comprehensive API Documentation** - Auto-generated Swagger UI

---

## 🌐 **Cloud Deployment on Render.com**

### **Step 1: Prepare Repository**

1. **Ensure Database is Deployed**
   - Complete `DATABASE_DEPLOYMENT_GUIDE.md` first
   - Note your PostgreSQL connection string

2. **Verify Backend Code Structure**
   ```bash
   cd sunrise-backend-fastapi
   ls -la
   # Should see: main.py, requirements.txt, app/, Dockerfile
   ```

### **Step 2: Create Web Service on Render.com**

1. **Login to Render.com**
   ```
   https://render.com/
   ```

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - **Connect Repository**: Link your GitHub repository
   - **Name**: `sunrise-backend`
   - **Region**: **Singapore** (nearest to India)
   - **Branch**: `main` (or your deployment branch)
   - **Root Directory**: `sunrise-backend-fastapi`

3. **Build Configuration**
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`

### **Step 3: Environment Variables Configuration**

**Required Environment Variables:**
```bash
# Database Configuration
DATABASE_URL=postgresql://sunrise_user:password@dpg-xxx.singapore-postgres.render.com/sunrise_school

# Security Configuration
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# Application Configuration
ENVIRONMENT=production
BACKEND_CORS_ORIGINS=https://your-frontend-url.onrender.com

# Cloudinary Configuration (Required for Gallery Management)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Optional: Logging Configuration
LOG_LEVEL=INFO
```

**How to Set Environment Variables:**
1. In Render dashboard → Your service → Environment
2. Add each variable with key-value pairs
3. **Important**: Mark sensitive variables as "Secret"

### **Step 4: Deploy Service**
1. Click "Create Web Service"
2. Monitor build logs for any errors
3. Wait for deployment to complete (usually 5-10 minutes)
4. Note your service URL: `https://sunrise-backend.onrender.com`

---

## 🏠 **Local Development Setup**

### **Step 1: Environment Setup**

**Clone Repository:**
```bash
git clone <repository-url>
cd sunrise-school-management/sunrise-backend-fastapi
```

**Create Virtual Environment:**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

### **Step 2: Local Configuration**

**Create `.env` file:**
```bash
# Database (use local PostgreSQL)
DATABASE_URL=postgresql://sunrise_user:password@localhost:5432/sunrise_school

# Security (generate secure keys for production)
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# Development settings
ENVIRONMENT=development
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Logging
LOG_LEVEL=DEBUG
```

### **Step 3: Run Development Server**
```bash
# Start the FastAPI server
python main.py

# Or use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Access Points:**
- **API Base**: http://localhost:8000/api/v1
- **Swagger Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

---

## 📡 **API Endpoints Documentation**

### **Authentication Endpoints**
```bash
POST /api/v1/auth/login              # User login (email + password)
POST /api/v1/auth/enhanced-login     # Enhanced login with detailed response
GET  /api/v1/auth/me                 # Get current user profile
POST /api/v1/auth/refresh            # Refresh access token
```

### **Service-Specific Configuration Endpoints**
```bash
# Optimized metadata endpoints (60-80% smaller payloads)
GET /api/v1/configuration/fee-management/        # Fee system metadata
GET /api/v1/configuration/student-management/    # Student system metadata
GET /api/v1/configuration/leave-management/      # Leave system metadata
GET /api/v1/configuration/expense-management/    # Expense system metadata
GET /api/v1/configuration/teacher-management/    # Teacher system metadata
GET /api/v1/configuration/common/                # Common metadata
```

### **Student Management**
```bash
GET    /api/v1/students/             # List students with filters
POST   /api/v1/students/             # Create new student
GET    /api/v1/students/{id}         # Get student details
PUT    /api/v1/students/{id}         # Update student
DELETE /api/v1/students/{id}         # Soft delete student
```

### **Teacher Management**
```bash
GET    /api/v1/teachers/             # List teachers with filters
POST   /api/v1/teachers/             # Create new teacher
GET    /api/v1/teachers/{id}         # Get teacher details
PUT    /api/v1/teachers/{id}         # Update teacher
DELETE /api/v1/teachers/{id}         # Soft delete teacher
```

### **Enhanced Fee Management**
```bash
GET    /api/v1/fees/                 # List fee records with advanced filters
POST   /api/v1/fees/                 # Create fee record
GET    /api/v1/fees/{id}             # Get fee record details
PUT    /api/v1/fees/{id}             # Update fee record
POST   /api/v1/fees/payment          # Process payment
GET    /api/v1/fees/history/{student_id}  # Payment history
POST   /api/v1/fees/enable-monthly-tracking  # Enable monthly tracking
GET    /api/v1/fees/monthly-summary/{student_id}  # Monthly fee summary
```

### **Leave Management**
```bash
GET    /api/v1/leaves/               # List leave requests
POST   /api/v1/leaves/               # Create leave request
GET    /api/v1/leaves/{id}           # Get leave details
PUT    /api/v1/leaves/{id}           # Update leave request
PATCH  /api/v1/leaves/{id}/approve   # Approve leave
PATCH  /api/v1/leaves/{id}/reject    # Reject leave
```

### **Expense Management**
```bash
GET    /api/v1/expenses/             # List expenses with filters
POST   /api/v1/expenses/             # Create expense
GET    /api/v1/expenses/{id}         # Get expense details
PUT    /api/v1/expenses/{id}         # Update expense
PATCH  /api/v1/expenses/{id}/approve # Approve expense
GET    /api/v1/expenses/categories   # Get expense categories
```

### **Public Endpoints (No Authentication)**
```bash
GET /api/v1/public/faculty           # Get active teachers for public display
GET /api/v1/public/gallery           # Get gallery images grouped by category
GET /api/v1/public/gallery/home-page # Get featured images for home page carousel
```

### **Gallery Management (Admin Only)**
```bash
GET    /api/v1/gallery/categories    # List gallery categories
POST   /api/v1/gallery/categories    # Create new category
PUT    /api/v1/gallery/categories/{id} # Update category
DELETE /api/v1/gallery/categories/{id} # Delete category

GET    /api/v1/gallery/images        # List gallery images
POST   /api/v1/gallery/images/upload # Upload image to Cloudinary
GET    /api/v1/gallery/images/{id}   # Get image details
PUT    /api/v1/gallery/images/{id}   # Update image metadata
DELETE /api/v1/gallery/images/{id}   # Delete image (from DB and Cloudinary)
```

---

## 🔐 **Authentication & Security**

### **JWT Token Configuration**
- **Algorithm**: HS256
- **Expiration**: 8 days (11,520 minutes)
- **Auto-refresh**: Supported
- **Secure Storage**: HttpOnly cookies recommended for production

### **Role-Based Access Control**
```python
# User Roles and Permissions
ADMIN:    # Full system access
  - Manage all students, teachers, fees, leaves, expenses
  - View all reports and analytics
  - System configuration access

TEACHER:  # Limited management access
  - View assigned students
  - Manage own leave requests
  - View fee information (read-only)
  - Submit expense requests

STUDENT:  # Self-service access
  - View own profile and fee status
  - Submit leave requests
  - View payment history

STAFF:    # Administrative support
  - Manage students and fees
  - Process payments
  - Generate reports

PARENT:   # Child information access
  - View child's profile and fees
  - Make payments
  - Submit leave requests for child
```

### **Security Features**
- **Password Hashing**: bcrypt with salt
- **CORS Protection**: Configurable origins
- **SQL Injection Prevention**: SQLAlchemy ORM
- **Input Validation**: Pydantic schemas
- **Rate Limiting**: Built-in FastAPI features

---

## 📊 **Database Integration**

### **Connection Configuration**
```python
# Async PostgreSQL connection
ASYNC_DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"

# Connection pooling
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
    pool_size=20,
    max_overflow=0
)
```

### **Metadata-Driven Architecture**
```python
# Service-specific metadata loading
SERVICE_METADATA_MAPPINGS = {
    "fee-management": [
        "payment_types", "payment_statuses", "payment_methods",
        "session_years", "classes"
    ],
    "student-management": [
        "genders", "classes", "session_years", "user_types"
    ],
    "leave-management": [
        "leave_types", "leave_statuses", "session_years"
    ]
}
```

### **Enhanced Fee System Integration**
- **Monthly Fee Tracking**: Automatic month-wise payment allocation
- **Partial Payment Support**: Handle payments like ₹3200 = 3 full months + ₹200 partial
- **Duplicate Prevention**: Prevent payments for already-paid months
- **Session Year Filtering**: Academic year-based fee management

---

## ✅ **Verification Steps**

### **Step 1: Health Check**
```bash
# Test basic connectivity
curl https://your-backend-url.onrender.com/

# Expected response: {"message": "Sunrise Backend FastAPI is running!"}
```

### **Step 2: API Documentation**
```bash
# Access Swagger UI
https://your-backend-url.onrender.com/docs

# Access ReDoc
https://your-backend-url.onrender.com/redoc
```

### **Step 3: Authentication Test**
```bash
# Test login endpoint
curl -X POST "https://your-backend-url.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@sunrise.com&password=admin123"

# Expected: JWT token in response
```

### **Step 4: Configuration Endpoint Test**
```bash
# Test service-specific configuration
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "https://your-backend-url.onrender.com/api/v1/configuration/fee-management/"

# Expected: Metadata for fee management system
```

### **Step 5: Database Connectivity**
```bash
# Check database connection through API
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "https://your-backend-url.onrender.com/api/v1/students/?limit=1"

# Expected: Student data or empty array
```

---

## 🚨 **Troubleshooting**

### **Common Deployment Issues**

#### **Build Failures**
```bash
# Check requirements.txt
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.11+

# Check for missing dependencies
pip check
```

#### **Database Connection Issues**
```bash
# Test database URL format
postgresql://user:password@host:port/database

# Verify SSL requirements
postgresql://user:password@host:port/database?sslmode=require

# Check connection from local environment
psql "your_database_url" -c "SELECT 1;"
```

#### **Environment Variable Issues**
```bash
# Verify all required variables are set
echo $DATABASE_URL
echo $SECRET_KEY
echo $JWT_SECRET_KEY

# Check for typos in variable names
# Ensure no trailing spaces in values
```

#### **CORS Issues**
```bash
# Verify CORS origins include frontend URL
BACKEND_CORS_ORIGINS=https://your-frontend.onrender.com,http://localhost:3000

# Check browser console for CORS errors
# Ensure no trailing slashes in URLs
```

### **Performance Issues**
```bash
# Monitor application logs
# Check database query performance
# Verify connection pool settings
# Monitor memory usage
```

---

## 📈 **Monitoring and Maintenance**

### **Application Monitoring**
```python
# Built-in logging configuration
import logging
logging.basicConfig(level=logging.INFO)

# Monitor key metrics:
# - Response times
# - Database connection pool
# - Memory usage
# - Error rates
```

### **Health Checks**
```bash
# Set up monitoring endpoints
GET /health              # Application health
GET /api/v1/auth/me      # Authentication health
GET /api/v1/students/    # Database connectivity
```

### **Log Monitoring**
```bash
# Key log patterns to monitor:
# - Authentication failures
# - Database connection errors
# - API response times > 2s
# - Memory usage warnings
```

---

## 🎯 **Production Deployment Checklist**

### **Pre-Deployment**
- [ ] Database deployed and accessible
- [ ] Environment variables configured
- [ ] CORS origins set correctly
- [ ] SSL certificates configured
- [ ] Monitoring setup planned
- [ ] Cloudinary account created (for Gallery)

### **Deployment**
- [ ] Repository connected to Render
- [ ] Build and start commands configured
- [ ] Environment variables set (including Cloudinary)
- [ ] Service deployed successfully
- [ ] Health checks passing

### **Post-Deployment**
- [ ] API documentation accessible
- [ ] Authentication working
- [ ] Database connectivity verified
- [ ] All endpoints responding
- [ ] Frontend integration tested

### **Gallery Management System**
- [ ] Gallery database tables created (gallery_categories, gallery_images)
- [ ] Initial 10 categories loaded
- [ ] Cloudinary environment variables configured
- [ ] Gallery endpoints tested (public and admin)
- [ ] Image upload functionality verified
- [ ] Home page carousel endpoint tested
- [ ] Initial images uploaded (5-10 per category)
- [ ] Home page carousel configured (3-5 featured images)

---

## 🔗 **Next Steps**

After successful backend deployment:

1. **Frontend Deployment**: Follow `FRONTEND_DEPLOYMENT_GUIDE.md`
2. **Integration Testing**: Test complete user workflows
3. **Performance Optimization**: Monitor and optimize slow queries
4. **Security Hardening**: Review and enhance security measures

---

## 🔧 **Advanced Configuration**

### **Custom Domain Setup (Optional)**
```bash
# Configure custom domain in Render dashboard
1. Go to your web service settings
2. Add custom domain: api.sunrise.com
3. Configure DNS CNAME record:
   CNAME api.sunrise.com -> your-service.onrender.com
4. SSL certificate will be auto-generated
```

### **Environment-Specific Configurations**
```python
# app/core/config.py - Advanced settings
class Settings:
    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "0"))

    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "11520"))

    # Performance settings
    ENABLE_QUERY_LOGGING: bool = os.getenv("ENABLE_QUERY_LOGGING", "false").lower() == "true"
    API_RATE_LIMIT: str = os.getenv("API_RATE_LIMIT", "100/minute")

    # Feature flags
    ENABLE_MONTHLY_FEE_TRACKING: bool = os.getenv("ENABLE_MONTHLY_FEE_TRACKING", "true").lower() == "true"
    ENABLE_AUDIT_LOGGING: bool = os.getenv("ENABLE_AUDIT_LOGGING", "false").lower() == "true"
```

### **Logging Configuration**
```python
# app/core/logging.py
import logging
import sys
from typing import Dict, Any

def setup_logging(level: str = "INFO") -> None:
    """Configure application logging"""

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)

    # Application-specific loggers
    app_logger = logging.getLogger("sunrise_app")
    app_logger.setLevel(logging.INFO)

    # Database query logger (optional)
    if os.getenv("ENABLE_QUERY_LOGGING", "false").lower() == "true":
        db_logger = logging.getLogger("sqlalchemy.engine")
        db_logger.setLevel(logging.INFO)
```

---

## 📊 **API Performance Optimization**

### **Database Query Optimization**
```python
# app/crud/base.py - Optimized CRUD operations
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select

class CRUDBase:
    async def get_with_relationships(
        self,
        db: AsyncSession,
        id: int,
        load_relationships: List[str] = None
    ):
        """Optimized query with eager loading"""
        query = select(self.model).where(self.model.id == id)

        if load_relationships:
            for rel in load_relationships:
                query = query.options(selectinload(getattr(self.model, rel)))

        result = await db.execute(query)
        return result.scalar_one_or_none()

# Example usage in endpoints
@router.get("/{student_id}", response_model=StudentWithDetails)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db)
):
    student = await student_crud.get_with_relationships(
        db,
        student_id,
        load_relationships=["class", "session_year", "fee_records"]
    )
    return student
```

### **Caching Implementation**
```python
# app/core/cache.py
from functools import wraps
import json
import hashlib
from typing import Any, Dict, Optional

class MemoryCache:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._ttl: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            if time.time() < self._ttl.get(key, 0):
                return self._cache[key]
            else:
                self.delete(key)
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        self._cache[key] = value
        self._ttl[key] = time.time() + ttl

    def delete(self, key: str):
        self._cache.pop(key, None)
        self._ttl.pop(key, None)

# Cache decorator for expensive operations
def cache_result(ttl: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

# Usage in configuration endpoints
@cache_result(ttl=600)  # Cache for 10 minutes
async def get_fee_management_configuration(db: AsyncSession):
    return await _load_service_metadata(db, "fee-management")
```

### **API Rate Limiting**
```python
# app/core/rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Apply to FastAPI app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Usage in endpoints
@router.post("/login")
@limiter.limit("5/minute")  # Limit login attempts
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Login logic here
    pass
```

---

## 🔒 **Security Hardening**

### **Input Validation and Sanitization**
```python
# app/schemas/base.py - Enhanced validation
from pydantic import BaseModel, validator, Field
import re

class BaseSchema(BaseModel):
    @validator('*', pre=True)
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class StudentCreate(BaseSchema):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: Optional[str] = Field(None, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    phone: Optional[str] = Field(None, regex=r'^\+?[1-9]\d{1,14}$')

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Names can only contain letters and spaces')
        return v.title()
```

### **SQL Injection Prevention**
```python
# app/crud/base.py - Safe query construction
from sqlalchemy import text

class CRUDBase:
    async def search_students(
        self,
        db: AsyncSession,
        search_term: str,
        class_id: Optional[int] = None
    ):
        """Safe search with parameterized queries"""
        query = """
        SELECT s.*, c.display_name as class_name
        FROM students s
        JOIN classes c ON s.class_id = c.id
        WHERE (s.first_name ILIKE :search OR s.last_name ILIKE :search)
        """

        params = {"search": f"%{search_term}%"}

        if class_id:
            query += " AND s.class_id = :class_id"
            params["class_id"] = class_id

        result = await db.execute(text(query), params)
        return result.fetchall()
```

### **CORS Security**
```python
# main.py - Secure CORS configuration
from fastapi.middleware.cors import CORSMiddleware

# Production CORS settings
if settings.ENVIRONMENT == "production":
    allowed_origins = [
        "https://your-frontend.onrender.com",
        "https://sunrise.com"  # Custom domain
    ]
else:
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:8080"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)
```

---

## 📈 **Monitoring and Observability**

### **Health Check Endpoints**
```python
# app/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check including database"""
    try:
        # Test database connection
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "database": db_status,
            "api": "healthy"
        }
    }
```

### **Request Logging Middleware**
```python
# app/middleware/logging.py
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api_requests")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(f"Request: {request.method} {request.url}")

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {response.status_code} - "
            f"Duration: {duration:.3f}s - "
            f"Path: {request.url.path}"
        )

        # Add performance headers
        response.headers["X-Process-Time"] = str(duration)

        return response

# Add to FastAPI app
app.add_middleware(RequestLoggingMiddleware)
```

### **Error Tracking**
```python
# app/core/error_handling.py
import logging
import traceback
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("error_tracking")

async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""

    # Log the error with full traceback
    logger.error(
        f"Unhandled exception in {request.method} {request.url}: "
        f"{str(exc)}\n{traceback.format_exc()}"
    )

    # Return generic error response
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_id": str(uuid.uuid4()),  # For tracking
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Add to FastAPI app
app.add_exception_handler(Exception, global_exception_handler)
```

---

## 🚀 **Deployment Automation**

### **GitHub Actions CI/CD (Optional)**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Render

on:
  push:
    branches: [ main ]
    paths: [ 'sunrise-backend-fastapi/**' ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        cd sunrise-backend-fastapi
        pip install -r requirements.txt
        pip install pytest pytest-asyncio

    - name: Run tests
      run: |
        cd sunrise-backend-fastapi
        pytest tests/ -v

    - name: Trigger Render Deploy
      if: success()
      run: |
        curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK }}"
```

### **Docker Configuration**
```dockerfile
# sunrise-backend-fastapi/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📸 **Gallery Management System Deployment**

### **Overview**
The Gallery Management System allows uploading and managing ~200 school photos across different categories (Independence Day, School Premises, Sports Day, etc.) with Cloudinary integration for cloud storage.

---

### **Step 1: Database Migration**

**Tables to Create:**
1. `gallery_categories` - Stores gallery categories (10 initial categories)
2. `gallery_images` - Stores image metadata (actual images in Cloudinary)

**Migration Scripts Location:**
```bash
Database/Tables/T700_gallery_categories.sql
Database/Tables/T710_gallery_images.sql
Database/DataLoads/DL701_gallery_categories.sql
```

**Execute Migration (Production Database):**

**Option A: Automated Script (Windows)**
```powershell
# Create a PowerShell script: deploy_gallery_production.ps1
$DB_URL = "postgresql://sunrise_admin:password@host/database"

# Run migrations
& psql $DB_URL -f Database/Tables/T700_gallery_categories.sql
& psql $DB_URL -f Database/Tables/T710_gallery_images.sql
& psql $DB_URL -f Database/DataLoads/DL701_gallery_categories.sql
```

**Option B: Manual Commands**
```bash
# Set your production database connection string
DB_URL="postgresql://sunrise_admin:password@dpg-xxx.singapore-postgres.render.com/sunrise_school_db"

# Create gallery_categories table
psql "$DB_URL" -f Database/Tables/T700_gallery_categories.sql

# Create gallery_images table
psql "$DB_URL" -f Database/Tables/T710_gallery_images.sql

# Load initial 10 categories
psql "$DB_URL" -f Database/DataLoads/DL701_gallery_categories.sql
```

**Verify Migration:**
```sql
-- Connect to database
psql "$DB_URL"

-- Check tables exist
\dt gallery*

-- Check categories loaded
SELECT COUNT(*) FROM gallery_categories;
-- Expected: 10

-- View categories
SELECT id, name, display_order FROM gallery_categories ORDER BY display_order;
```

---

### **Step 2: Cloudinary Configuration**

**Sign up for Cloudinary:**
1. Visit: https://cloudinary.com/
2. Create free account (25 GB storage, 25 GB bandwidth/month)
3. Note your credentials from dashboard

**Add Environment Variables to Render.com:**

Navigate to: Render Dashboard → Your Backend Service → Environment

Add these 3 variables:
```bash
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

**Example (Production Values):**
```bash
CLOUDINARY_CLOUD_NAME=dqfxyrvti
CLOUDINARY_API_KEY=923627892216717
CLOUDINARY_API_SECRET=WLjFTK1ARsx3idcJGSU7DxuimII
```

**⚠️ Important:** Keep these credentials secure! Do not commit to Git.

---

### **Step 3: Backend Code Verification**

**Verify Dependencies:**
```bash
# Check requirements.txt includes:
cloudinary==1.41.0
```

**Verify Cloudinary Configuration:**
```python
# app/core/cloudinary_config.py should exist
# Initializes Cloudinary SDK with credentials from environment variables
```

**Verify Gallery Endpoints:**
```python
# app/api/v1/endpoints/gallery.py should include:
# - GET /categories
# - POST /images/upload
# - PUT /images/{id}
# - DELETE /images/{id}
```

**Verify Public Endpoints:**
```python
# app/api/v1/endpoints/public.py should include:
# - GET /public/gallery
# - GET /public/gallery/home-page
```

---

### **Step 4: Deploy Backend**

**Trigger Deployment:**
1. Push code to Git repository
2. Render.com auto-deploys (or click "Manual Deploy")
3. Monitor deployment logs
4. Wait for completion (~3-5 minutes)

**Verify Deployment:**
```bash
# Test health endpoint
curl https://your-backend-url.onrender.com/

# Test gallery categories endpoint
curl https://your-backend-url.onrender.com/api/v1/gallery/categories

# Expected: Array of 10 categories
```

---

### **Step 5: Test Gallery Functionality**

**Test Public Endpoints (No Authentication):**
```bash
# Get public gallery (grouped by category)
curl https://your-backend-url.onrender.com/api/v1/public/gallery

# Get home page carousel images
curl https://your-backend-url.onrender.com/api/v1/public/gallery/home-page
# Expected: Empty array [] (no images marked for home page yet)
```

**Test Admin Endpoints (With Authentication):**
```bash
# 1. Login as admin
curl -X POST "https://your-backend-url.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sunrise.com","password":"admin123"}'

# Save the access_token from response

# 2. Upload test image (use Swagger UI for easier testing)
# Visit: https://your-backend-url.onrender.com/docs
# Navigate to: POST /api/v1/gallery/images/upload
# Click "Authorize" and enter token
# Upload a test image with metadata

# 3. Verify image uploaded
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-backend-url.onrender.com/api/v1/gallery/images
```

---

### **Step 6: Gallery Database Schema**

**gallery_categories Table:**
```sql
CREATE TABLE gallery_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),                    -- Material-UI icon name
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

**Initial Categories (10):**
1. Independence Day
2. School Premises
3. First Day of School
4. Sports Day
5. Annual Function
6. Republic Day
7. Science Exhibition
8. Cultural Events
9. Classroom Activities
10. Teachers Day

**gallery_images Table:**
```sql
CREATE TABLE gallery_images (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES gallery_categories(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    cloudinary_public_id VARCHAR(255) NOT NULL UNIQUE,
    cloudinary_url TEXT NOT NULL,
    cloudinary_thumbnail_url TEXT,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_visible_on_home_page BOOLEAN DEFAULT FALSE,  -- For home page carousel
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

**Indexes Created:**
- `idx_gallery_categories_active` - Fast filtering by active status
- `idx_gallery_categories_display_order` - Ordered category display
- `idx_gallery_images_category` - Fast category-based queries
- `idx_gallery_images_active` - Fast filtering by active status
- `idx_gallery_images_home_page` - Fast home page queries
- `idx_gallery_images_display_order` - Ordered image display
- `idx_gallery_images_upload_date` - Chronological sorting
- `idx_gallery_images_home_page_active` - Composite index for home carousel

---

### **Step 7: Cloudinary Integration Details**

**Upload Configuration:**
```python
# Backend automatically configures:
# - Folder: gallery/
# - Quality: auto (optimized for web)
# - Format: auto (WebP/AVIF for modern browsers)
# - Thumbnail: 400x300px, crop-fill, auto-quality
```

**Image Transformations:**
```python
# Original image URL:
https://res.cloudinary.com/dqfxyrvti/image/upload/v1234567890/gallery/image.jpg

# Thumbnail URL (auto-generated):
https://res.cloudinary.com/dqfxyrvti/image/upload/w_400,h_300,c_fill,q_auto,f_auto/v1234567890/gallery/image.jpg
```

**Storage Limits (Free Tier):**
- Storage: 25 GB
- Bandwidth: 25 GB/month
- Transformations: 25,000/month
- Estimated capacity: ~200-300 high-quality images

---

### **Step 8: Gallery API Endpoints Reference**

**Public Endpoints (No Auth Required):**

**GET /api/v1/public/gallery**
- Returns: Gallery images grouped by category
- Use case: Public gallery page
- Response: Array of categories with images

**GET /api/v1/public/gallery/home-page**
- Returns: Featured images for home page carousel
- Filter: `is_visible_on_home_page = true`
- Limit: Default 10 images
- Order: `display_order ASC`, `upload_date DESC`

**Admin Endpoints (Auth Required):**

**GET /api/v1/gallery/categories**
- Returns: All gallery categories
- Filters: `is_active` (optional)

**POST /api/v1/gallery/images/upload**
- Uploads image to Cloudinary
- Saves metadata to database
- Required fields:
  - `file`: Image file (multipart/form-data)
  - `category_id`: Category ID
  - `title`: Image title
- Optional fields:
  - `description`: Image description
  - `display_order`: Display order (default: 0)
  - `is_visible_on_home_page`: Show on home page (default: false)

**PUT /api/v1/gallery/images/{id}**
- Updates image metadata
- Validates duplicate display_order within same category
- Cannot update: `cloudinary_public_id`, `cloudinary_url`

**DELETE /api/v1/gallery/images/{id}**
- Deletes image from Cloudinary
- Deletes metadata from database
- Cascade: Removes from home page carousel if marked

---

### **Step 9: Troubleshooting Gallery Issues**

**Issue: Upload Fails**
```bash
# Check Cloudinary credentials
echo $CLOUDINARY_CLOUD_NAME
echo $CLOUDINARY_API_KEY
echo $CLOUDINARY_API_SECRET

# Verify credentials in Render dashboard
# Ensure no trailing spaces in values
```

**Issue: Images Not Displaying**
```sql
-- Check if images are active
SELECT id, title, is_active FROM gallery_images WHERE is_active = FALSE;

-- Activate images if needed
UPDATE gallery_images SET is_active = TRUE WHERE id = <image_id>;
```

**Issue: Home Page Carousel Empty**
```sql
-- Check if any images marked for home page
SELECT id, title, is_visible_on_home_page
FROM gallery_images
WHERE is_visible_on_home_page = TRUE;

-- Mark images for home page if needed
UPDATE gallery_images
SET is_visible_on_home_page = TRUE
WHERE id IN (1, 2, 3, 4, 5);
```

**Issue: Duplicate Display Order Error**
```sql
-- Check for duplicate display orders in same category
SELECT category_id, display_order, COUNT(*)
FROM gallery_images
GROUP BY category_id, display_order
HAVING COUNT(*) > 1;

-- Fix duplicates by updating display orders
UPDATE gallery_images SET display_order = <new_order> WHERE id = <image_id>;
```

---

### **Step 10: Post-Deployment Gallery Tasks**

**1. Upload Initial Images:**
- Login as admin
- Navigate to Gallery Management
- Upload 5-10 images per category
- Set appropriate display orders
- Mark 3-5 best images for home page

**2. Configure Home Page Carousel:**
- Select high-quality images
- Mix different categories for variety
- Use landscape orientation (16:9 or 4:3)
- Set display orders: 1, 2, 3, 4, 5...
- Test carousel on mobile and desktop

**3. Monitor Cloudinary Usage:**
- Check storage usage monthly
- Monitor bandwidth consumption
- Optimize images if approaching limits
- Consider upgrading plan if needed

**4. Backup Strategy:**
```bash
# Backup gallery tables
pg_dump -U sunrise_admin \
  -h dpg-xxx.singapore-postgres.render.com \
  -d sunrise_school_db \
  -t gallery_categories -t gallery_images \
  > gallery_backup_$(date +%Y%m%d).sql

# Download important images from Cloudinary as backup
# Use Cloudinary dashboard or API
```

---

## 🎯 **Production Deployment Checklist**

### **Security**
- [ ] Environment variables secured (no hardcoded secrets)
- [ ] CORS origins restricted to production domains
- [ ] Rate limiting enabled for authentication endpoints
- [ ] Input validation implemented for all endpoints
- [ ] SQL injection prevention verified
- [ ] HTTPS enforced (handled by Render)

### **Performance**
- [ ] Database connection pooling configured
- [ ] Query optimization implemented
- [ ] Caching strategy deployed
- [ ] API response times < 500ms for most endpoints
- [ ] Memory usage optimized

### **Monitoring**
- [ ] Health check endpoints implemented
- [ ] Request logging enabled
- [ ] Error tracking configured
- [ ] Performance monitoring set up
- [ ] Database query monitoring enabled

### **Reliability**
- [ ] Graceful error handling implemented
- [ ] Database connection retry logic
- [ ] Proper HTTP status codes returned
- [ ] API documentation up to date
- [ ] Backup and recovery procedures tested

---

**Backend deployment completed successfully!** 🎉
**Production-ready FastAPI service with comprehensive security, monitoring, and performance optimizations.**
**API service ready for frontend integration and production use.**
