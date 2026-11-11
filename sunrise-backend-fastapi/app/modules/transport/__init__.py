"""
Transport operations module (Phase 3 of docs/MULTI_TENANT_FEE_REDESIGN_PLAN.md).

Decides who rides, on what, from where and at what monthly rate. It never
stores dues or payments: each assignment owns TRANSPORT lines in the fee
module's student_fee_plans, and the fee module bills them.

Layers:
    models        SQLAlchemy models (all tenant-scoped through TenantMixin)
    schemas       Pydantic request and response models
    repository    queries
    billing       assignment -> billed months -> fee plan lines (the handoff)
    service       business rules (setup, rates, assignments, rosters)
    router        HTTP routes, mounted at /api/v1/transit
"""
