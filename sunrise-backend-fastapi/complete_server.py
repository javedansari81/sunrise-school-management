#!/usr/bin/env python3
"""
Complete Sunrise School Management System Server with Full CRUD Operations
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from datetime import timedelta, datetime, date
from typing import Optional, List
import bcrypt
import json
import base64

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Create FastAPI app
app = FastAPI(
    title="🏫 Sunrise School Management System",
    version="1.0.0",
    description="Complete School Management System with Full CRUD Operations",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict
    permissions: List[str]

class StudentCreate(BaseModel):
    admission_number: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    current_class: str
    section: Optional[str] = None
    father_name: str
    mother_name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    current_class: Optional[str] = None
    section: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None

class TeacherCreate(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    position: str
    department: Optional[str] = None
    qualification: str
    joining_date: date

class TeacherUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None

class FeeCreate(BaseModel):
    student_id: int
    session_year: str
    payment_type: str
    total_amount: float
    due_date: date

class LeaveCreate(BaseModel):
    student_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: str

class ExpenseCreate(BaseModel):
    title: str
    category: str
    amount: float
    expense_date: date
    vendor_name: Optional[str] = None

# Mock data (in production, this would come from database)
MOCK_ADMIN = {
    "id": 1,
    "email": "admin@sunriseschool.edu",
    "password_hash": "$2b$12$wq4BwIaHKkm5IPdmm9rvz.pyOmvDofmSGt9m5zJrRiv8Q6IuDM5tC",
    "first_name": "Admin",
    "last_name": "User",
    "user_type": "admin",
    "is_active": True
}

MOCK_TEACHER = {
    "id": 2,
    "email": "teacher@sunriseschool.edu",
    "password_hash": "$2b$12$wq4BwIaHKkm5IPdmm9rvz.pyOmvDofmSGt9m5zJrRiv8Q6IuDM5tC",
    "first_name": "John",
    "last_name": "Teacher",
    "user_type": "teacher",
    "is_active": True
}

MOCK_STUDENT = {
    "id": 3,
    "email": "student@sunriseschool.edu",
    "password_hash": "$2b$12$wq4BwIaHKkm5IPdmm9rvz.pyOmvDofmSGt9m5zJrRiv8Q6IuDM5tC",
    "first_name": "Jane",
    "last_name": "Student",
    "user_type": "student",
    "is_active": True
}

# Mock data storage
students_db = []
teachers_db = []
fees_db = []
leaves_db = []
expenses_db = []

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except:
        return False

def create_access_token(data: dict):
    token_data = {"sub": data["email"], "user_id": data["id"], "user_type": data["user_type"]}
    token = base64.b64encode(json.dumps(token_data).encode()).decode()
    return token

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = json.loads(base64.b64decode(token).decode())
        email = payload.get("sub")
        if email == MOCK_ADMIN["email"]:
            return MOCK_ADMIN
        elif email == MOCK_TEACHER["email"]:
            return MOCK_TEACHER
        elif email == MOCK_STUDENT["email"]:
            return MOCK_STUDENT
    except:
        pass
    raise HTTPException(status_code=401, detail="Invalid token")

def get_user_permissions(user_type: str) -> List[str]:
    if user_type == "admin":
        return ["all_permissions"]
    elif user_type == "teacher":
        return ["view_students", "view_leaves", "create_expenses"]
    elif user_type == "student":
        return ["view_profile", "create_leaves"]
    return []

# Basic routes
@app.get("/")
async def root():
    return {
        "message": "🏫 Welcome to Sunrise School Management System!",
        "status": "running",
        "version": "1.0.0",
        "docs": "Visit /docs for API documentation",
        "features": [
            "Complete CRUD Operations",
            "Role-based Authentication",
            "Student Management",
            "Teacher Management", 
            "Fee Management",
            "Leave Management",
            "Expense Management"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Sunrise School Management System"}

# Authentication endpoints
@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users = [MOCK_ADMIN, MOCK_TEACHER, MOCK_STUDENT]
    for user in users:
        if form_data.username == user["email"]:
            if verify_password(form_data.password, user["password_hash"]):
                access_token = create_access_token(user)
                permissions = get_user_permissions(user["user_type"])
                return LoginResponse(
                    access_token=access_token,
                    token_type="bearer",
                    user={
                        "id": user["id"],
                        "email": user["email"],
                        "first_name": user["first_name"],
                        "last_name": user["last_name"],
                        "user_type": user["user_type"]
                    },
                    permissions=permissions
                )
    
    raise HTTPException(status_code=401, detail="Incorrect email or password")

@app.post("/api/v1/auth/login-json", response_model=LoginResponse)
async def login_json(login_data: LoginRequest):
    users = [MOCK_ADMIN, MOCK_TEACHER, MOCK_STUDENT]
    for user in users:
        if login_data.email == user["email"]:
            if verify_password(login_data.password, user["password_hash"]):
                access_token = create_access_token(user)
                permissions = get_user_permissions(user["user_type"])
                return LoginResponse(
                    access_token=access_token,
                    token_type="bearer",
                    user={
                        "id": user["id"],
                        "email": user["email"],
                        "first_name": user["first_name"],
                        "last_name": user["last_name"],
                        "user_type": user["user_type"]
                    },
                    permissions=permissions
                )
    
    raise HTTPException(status_code=401, detail="Incorrect email or password")

@app.get("/api/v1/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "first_name": current_user["first_name"],
        "last_name": current_user["last_name"],
        "user_type": current_user["user_type"]
    }

# Student Management Endpoints
@app.get("/api/v1/students/")
async def get_students(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all students with pagination and search"""
    filtered_students = students_db
    if search:
        filtered_students = [s for s in students_db if search.lower() in s.get('first_name', '').lower() or search.lower() in s.get('last_name', '').lower()]

    start = (page - 1) * per_page
    end = start + per_page

    return {
        "students": filtered_students[start:end],
        "total": len(filtered_students),
        "page": page,
        "per_page": per_page,
        "total_pages": (len(filtered_students) + per_page - 1) // per_page
    }

