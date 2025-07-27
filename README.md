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
- Email: admin@sunriseschool.edu
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
├── docker-compose.yml                # Development compose
├── docker-compose.prod.yml           # Production compose
└── README.md                         # This file
```

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
