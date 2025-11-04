from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, teachers, students, leaves, expenses, fees, configuration,
    public, database, transport, dashboard, gallery, reports, inventory
)
# users endpoints removed - not used in frontend
# user management handled through student/teacher endpoints

api_router = APIRouter()

# Public endpoints (no authentication required)
api_router.include_router(public.router, prefix="/public", tags=["public"])

# Database management endpoints (admin only - no auth for initial deployment)
api_router.include_router(database.router, prefix="/database", tags=["database"])

# Authenticated endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(configuration.router, prefix="/configuration", tags=["configuration"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
# users.router removed - endpoints not used in frontend
api_router.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(leaves.router, prefix="/leaves", tags=["leaves"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(fees.router, prefix="/fees", tags=["fees"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(transport.router, prefix="/transport", tags=["transport"])
api_router.include_router(gallery.router, prefix="/gallery", tags=["gallery"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
