"""HTTP routes of the unified fee module, mounted at /api/v1/billing."""
from fastapi import APIRouter

from app.modules.fees.router import billing, payments, reports, self_service, setup

router = APIRouter()
router.include_router(setup.router)
router.include_router(billing.router)
router.include_router(payments.router)
router.include_router(reports.router)
router.include_router(self_service.router)
