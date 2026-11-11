"""HTTP routes of the transport operations module, mounted at /api/v1/transit."""
from fastapi import APIRouter

from app.modules.transport.router import assignments, setup

router = APIRouter()
router.include_router(setup.router)
router.include_router(assignments.router)