@app.post("/api/v1/students/")
async def create_student(student: StudentCreate, current_user: dict = Depends(get_current_user)):
    """Create a new student"""
    if current_user["user_type"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    new_student = {
        "id": len(students_db) + 1,
        **student.dict(),
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    students_db.append(new_student)
    return new_student

@app.get("/api/v1/students/{student_id}")
async def get_student(student_id: int, current_user: dict = Depends(get_current_user)):
    """Get student by ID"""
    student = next((s for s in students_db if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/api/v1/students/{student_id}")
async def update_student(student_id: int, student_update: StudentUpdate, current_user: dict = Depends(get_current_user)):
    """Update student information"""
    if current_user["user_type"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    student = next((s for s in students_db if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    for key, value in student_update.dict(exclude_unset=True).items():
        student[key] = value
    student["updated_at"] = datetime.now().isoformat()

    return student

@app.delete("/api/v1/students/{student_id}")
async def delete_student(student_id: int, current_user: dict = Depends(get_current_user)):
    """Delete (deactivate) student"""
    if current_user["user_type"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    student = next((s for s in students_db if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student["is_active"] = False
    student["updated_at"] = datetime.now().isoformat()

    return {"message": "Student deactivated successfully"}

@app.get("/api/v1/students/search")
async def search_students(q: str = Query(...), current_user: dict = Depends(get_current_user)):
    """Search students"""
    results = [s for s in students_db if q.lower() in s.get('first_name', '').lower() or q.lower() in s.get('last_name', '').lower() or q.lower() in s.get('admission_number', '').lower()]
    return {"students": results, "total": len(results)}

@app.get("/api/v1/students/dashboard/stats")
async def get_student_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get student dashboard statistics"""
    total_students = len([s for s in students_db if s.get("is_active", True)])
    return {
        "total_students": total_students,
        "active_students": total_students,
        "class_distribution": {},
        "gender_distribution": {}
    }

# Teacher Management Endpoints
@app.get("/api/v1/teachers/")
async def get_teachers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all teachers with pagination and search"""
    filtered_teachers = teachers_db
    if search:
        filtered_teachers = [t for t in teachers_db if search.lower() in t.get('first_name', '').lower() or search.lower() in t.get('last_name', '').lower()]

    start = (page - 1) * per_page
    end = start + per_page

    return {
        "teachers": filtered_teachers[start:end],
        "total": len(filtered_teachers),
        "page": page,
        "per_page": per_page,
        "total_pages": (len(filtered_teachers) + per_page - 1) // per_page
    }

@app.post("/api/v1/teachers/")
async def create_teacher(teacher: TeacherCreate, current_user: dict = Depends(get_current_user)):
    """Create a new teacher"""
    if current_user["user_type"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    new_teacher = {
        "id": len(teachers_db) + 1,
        **teacher.dict(),
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    teachers_db.append(new_teacher)
    return new_teacher

@app.get("/api/v1/teachers/{teacher_id}")
async def get_teacher(teacher_id: int, current_user: dict = Depends(get_current_user)):
    """Get teacher by ID"""
    teacher = next((t for t in teachers_db if t["id"] == teacher_id), None)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@app.put("/api/v1/teachers/{teacher_id}")
async def update_teacher(teacher_id: int, teacher_update: TeacherUpdate, current_user: dict = Depends(get_current_user)):
    """Update teacher information"""
    if current_user["user_type"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    teacher = next((t for t in teachers_db if t["id"] == teacher_id), None)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    for key, value in teacher_update.dict(exclude_unset=True).items():
        teacher[key] = value
    teacher["updated_at"] = datetime.now().isoformat()

    return teacher

@app.delete("/api/v1/teachers/{teacher_id}")
async def delete_teacher(teacher_id: int, current_user: dict = Depends(get_current_user)):
    """Delete (deactivate) teacher"""
    if current_user["user_type"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    teacher = next((t for t in teachers_db if t["id"] == teacher_id), None)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    teacher["is_active"] = False
    teacher["updated_at"] = datetime.now().isoformat()

    return {"message": "Teacher deactivated successfully"}

@app.get("/api/v1/teachers/dashboard/stats")
async def get_teacher_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get teacher dashboard statistics"""
    total_teachers = len([t for t in teachers_db if t.get("is_active", True)])
    return {
        "total_teachers": total_teachers,
        "active_teachers": total_teachers,
        "departments": [],
        "qualification_breakdown": []
    }

@app.get("/api/v1/teachers/options/departments")
async def get_departments(current_user: dict = Depends(get_current_user)):
    """Get all departments"""
    departments = list(set([t.get("department") for t in teachers_db if t.get("department")]))
    return {"departments": departments}

# Fee Management Endpoints
@app.get("/api/v1/fees/")
async def get_fees(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get all fee records"""
    start = (page - 1) * per_page
    end = start + per_page

    return {
        "fees": fees_db[start:end],
        "total": len(fees_db),
        "page": page,
        "per_page": per_page,
        "total_pages": (len(fees_db) + per_page - 1) // per_page,
        "summary": {"total_amount": 0, "paid_amount": 0, "pending_amount": 0}
    }

@app.post("/api/v1/fees/")
async def create_fee_record(fee: FeeCreate, current_user: dict = Depends(get_current_user)):
    """Create a new fee record"""
    if current_user["user_type"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    new_fee = {
        "id": len(fees_db) + 1,
        **fee.dict(),
        "paid_amount": 0.0,
        "balance_amount": fee.total_amount,
        "status": "Pending",
        "created_at": datetime.now().isoformat()
    }
    fees_db.append(new_fee)
    return new_fee

@app.get("/api/v1/fees/structure")
async def get_fee_structure(current_user: dict = Depends(get_current_user)):
    """Get fee structure"""
    return {
        "fee_structures": [
            {"class_name": "PG", "annual_fee": 25000},
            {"class_name": "LKG", "annual_fee": 28000},
            {"class_name": "UKG", "annual_fee": 30000},
            {"class_name": "Class 1", "annual_fee": 32000},
            {"class_name": "Class 2", "annual_fee": 34000},
            {"class_name": "Class 3", "annual_fee": 36000},
            {"class_name": "Class 4", "annual_fee": 38000},
            {"class_name": "Class 5", "annual_fee": 40000},
            {"class_name": "Class 6", "annual_fee": 42000},
            {"class_name": "Class 7", "annual_fee": 44000},
            {"class_name": "Class 8", "annual_fee": 46000}
        ]
    }

@app.get("/api/v1/fees/dashboard")
async def get_fee_dashboard(current_user: dict = Depends(get_current_user)):
    """Get fee dashboard data"""
    total_fees = sum(f.get("total_amount", 0) for f in fees_db)
    paid_fees = sum(f.get("paid_amount", 0) for f in fees_db)

    return {
        "total_students": len(students_db),
        "total_fees_collected": paid_fees,
        "total_fees_pending": total_fees - paid_fees,
        "overdue_fees": 0,
        "collection_rate": (paid_fees / total_fees * 100) if total_fees > 0 else 0
    }

# Leave Management Endpoints
@app.get("/api/v1/leaves/")
async def get_leaves(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get all leave requests"""
    start = (page - 1) * per_page
    end = start + per_page

    return {
        "leaves": leaves_db[start:end],
        "total": len(leaves_db),
        "page": page,
        "per_page": per_page,
        "total_pages": (len(leaves_db) + per_page - 1) // per_page
    }

@app.post("/api/v1/leaves/")
async def create_leave_request(leave: LeaveCreate, current_user: dict = Depends(get_current_user)):
    """Create a new leave request"""
    total_days = (leave.end_date - leave.start_date).days + 1

    new_leave = {
        "id": len(leaves_db) + 1,
        **leave.dict(),
        "total_days": total_days,
        "status": "Pending",
        "created_at": datetime.now().isoformat()
    }
    leaves_db.append(new_leave)
    return new_leave

@app.get("/api/v1/leaves/pending")
async def get_pending_leaves(current_user: dict = Depends(get_current_user)):
    """Get pending leave requests"""
    pending_leaves = [l for l in leaves_db if l.get("status") == "Pending"]
    return {"pending_requests": pending_leaves, "total_pending": len(pending_leaves)}

@app.patch("/api/v1/leaves/{leave_id}/approve")
async def approve_leave(leave_id: int, status: str, current_user: dict = Depends(get_current_user)):
    """Approve or reject leave request"""
    if current_user["user_type"] not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    leave = next((l for l in leaves_db if l["id"] == leave_id), None)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave["status"] = status
    leave["approved_by"] = current_user["id"]
    leave["approved_at"] = datetime.now().isoformat()

    return leave

@app.get("/api/v1/leaves/reports/summary")
async def get_leave_summary(current_user: dict = Depends(get_current_user)):
    """Get leave summary report"""
    total_requests = len(leaves_db)
    approved_requests = len([l for l in leaves_db if l.get("status") == "Approved"])
    pending_requests = len([l for l in leaves_db if l.get("status") == "Pending"])

    return {
        "summary": {
            "total_requests": total_requests,
            "approved_requests": approved_requests,
            "pending_requests": pending_requests,
            "approval_rate": (approved_requests / total_requests * 100) if total_requests > 0 else 0
        }
    }

# Expense Management Endpoints
@app.get("/api/v1/expenses/")
async def get_expenses(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get all expenses"""
    start = (page - 1) * per_page
    end = start + per_page

    return {
        "expenses": expenses_db[start:end],
        "total": len(expenses_db),
        "page": page,
        "per_page": per_page,
        "total_pages": (len(expenses_db) + per_page - 1) // per_page,
        "summary": {"total_expenses": len(expenses_db), "total_amount": sum(e.get("amount", 0) for e in expenses_db)}
    }

@app.post("/api/v1/expenses/")
async def create_expense(expense: ExpenseCreate, current_user: dict = Depends(get_current_user)):
    """Create a new expense"""
    new_expense = {
        "id": len(expenses_db) + 1,
        **expense.dict(),
        "status": "Pending",
        "requested_by": current_user["id"],
        "created_at": datetime.now().isoformat()
    }
    expenses_db.append(new_expense)
    return new_expense

@app.get("/api/v1/expenses/{expense_id}")
async def get_expense(expense_id: int, current_user: dict = Depends(get_current_user)):
    """Get expense by ID"""
    expense = next((e for e in expenses_db if e["id"] == expense_id), None)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@app.put("/api/v1/expenses/{expense_id}")
async def update_expense(expense_id: int, expense_update: dict, current_user: dict = Depends(get_current_user)):
    """Update expense"""
    expense = next((e for e in expenses_db if e["id"] == expense_id), None)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if expense["requested_by"] != current_user["id"] and current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    for key, value in expense_update.items():
        expense[key] = value
    expense["updated_at"] = datetime.now().isoformat()

    return expense

@app.delete("/api/v1/expenses/{expense_id}")
async def delete_expense(expense_id: int, current_user: dict = Depends(get_current_user)):
    """Delete expense"""
    expense = next((e for e in expenses_db if e["id"] == expense_id), None)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if expense["requested_by"] != current_user["id"] and current_user["user_type"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    expenses_db.remove(expense)
    return {"message": "Expense deleted successfully"}

@app.get("/api/v1/expenses/pending")
async def get_pending_expenses(current_user: dict = Depends(get_current_user)):
    """Get pending expenses"""
    pending_expenses = [e for e in expenses_db if e.get("status") == "Pending"]
    return {"pending_expenses": pending_expenses, "total_pending": len(pending_expenses)}

@app.patch("/api/v1/expenses/{expense_id}/approve")
async def approve_expense(expense_id: int, status: str, current_user: dict = Depends(get_current_user)):
    """Approve or reject expense"""
    if current_user["user_type"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    expense = next((e for e in expenses_db if e["id"] == expense_id), None)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    expense["status"] = status
    expense["approved_by"] = current_user["id"]
    expense["approved_at"] = datetime.now().isoformat()

    return expense

@app.get("/api/v1/expenses/categories")
async def get_expense_categories(current_user: dict = Depends(get_current_user)):
    """Get expense categories"""
    return {
        "categories": [
            "Office Supplies", "Maintenance", "Utilities", "Transport",
            "Food & Catering", "Equipment", "Marketing", "Staff Welfare",
            "Academic Materials", "Infrastructure", "Other"
        ]
    }

@app.get("/api/v1/expenses/dashboard")
async def get_expense_dashboard(current_user: dict = Depends(get_current_user)):
    """Get expense dashboard data"""
    total_expenses = sum(e.get("amount", 0) for e in expenses_db)
    pending_count = len([e for e in expenses_db if e.get("status") == "Pending"])

    return {
        "total_expenses": total_expenses,
        "pending_approvals": pending_count,
        "monthly_expenses": 0,
        "category_wise_expenses": [],
        "recent_expenses": expenses_db[-10:] if expenses_db else []
    }

if __name__ == "__main__":
    print("=" * 60)
    print("🏫 SUNRISE SCHOOL MANAGEMENT SYSTEM - COMPLETE VERSION")
    print("=" * 60)
    print("🚀 Starting complete backend server with full CRUD...")
    print("\n🌐 Server starting on http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("\n💡 Login Credentials:")
    print("   👨‍💼 Admin: admin@sunriseschool.edu / admin123")
    print("   👨‍🏫 Teacher: teacher@sunriseschool.edu / admin123")
    print("   👨‍🎓 Student: student@sunriseschool.edu / admin123")
    print("\n" + "=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
