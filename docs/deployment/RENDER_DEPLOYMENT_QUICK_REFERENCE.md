# 🚀 Render.com Deployment Quick Reference
## Sunrise School Management System

### 📋 Service Names & URLs (Copy-Paste Ready)

#### Database Service:
```
Name: sunrise-school-postgres-db
Database: sunrise_school_db
User: sunrise_admin
PostgreSQL Version: 15
Region: Singapore
```

#### Backend Service:
```
Name: sunrise-school-backend-api
URL: https://sunrise-school-backend-api.onrender.com
API Docs: https://sunrise-school-backend-api.onrender.com/docs
Root Directory: sunrise-backend-fastapi
```

#### Frontend Service:
```
Name: sunrise-school-frontend-web
URL: https://sunrise-school-frontend-web.onrender.com
Root Directory: sunrise-school-frontend
```

### 🔧 Environment Variables

#### Backend Environment Variables:
```
DATABASE_URL: [Copy from database dashboard]
SECRET_KEY: sunrise-school-secret-key-2024-production-india
ENVIRONMENT: production
BACKEND_CORS_ORIGINS: https://sunrise-school-frontend-web.onrender.com
```

#### Frontend Environment Variables:
```
REACT_APP_API_URL: https://sunrise-school-backend-api.onrender.com/api/v1
REACT_APP_SCHOOL_NAME: Sunrise National Public School
```

### 🌏 Recommended Settings

#### Region Selection:
- **Primary**: Singapore (best for India)
- **Alternative**: Frankfurt (EU)

#### Plans:
- **Testing**: Free tier for all services
- **Production**: Starter ($7/month) for backend + database

### 🔑 Test Credentials

```
Admin: admin@sunriseschool.edu / admin123
Teacher: teacher@sunriseschool.edu / admin123
Student: student@sunriseschool.edu / admin123
```

### 📝 Deployment Checklist

- [ ] Create Render account with GitHub
- [ ] Deploy PostgreSQL database (Singapore region)
- [ ] Deploy backend service with environment variables
- [ ] Deploy frontend service with environment variables
- [ ] Update CORS settings in backend
- [ ] Initialize database with sample data
- [ ] Test all login credentials
- [ ] Verify API documentation access
- [ ] Check performance from India
- [ ] Set up custom domain (optional)

### 🚨 Common Commands

#### Database Setup (Backend Shell):
```bash
cd /opt/render/project/src
python setup_database.py
```

#### Check Service Status:
- Backend health: `https://sunrise-school-backend-api.onrender.com/health`
- API docs: `https://sunrise-school-backend-api.onrender.com/docs`

### 🌐 Custom Domain Setup

#### DNS Records:
```
Type: CNAME
Name: school
Value: sunrise-school-frontend-web.onrender.com
TTL: 300
```

#### API Subdomain (Optional):
```
Type: CNAME
Name: api
Value: sunrise-school-backend-api.onrender.com
TTL: 300
```

---
**💡 Pro Tip**: Keep this reference handy during deployment for quick copy-paste of service names and URLs!
