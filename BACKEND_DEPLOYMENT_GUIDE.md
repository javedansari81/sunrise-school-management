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
  -d "username=admin@sunriseschool.edu&password=admin123"

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

### **Deployment**
- [ ] Repository connected to Render
- [ ] Build and start commands configured
- [ ] Environment variables set
- [ ] Service deployed successfully
- [ ] Health checks passing

### **Post-Deployment**
- [ ] API documentation accessible
- [ ] Authentication working
- [ ] Database connectivity verified
- [ ] All endpoints responding
- [ ] Frontend integration tested

---

## 🔗 **Next Steps**

After successful backend deployment:

1. **Frontend Deployment**: Follow `FRONTEND_DEPLOYMENT_GUIDE.md`
2. **Integration Testing**: Test complete user workflows
3. **Performance Optimization**: Monitor and optimize slow queries
4. **Security Hardening**: Review and enhance security measures

---

**Backend deployment completed successfully!** 🎉  
**API service ready for frontend integration and production use.**
