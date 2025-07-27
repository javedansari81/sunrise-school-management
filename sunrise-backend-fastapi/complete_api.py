#!/usr/bin/env python3
"""
Complete API server with all endpoints organized by tags
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import asyncpg
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a436afdbaade6c5ae255289d8aa80103adbd4f622b4a99077bb40ac9140b8368a")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8  # 8 days

app = FastAPI(
    title="Sunrise School Management API",
    description="Complete API with authentication and CRUD operations for all entities",
    version="1.0.0"
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/sunrise_db")

# Pydantic Models
class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    user_type: str
    is_active: bool

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    mobile: str
    email: str
    password: str
    user_type: str = "user"

class StudentCreate(BaseModel):
    admission_number: str
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    current_class: str
    section: Optional[str] = None
    father_name: str
    mother_name: str
    admission_date: str

class TeacherCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    subject: str
    qualification: str
    experience_years: int
    salary: float

class LeaveCreate(BaseModel):
    student_id: int
    leave_type: str
    start_date: str
    end_date: str
    total_days: int
    reason: str
    description: Optional[str] = None
    emergency_contact: Optional[str] = None

class ExpenseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    amount: float
    tax_amount: float = 0.0
    total_amount: float
    vendor_name: Optional[str] = None
    expense_date: str

class FeeCreate(BaseModel):
    student_id: int
    session_year: str
    payment_type: str
    total_amount: float
    due_date: str

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: str
    location: Optional[str] = None
    event_type: str

# Authentication functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    conn = await get_db_connection()
    try:
        user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
        if user is None:
            raise credentials_exception
        return dict(user)
    finally:
        await conn.close()

async def get_db_connection():
    """Get database connection"""
    try:
        # Parse DATABASE_URL
        parts = DATABASE_URL.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        host_port = host_db[0].split(":")
        
        user = user_pass[0]
        password = user_pass[1]
        host = host_port[0]
        port = int(host_port[1])
        database = host_db[1]
        
        conn = await asyncpg.connect(
            host=host, port=port, user=user, password=password, database=database
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

def serialize_record(record):
    """Convert asyncpg record to JSON-serializable dict"""
    result = {}
    for key, value in record.items():
        if isinstance(value, (datetime, date)):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Sunrise School Management API", "status": "running"}

# Authentication Endpoints
@app.post("/api/v1/auth/login", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint (OAuth2 form data)"""
    conn = await get_db_connection()
    try:
        # Get user by email
        user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", form_data.username)
        if not user or not verify_password(form_data.password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user['email']}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        await conn.close()

@app.post("/api/v1/auth/login-json", response_model=Token, tags=["Authentication"])
async def login_json(login_data: LoginRequest):
    """Login endpoint (JSON data)"""
    conn = await get_db_connection()
    try:
        # Get user by email
        user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", login_data.email)
        if not user or not verify_password(login_data.password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user['email']}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        await conn.close()

@app.get("/api/v1/auth/me", response_model=User, tags=["Authentication"])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user["id"],
        "first_name": current_user["first_name"],
        "last_name": current_user["last_name"],
        "email": current_user["email"],
        "user_type": current_user["user_type"],
        "is_active": current_user["is_active"]
    }

# Students Endpoints
@app.get("/api/v1/students/", tags=["Students"])
async def get_students():
    """Get all students"""
    conn = await get_db_connection()
    try:
        query = """
            SELECT id, admission_number, first_name, last_name, date_of_birth,
                   gender, current_class, section, roll_number, email, phone,
                   father_name, mother_name, admission_date, is_active
            FROM students
            WHERE is_active = true
            ORDER BY current_class, section, roll_number
        """
        records = await conn.fetch(query)
        students = [serialize_record(record) for record in records]
        return {"students": students, "total": len(students)}
    finally:
        await conn.close()

@app.post("/api/v1/students/", tags=["Students"])
async def create_student(student: StudentCreate, current_user: dict = Depends(get_current_user)):
    """Create a new student"""
    conn = await get_db_connection()
    try:
        # Convert string dates to date objects
        date_of_birth = datetime.strptime(student.date_of_birth, "%Y-%m-%d").date()
        admission_date = datetime.strptime(student.admission_date, "%Y-%m-%d").date()

        query = """
            INSERT INTO students (admission_number, first_name, last_name, date_of_birth,
                                gender, current_class, section, father_name, mother_name, admission_date)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING id, admission_number, first_name, last_name
        """
        result = await conn.fetchrow(
            query, student.admission_number, student.first_name, student.last_name,
            date_of_birth, student.gender, student.current_class, student.section,
            student.father_name, student.mother_name, admission_date
        )
        return {"message": "Student created successfully", "student": serialize_record(result)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create student: {str(e)}")
    finally:
        await conn.close()

@app.put("/api/v1/students/{student_id}", tags=["Students"])
async def update_student(student_id: int, student: StudentCreate, current_user: dict = Depends(get_current_user)):
    """Update a student"""
    conn = await get_db_connection()
    try:
        query = """
            UPDATE students
            SET first_name = $2, last_name = $3, current_class = $4, section = $5,
                father_name = $6, mother_name = $7
            WHERE id = $1
            RETURNING id, admission_number, first_name, last_name
        """
        result = await conn.fetchrow(
            query, student_id, student.first_name, student.last_name,
            student.current_class, student.section, student.father_name, student.mother_name
        )
        if not result:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"message": "Student updated successfully", "student": serialize_record(result)}
    finally:
        await conn.close()

