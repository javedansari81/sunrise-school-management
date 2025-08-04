# Sunrise School Management System - Setup and Testing Guide

This guide provides comprehensive instructions for setting up and testing the Sunrise School Management System, which consists of a FastAPI backend and React frontend with complete authentication and page implementations.

## 🏗️ System Architecture

- **Backend**: FastAPI with PostgreSQL database, JWT authentication
- **Frontend**: React with TypeScript, Material-UI, and comprehensive page implementations
- **Authentication**: JWT-based with proper login/logout functionality
- **Pages**: Complete implementation of all school website pages and admin panels

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL (optional, can use SQLite for development)
- Git

## 🚀 Backend Setup

### 1. Navigate to Backend Directory
```bash
cd sunrise-backend-fastapi
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Initialize database and create default admin user
python scripts/setup.py
```

### 5. Start Backend Server
```bash
python main.py
```

The backend will be available at `http://localhost:8000`

## 🎨 Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd sunrise-school-frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Start Frontend Development Server
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## 🔐 Default Login Credentials

- **Email**: admin@sunriseschool.edu
- **Password**: admin123

## 📄 Implemented Pages

### Public Pages
- **Home** (`/`) - School homepage with hero section and overview
- **About** (`/about`) - School mission, vision, values, and history
- **Academics** (`/academics`) - Academic programs, facilities, and methodology
- **Admissions** (`/admissions`) - Admission process, fees, and contact information
- **Faculty** (`/faculty`) - Faculty profiles and department information
- **Gallery** (`/gallery`) - Photo gallery with categorized images
- **Contact** (`/contact`) - Contact information and inquiry form

### Admin Pages (Protected)
- **Admin Dashboard** (`/admin/dashboard`) - Overview and statistics
- **Fees Management** (`/admin/fees`) - Student fee management
- **Leave Management** (`/admin/leaves`) - Staff leave request management
- **Expense Management** (`/admin/expenses`) - School expense tracking
- **Student Profiles** (`/admin/students`) - Student information management

## 🧪 Testing

### Backend Tests

#### Run All Tests
```bash
cd sunrise-backend-fastapi
python scripts/run_tests.py
```

#### Run Authentication Tests Only
```bash
python scripts/run_tests.py auth
```

#### Run Code Linting
```bash
python scripts/run_tests.py lint
```

#### Run Integration Tests
```bash
# Make sure the server is running first
python main.py

# In another terminal
python scripts/integration_test.py
```

### Frontend Tests

#### Run React Tests
```bash
cd sunrise-school-frontend
npm test
```

#### Run Authentication Context Tests
```bash
npm test -- --testPathPattern=AuthContext
```

## 🔧 API Documentation

With the backend running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key API Endpoints

#### Authentication
- `POST /api/v1/auth/login-json` - Login with JSON payload
- `POST /api/v1/auth/login` - Login with OAuth2 form
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/protected` - Test protected route

#### Other Endpoints
- `GET /health` - Health check
- `GET /api/v1/test` - API test endpoint

## 🔍 Features Implemented

### Authentication System
- ✅ JWT-based authentication
- ✅ Password hashing with bcrypt
- ✅ Token validation and refresh
- ✅ Protected routes
- ✅ Login/logout functionality
- ✅ User registration
- ✅ Authentication context in React

### Frontend Features
- ✅ Responsive design with Material-UI
- ✅ Complete page implementations
- ✅ Authentication state management
- ✅ Protected admin routes
- ✅ Logout functionality in header
- ✅ Form validation and error handling
- ✅ Loading states and user feedback

### Backend Features
- ✅ FastAPI with async/await
- ✅ SQLAlchemy ORM with async support
- ✅ Database migrations with Alembic
- ✅ CORS configuration
- ✅ Comprehensive error handling
- ✅ API documentation with Swagger

## 🐛 Troubleshooting

### Backend Issues

#### Database Connection Error
```bash
# Check if PostgreSQL is running or use SQLite for development
# Update DATABASE_URL in app/core/config.py
```

#### Import Errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Authentication Errors
```bash
# Create default admin user
python scripts/setup.py
```

### Frontend Issues

#### Module Not Found
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### API Connection Issues
```bash
# Check if backend is running on port 8000
# Verify CORS settings in backend
```

## 📝 Development Notes

### Code Structure
- Backend follows FastAPI best practices with proper separation of concerns
- Frontend uses React hooks and context for state management
- Authentication is handled consistently across both frontend and backend
- All pages are fully implemented with proper styling and functionality

### Security Features
- Passwords are hashed using bcrypt
- JWT tokens have configurable expiration
- Protected routes require valid authentication
- CORS is properly configured for development

### Testing Coverage
- Authentication system is thoroughly tested
- Integration tests verify end-to-end functionality
- Frontend authentication context has comprehensive tests

## 🚀 Next Steps

1. **Database Migration**: Set up PostgreSQL for production
2. **Environment Configuration**: Configure environment variables for different stages
3. **Deployment**: Deploy to production servers
4. **Additional Features**: Implement remaining CRUD operations for all entities
5. **Performance**: Add caching and optimization
6. **Monitoring**: Add logging and monitoring systems

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure both backend and frontend servers are running
4. Check the console logs for detailed error messages

The system is now fully functional with complete authentication and all pages implemented!
