# 🚨 URGENT: Render.com Environment Configuration Fix
## Backend Server Connection Issue Resolution

### 🔍 Problem Diagnosis
Your "Backend server is not running" error is caused by:
1. **CORS Configuration Issues** - Backend not allowing frontend origin
2. **Environment Variable Mismatches** - Incorrect API URLs
3. **Service Name Inconsistencies** - Documentation vs actual deployment

### 🛠️ IMMEDIATE FIXES REQUIRED

#### 1. Backend Service Environment Variables
**Go to your Render.com Backend Service → Environment Tab**

**CRITICAL: Update these environment variables:**

```bash
# Database (Copy from your PostgreSQL service)
DATABASE_URL=postgresql://username:password@host:port/database

# Security
SECRET_KEY=sunrise-school-secret-key-2024-production-india
ENVIRONMENT=production

# CORS - MUST MATCH YOUR ACTUAL FRONTEND URL
BACKEND_CORS_ORIGINS=https://sunrise-school-frontend-web.onrender.com

# Optional: JWT Settings
JWT_SECRET_KEY=a436afdbaade6c5ae255289d8aa80103adbd4f622b4a99077bb40ac9140b8368a
```

#### 2. Frontend Service Environment Variables
**Go to your Render.com Frontend Service → Environment Tab**

**CRITICAL: Update these environment variables:**

```bash
# API URL - MUST MATCH YOUR ACTUAL BACKEND URL
REACT_APP_API_URL=https://sunrise-school-backend-api.onrender.com/api/v1

# School Name
REACT_APP_SCHOOL_NAME=Sunrise National Public School
```

### 🔍 Verify Your Actual Service URLs

**IMPORTANT:** Your documentation shows these URLs, but verify they match your actual Render services:

- **Backend**: `https://sunrise-school-backend-api.onrender.com`
- **Frontend**: `https://sunrise-school-frontend-web.onrender.com`

**To check your actual URLs:**
1. Go to Render.com Dashboard
2. Click on each service
3. Copy the actual URL from the service page
4. Update environment variables accordingly

### 🧪 Testing Steps

#### Step 1: Test Backend Health
Visit: `https://your-actual-backend-url.onrender.com/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "Sunrise Backend FastAPI",
  "environment": "production",
  "database": "connected",
  "cors_origins": ["https://your-frontend-url.onrender.com"]
}
```

#### Step 2: Test API Endpoint
Visit: `https://your-actual-backend-url.onrender.com/api/v1/test`

**Expected Response:**
```json
{
  "message": "API v1 is working!",
  "endpoint": "/api/v1/test",
  "environment": "production",
  "timestamp": "2025-01-26"
}
```

#### Step 3: Test Leave Management API
Visit: `https://your-actual-backend-url.onrender.com/docs`

Look for `/api/v1/leaves/` endpoints and test them.

### 🚨 Common Issues & Solutions

#### Issue 1: Service Names Don't Match
**Problem:** Documentation shows `sunrise-school-backend-api` but actual service is named differently.

**Solution:**
1. Check actual service names in Render dashboard
2. Update environment variables with correct URLs
3. Update documentation

#### Issue 2: CORS Still Blocking
**Problem:** Frontend still can't connect after CORS fix.

**Solution:**
1. Ensure `BACKEND_CORS_ORIGINS` exactly matches frontend URL
2. No trailing slashes in URLs
3. Use `https://` not `http://`

#### Issue 3: Database Connection Failed
**Problem:** Backend health check shows database error.

**Solution:**
1. Copy DATABASE_URL from PostgreSQL service dashboard
2. Ensure PostgreSQL service is running
3. Check database service region matches backend region

### 📋 Deployment Checklist

- [ ] Update backend `BACKEND_CORS_ORIGINS` with actual frontend URL
- [ ] Update frontend `REACT_APP_API_URL` with actual backend URL
- [ ] Set backend `ENVIRONMENT=production`
- [ ] Copy correct `DATABASE_URL` from PostgreSQL service
- [ ] Test `/health` endpoint
- [ ] Test `/api/v1/test` endpoint
- [ ] Test Leave Management System in frontend
- [ ] Verify all services are in same region (Singapore recommended)

### 🔄 After Making Changes

1. **Redeploy Backend Service** (Environment changes require redeploy)
2. **Redeploy Frontend Service** (Build-time environment variables require rebuild)
3. **Wait 2-3 minutes** for services to fully restart
4. **Test the health endpoints** before testing frontend
5. **Clear browser cache** when testing frontend

### 📞 Emergency Debugging

If issues persist, check these URLs in order:

1. `https://your-backend-url.onrender.com/` - Should show welcome message
2. `https://your-backend-url.onrender.com/health` - Should show health status
3. `https://your-backend-url.onrender.com/docs` - Should show API documentation
4. `https://your-frontend-url.onrender.com/` - Should load without backend errors

**Next Steps:** After fixing environment variables, test the Leave Management System specifically.
