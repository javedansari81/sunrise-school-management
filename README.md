# Sunrise National Public School - Management System

A comprehensive school management system built with React (TypeScript) frontend and FastAPI backend.

## Features

### 🏠 **Public Website**
- Beautiful landing page with image slider
- School information and achievements
- Responsive design for all devices
- Professional school branding

### 🔐 **Admin Portal**
- Secure authentication system
- Role-based access control
- Comprehensive dashboard with key metrics

### 💰 **Fees Management**
- Multiple payment options (Monthly, Quarterly, Half-yearly, Yearly)
- Partial payment support with balance tracking
- Advanced filtering and search
- Payment history and reports
- Multiple payment methods (Cash, Cheque, Online, UPI, Card)

### 📝 **Leave Management**
- Student leave request system
- Approval workflow for administrators
- Leave history and tracking
- Different leave types (Sick, Casual, Emergency, etc.)

### 💼 **Expense Management**
- School expense tracking and approval
- Category-wise expense management
- Vendor management
- Monthly and yearly reports

### 👨‍🎓 **Student Management**
- Complete student profiles
- Academic records tracking
- Parent information management
- Class-wise student organization (PG to Class 8)

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Material-UI (MUI)** for UI components
- **React Router** for navigation
- **Axios** for API communication
- **React Slick** for image carousel

### Backend
- **FastAPI** with Python 3.11
- **SQLAlchemy** for database ORM
- **PostgreSQL** database
- **JWT** authentication
- **Pydantic** for data validation

### Deployment
- **Docker** containerization
- **Docker Compose** for orchestration
- **Nginx** reverse proxy
- **Render** deployment ready

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose (for containerized deployment)

### Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd sunrise-school-management
```

2. **Backend Setup**
```bash
cd sunrise-backend-fastapi
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python main.py
```

3. **Frontend Setup**
```bash
cd sunrise-school-frontend
npm install
npm start
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Docker Deployment

1. **Development Environment**
```bash
docker-compose up -d
```

2. **Production Environment**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Admin Access

**Demo Credentials:**
- Email: admin@sunrise.com
- Password: admin123

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user

### Students
- `GET /api/v1/students` - Get all students
- `POST /api/v1/students` - Create student
- `GET /api/v1/students/{id}` - Get student details
- `PUT /api/v1/students/{id}` - Update student
- `DELETE /api/v1/students/{id}` - Delete student

### Fees Management
- `GET /api/v1/fees` - Get fee records with filters
- `POST /api/v1/fees` - Create fee record
- `POST /api/v1/fees/payment` - Process payment
- `GET /api/v1/fees/history/{student_id}` - Payment history

### Leave Management
- `GET /api/v1/leaves` - Get leave requests
- `POST /api/v1/leaves` - Create leave request
- `PATCH /api/v1/leaves/{id}/approve` - Approve leave
- `PATCH /api/v1/leaves/{id}/reject` - Reject leave

### Expense Management
- `GET /api/v1/expenses` - Get expenses
- `POST /api/v1/expenses` - Create expense
- `PATCH /api/v1/expenses/{id}/approve` - Approve expense
- `GET /api/v1/expenses/categories` - Get categories

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/sunrise_school
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_SCHOOL_NAME=Sunrise National Public School
```

## Deployment on Render

1. **Fork this repository**

2. **Create a new Web Service on Render**
   - Connect your GitHub repository
   - Use `docker-compose.prod.yml`
   - Set environment variables

3. **Environment Variables for Render**
```
DATABASE_URL=<your-postgres-url>
SECRET_KEY=<your-secret-key>
REACT_APP_API_URL=<your-backend-url>/api/v1
POSTGRES_PASSWORD=<your-postgres-password>
```

## Project Structure

```
sunrise-school-management/
├── sunrise-backend-fastapi/          # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/         # API endpoints
│   │   ├── core/                     # Core functionality
│   │   ├── models/                   # Database models
│   │   └── schemas/                  # Pydantic schemas
│   ├── main.py                       # Application entry point
│   └── requirements.txt              # Python dependencies
├── sunrise-school-frontend/          # React Frontend
│   ├── src/
│   │   ├── components/               # Reusable components
│   │   ├── pages/                    # Page components
│   │   └── services/                 # API services
│   └── package.json                  # Node dependencies
├── tests/                            # Centralized test suite
│   ├── backend/                      # Backend Python tests
│   ├── frontend/                     # Frontend React tests
│   └── scripts/                      # Test automation scripts
├── docs/                             # Organized documentation
├── Database/                         # Database scripts and migrations
├── docker-compose.yml                # Development compose
├── docker-compose.prod.yml           # Production compose
└── README.md                         # This file
```

## 📚 Documentation

Comprehensive documentation is organized in the `docs/` directory:

- **[📖 Complete Documentation](docs/README.md)** - Main documentation hub with organized categories
- **[🔧 Setup & Configuration](docs/setup/)** - Installation, configuration, and system preparation
- **[🧪 Testing Procedures](docs/testing/)** - Testing guides, procedures, and troubleshooting
- **[🚀 Deployment Guides](docs/deployment/)** - Production deployment for Render.com, DigitalOcean, and more
- **[⭐ Feature Documentation](docs/features/)** - Detailed feature implementation and design guides
- **[🗄️ Database Documentation](docs/database/)** - Database setup, schema, and management
- **[📊 API Documentation](http://localhost:8000/docs)** - Interactive Swagger UI (when backend is running)

### Quick Links
- **New Installation**: Start with [docs/setup/SETUP_AND_TESTING.md](docs/setup/SETUP_AND_TESTING.md)
- **Database Setup**: Follow [docs/database/SETUP_GUIDE.md](docs/database/SETUP_GUIDE.md)
- **Production Deployment**: Use [docs/deployment/RENDER_DEPLOYMENT_GUIDE.md](docs/deployment/RENDER_DEPLOYMENT_GUIDE.md)
- **Testing**: Check [tests/README.md](tests/README.md) for complete test suite documentation

## 🧪 Testing

The project includes a comprehensive test suite organized in the `tests/` directory:

### Quick Test Commands
```bash
# Backend tests
cd sunrise-backend-fastapi
python scripts/run_tests.py

# Frontend tests
cd sunrise-school-frontend
npm test

# PowerShell API tests
cd tests/scripts/powershell/leave-management
.\test_api_request.ps1
```

### Test Categories
- **[Backend Tests](tests/backend/)** - Python unit, integration, and API tests
- **[Frontend Tests](tests/frontend/)** - React component and context tests
- **[Script Tests](tests/scripts/)** - PowerShell and web-based testing tools

For detailed testing instructions, see [tests/README.md](tests/README.md).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.

Doc Ref: 
Google Docs: 
https://docs.google.com/document/d/1kvFJdZbMeBRRjgMd46Fu7Y87U9oB0iGtHmurn-Fq3c0/edit?tab=t.w7mhsp5tn0sz

Confluence Page: 
https://sunrise-school-website.atlassian.net/wiki/spaces/SS/pages/590137/Technical+Analysis+Sunrise+School
