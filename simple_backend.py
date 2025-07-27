from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Sunrise Backend FastAPI",
    version="1.0.0",
    description="Sunrise School Management System API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to Sunrise Backend FastAPI!",
        "status": "running",
        "docs": "Visit /docs for API documentation"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Sunrise Backend FastAPI"}

@app.get("/api/v1/test")
async def test_api():
    return {
        "message": "API v1 is working!",
        "endpoint": "/api/v1/test",
        "timestamp": "2025-01-26"
    }

# Authentication endpoints
@app.post("/api/v1/auth/login")
async def login():
    return {
        "message": "Login endpoint - working",
        "access_token": "placeholder_token",
        "token_type": "bearer"
    }

@app.post("/api/v1/auth/register")
async def register():
    return {"message": "Register endpoint - working"}

@app.get("/api/v1/auth/me")
async def get_current_user():
    return {"message": "Get current user endpoint - working"}

# Students endpoints
@app.get("/api/v1/students")
async def get_students():
    return {
        "message": "Get students endpoint - working",
        "students": [
            {"id": 1, "name": "John Doe", "class": "Class 5", "admission_number": "SNS2024001"},
            {"id": 2, "name": "Sarah Johnson", "class": "Class 3", "admission_number": "SNS2024002"},
            {"id": 3, "name": "Mike Davis", "class": "Class 7", "admission_number": "SNS2024003"}
        ]
    }

@app.post("/api/v1/students")
async def create_student():
    return {"message": "Create student endpoint - working"}

@app.get("/api/v1/students/{student_id}")
async def get_student(student_id: int):
    return {
        "message": f"Get student {student_id} endpoint - working",
        "student": {
            "id": student_id,
            "name": "John Doe",
            "class": "Class 5",
            "admission_number": "SNS2024001"
        }
    }

# Fees endpoints
@app.get("/api/v1/fees")
async def get_fees():
    return {
        "message": "Get fees endpoint - working",
        "fees": [
            {
                "id": 1,
                "student_name": "John Doe",
                "admission_number": "SNS2024001",
                "class": "Class 5",
                "total_amount": 15000,
                "paid_amount": 10000,
                "balance_amount": 5000,
                "status": "Partial"
            },
            {
                "id": 2,
                "student_name": "Sarah Johnson",
                "admission_number": "SNS2024002",
                "class": "Class 3",
                "total_amount": 5000,
                "paid_amount": 5000,
                "balance_amount": 0,
                "status": "Paid"
            }
        ]
    }

@app.post("/api/v1/fees/payment")
async def process_fee_payment():
    return {"message": "Process fee payment endpoint - working"}

# Leave endpoints
@app.get("/api/v1/leaves")
async def get_leave_requests():
    return {
        "message": "Get leave requests endpoint - working",
        "leaves": [
            {
                "id": 1,
                "student_name": "John Doe",
                "leave_type": "Sick Leave",
                "start_date": "2024-01-15",
                "end_date": "2024-01-17",
                "status": "Pending"
            }
        ]
    }

@app.post("/api/v1/leaves")
async def create_leave_request():
    return {"message": "Create leave request endpoint - working"}

# Expenses endpoints
@app.get("/api/v1/expenses")
async def get_expenses():
    return {
        "message": "Get expenses endpoint - working",
        "expenses": [
            {
                "id": 1,
                "title": "Office Supplies",
                "category": "Supplies",
                "amount": 5000,
                "status": "Pending"
            }
        ]
    }

@app.post("/api/v1/expenses")
async def create_expense():
    return {"message": "Create expense endpoint - working"}

# Teachers endpoints
@app.get("/api/v1/teachers")
async def get_teachers():
    return {
        "message": "Get teachers endpoint - working",
        "teachers": [
            {"id": 1, "name": "Mrs. Smith", "subject": "Mathematics", "class": "Class 5"},
            {"id": 2, "name": "Mr. Johnson", "subject": "English", "class": "Class 3"}
        ]
    }

@app.post("/api/v1/teachers")
async def create_teacher():
    return {"message": "Create teacher endpoint - working"}

# Events endpoints
@app.get("/api/v1/events")
async def get_events():
    return {
        "message": "Get events endpoint - working",
        "events": [
            {"id": 1, "title": "Annual Sports Day", "date": "2024-02-15", "description": "School sports event"},
            {"id": 2, "title": "Science Fair", "date": "2024-03-10", "description": "Student science projects"}
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "simple_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
