from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, users, teachers, menus, submenus,
    products, classes, events, testimonials,
    students, leaves, expenses, fees
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(leaves.router, prefix="/leaves", tags=["leaves"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(fees.router, prefix="/fees", tags=["fees"])
api_router.include_router(menus.router, prefix="/menus", tags=["menus"])
api_router.include_router(submenus.router, prefix="/submenus", tags=["submenus"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(classes.router, prefix="/classes", tags=["classes"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(testimonials.router, prefix="/testimonials", tags=["testimonials"])
