from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, users, teachers, students, leaves, expenses, fees, configuration
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(configuration.router, prefix="/configuration", tags=["configuration"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(leaves.router, prefix="/leaves", tags=["leaves"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(fees.router, prefix="/fees", tags=["fees"])
