"""
Unified fee module (Phase 2 of docs/MULTI_TENANT_FEE_REDESIGN_PLAN.md).

Every charge (tuition, transport, admission, exam, late fee, one-offs) is a due
tagged with a fee head. Payments settle any mix of dues and produce one receipt
from one per-school, per-session series.

Layers:
    models      SQLAlchemy models (all tenant-scoped through TenantMixin)
    schemas     Pydantic request and response models
    repository  queries
    service     business rules
    router      HTTP routes, mounted at /api/v1/billing
"""