@app.delete("/api/v1/students/{student_id}", tags=["Students"])
async def delete_student(student_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a student (soft delete)"""
    conn = await get_db_connection()
    try:
        query = "UPDATE students SET is_active = false WHERE id = $1 RETURNING id, first_name, last_name"
        result = await conn.fetchrow(query, student_id)
        if not result:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"message": "Student deleted successfully", "student": serialize_record(result)}
    finally:
        await conn.close()

# Leave Requests Endpoints
@app.get("/api/v1/leaves/", tags=["Leave Management"])
async def get_leaves():
    """Get all leave requests"""
    conn = await get_db_connection()
    try:
        query = """
            SELECT lr.id, lr.student_id, lr.leave_type, lr.start_date, lr.end_date,
                   lr.total_days, lr.reason, lr.description, lr.status, lr.emergency_contact,
                   lr.created_at, s.first_name, s.last_name, s.admission_number, s.current_class
            FROM leave_requests lr
            JOIN students s ON lr.student_id = s.id
            ORDER BY lr.created_at DESC
        """
        records = await conn.fetch(query)
        leaves = [serialize_record(record) for record in records]
        return {"leave_requests": leaves, "total": len(leaves)}
    finally:
        await conn.close()

@app.post("/api/v1/leaves/", tags=["Leave Management"])
async def create_leave(leave: LeaveCreate, current_user: dict = Depends(get_current_user)):
    """Create a new leave request"""
    conn = await get_db_connection()
    try:
        # Convert string dates to date objects
        start_date = datetime.strptime(leave.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(leave.end_date, "%Y-%m-%d").date()

        query = """
            INSERT INTO leave_requests (student_id, leave_type, start_date, end_date,
                                      total_days, reason, description, emergency_contact)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, student_id, leave_type, reason, status
        """
        result = await conn.fetchrow(
            query, leave.student_id, leave.leave_type, start_date, end_date,
            leave.total_days, leave.reason, leave.description, leave.emergency_contact
        )
        return {"message": "Leave request created successfully", "leave": serialize_record(result)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create leave request: {str(e)}")
    finally:
        await conn.close()

@app.patch("/api/v1/leaves/{leave_id}/approve", tags=["Leave Management"])
async def approve_leave(leave_id: int, current_user: dict = Depends(get_current_user)):
    """Approve a leave request"""
    conn = await get_db_connection()
    try:
        query = """
            UPDATE leave_requests
            SET status = 'Approved', approved_by = $2, approved_at = NOW()
            WHERE id = $1
            RETURNING id, student_id, leave_type, status
        """
        result = await conn.fetchrow(query, leave_id, current_user["id"])
        if not result:
            raise HTTPException(status_code=404, detail="Leave request not found")
        return {"message": "Leave request approved", "leave": serialize_record(result)}
    finally:
        await conn.close()

@app.patch("/api/v1/leaves/{leave_id}/reject", tags=["Leave Management"])
async def reject_leave(leave_id: int, current_user: dict = Depends(get_current_user)):
    """Reject a leave request"""
    conn = await get_db_connection()
    try:
        query = """
            UPDATE leave_requests
            SET status = 'Rejected', approved_by = $2, approved_at = NOW()
            WHERE id = $1
            RETURNING id, student_id, leave_type, status
        """
        result = await conn.fetchrow(query, leave_id, current_user["id"])
        if not result:
            raise HTTPException(status_code=404, detail="Leave request not found")
        return {"message": "Leave request rejected", "leave": serialize_record(result)}
    finally:
        await conn.close()

# Expenses Endpoints
@app.get("/api/v1/expenses/", tags=["Expense Management"])
async def get_expenses():
    """Get all expenses"""
    conn = await get_db_connection()
    try:
        query = """
            SELECT e.id, e.title, e.description, e.category, e.amount, e.tax_amount,
                   e.total_amount, e.vendor_name, e.payment_mode, e.expense_date,
                   e.status, e.invoice_number, e.created_at,
                   u.first_name as requester_first_name, u.last_name as requester_last_name
            FROM expenses e
            JOIN users u ON e.requested_by = u.id
            ORDER BY e.expense_date DESC
        """
        records = await conn.fetch(query)
        expenses = [serialize_record(record) for record in records]
        return {"expenses": expenses, "total": len(expenses)}
    finally:
        await conn.close()

@app.post("/api/v1/expenses/", tags=["Expense Management"])
async def create_expense(expense: ExpenseCreate, current_user: dict = Depends(get_current_user)):
    """Create a new expense"""
    conn = await get_db_connection()
    try:
        # Convert string date to date object
        expense_date = datetime.strptime(expense.expense_date, "%Y-%m-%d").date()

        query = """
            INSERT INTO expenses (title, description, category, amount, tax_amount,
                                total_amount, vendor_name, expense_date, requested_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id, title, category, total_amount, status
        """
        result = await conn.fetchrow(
            query, expense.title, expense.description, expense.category, expense.amount,
            expense.tax_amount, expense.total_amount, expense.vendor_name,
            expense_date, current_user["id"]
        )
        return {"message": "Expense created successfully", "expense": serialize_record(result)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create expense: {str(e)}")
    finally:
        await conn.close()

@app.patch("/api/v1/expenses/{expense_id}/approve", tags=["Expense Management"])
async def approve_expense(expense_id: int, current_user: dict = Depends(get_current_user)):
    """Approve an expense"""
    conn = await get_db_connection()
    try:
        query = """
            UPDATE expenses
            SET status = 'Approved', approved_by = $2, approved_at = NOW()
            WHERE id = $1
            RETURNING id, title, category, status
        """
        result = await conn.fetchrow(query, expense_id, current_user["id"])
        if not result:
            raise HTTPException(status_code=404, detail="Expense not found")
        return {"message": "Expense approved", "expense": serialize_record(result)}
    finally:
        await conn.close()

@app.patch("/api/v1/expenses/{expense_id}/reject", tags=["Expense Management"])
async def reject_expense(expense_id: int, current_user: dict = Depends(get_current_user)):
    """Reject an expense"""
    conn = await get_db_connection()
    try:
        query = """
            UPDATE expenses
            SET status = 'Rejected', approved_by = $2, approved_at = NOW()
            WHERE id = $1
            RETURNING id, title, category, status
        """
        result = await conn.fetchrow(query, expense_id, current_user["id"])
        if not result:
            raise HTTPException(status_code=404, detail="Expense not found")
        return {"message": "Expense rejected", "expense": serialize_record(result)}
    finally:
        await conn.close()

# Fees Endpoints
@app.get("/api/v1/fees/", tags=["Fee Management"])
async def get_fees():
    """Get all fee records"""
    conn = await get_db_connection()
    try:
        query = """
            SELECT fr.id, fr.student_id, fr.session_year, fr.payment_type,
                   fr.total_amount, fr.paid_amount, fr.balance_amount, fr.status,
                   fr.due_date, fr.payment_method, fr.payment_date,
                   s.first_name, s.last_name, s.admission_number, s.current_class
            FROM fee_records fr
            JOIN students s ON fr.student_id = s.id
            ORDER BY fr.due_date DESC
        """
        records = await conn.fetch(query)
        fees = [serialize_record(record) for record in records]
        return {"fee_records": fees, "total": len(fees)}
    finally:
        await conn.close()

@app.post("/api/v1/fees/", tags=["Fee Management"])
async def create_fee_record(fee: FeeCreate, current_user: dict = Depends(get_current_user)):
    """Create a new fee record"""
    conn = await get_db_connection()
    try:
        # Convert string date to date object
        due_date = datetime.strptime(fee.due_date, "%Y-%m-%d").date()

        query = """
            INSERT INTO fee_records (student_id, session_year, payment_type, total_amount,
                                   balance_amount, due_date)
            VALUES ($1, $2, $3, $4, $4, $5)
            RETURNING id, student_id, total_amount, status
        """
        result = await conn.fetchrow(
            query, fee.student_id, fee.session_year, fee.payment_type,
            fee.total_amount, due_date
        )
        return {"message": "Fee record created successfully", "fee": serialize_record(result)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create fee record: {str(e)}")
    finally:
        await conn.close()

# Dashboard Endpoints
@app.get("/api/v1/dashboard/stats", tags=["Dashboard"])
async def get_dashboard_stats():
    """Get dashboard statistics"""
    conn = await get_db_connection()
    try:
        # Get counts
        students_count = await conn.fetchval("SELECT COUNT(*) FROM students WHERE is_active = true")
        leaves_pending = await conn.fetchval("SELECT COUNT(*) FROM leave_requests WHERE status = 'Pending'")
        expenses_pending = await conn.fetchval("SELECT COUNT(*) FROM expenses WHERE status = 'Pending'")
        fees_overdue = await conn.fetchval("SELECT COUNT(*) FROM fee_records WHERE status = 'Overdue'")

        return {
            "stats": {
                "total_students": students_count,
                "pending_leaves": leaves_pending,
                "pending_expenses": expenses_pending,
                "overdue_fees": fees_overdue
            }
        }
    finally:
        await conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
