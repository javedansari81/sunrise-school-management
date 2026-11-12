from fastapi import APIRouter, Depends

from app.api.deps import require_shop_enabled

from app.modules.fees.router import router as billing_router
from app.modules.transport.router import router as transit_router

from app.api.v1.endpoints import (
    auth, teachers, students, leaves, expenses, configuration,
    public, database, dashboard, gallery, reports, inventory,
    student_siblings, users, attendance, alerts, session_progression, platform,
    school_settings
)

api_router = APIRouter()

# Public endpoints (no authentication required)
api_router.include_router(public.router, prefix="/public", tags=["public"])

# Database management endpoints (platform admin only)
api_router.include_router(database.router, prefix="/database", tags=["database"])

# Platform admin: school management (platform admin token only)
api_router.include_router(platform.router, prefix="/platform", tags=["platform"])

# Authenticated endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
# School admin: the school's profile, settings and its own lists
api_router.include_router(school_settings.router, prefix="/school-settings", tags=["school-settings"])
api_router.include_router(configuration.router, prefix="/configuration", tags=["configuration"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(student_siblings.router, prefix="/students", tags=["student-siblings"])
api_router.include_router(leaves.router, prefix="/leaves", tags=["leaves"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
# Unified fee module: every charge, payment, receipt and fee report
api_router.include_router(billing_router, prefix="/billing", tags=["billing"])
# School Shop: only for schools that turned it on (setting module.shop.enabled)
api_router.include_router(
    inventory.router, prefix="/inventory", tags=["inventory"], dependencies=[Depends(require_shop_enabled)]
)
# Transport operations module: types, vehicles, routes, rates and assignments
api_router.include_router(transit_router, prefix="/transit", tags=["transit"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(gallery.router, prefix="/gallery", tags=["gallery"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(session_progression.router, prefix="/session-progression", tags=["session-progression"])
