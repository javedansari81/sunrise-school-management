"""
Transport defaults for a newly created school.

Existing schools got theirs from Database/Init/05_transport_defaults.sql (fresh
deployments) or migration V003. A school created later through the platform
API copies the template school's transport types, or gets E-Rickshaw, Van and
Bus without a template. Routes, vehicles and rates are the school's own and
are not copied. The transport settings (fee.transport.*) are copied with the
fee settings by app.modules.fees.provisioning.

Runs on a platform session (tenant scoping off), so school_id is set explicitly.
"""
from typing import Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.transport.constants import DEFAULT_TYPES
from app.modules.transport.models import TransportType


async def seed_transport_defaults(
    db: AsyncSession, *, school_id: int, template_school_id: Optional[int]
) -> Dict[str, int]:
    template = []
    if template_school_id is not None:
        template = (await db.execute(
            select(TransportType).where(TransportType.school_id == template_school_id).order_by(TransportType.id)
        )).scalars().all()
    if template:
        rows = [TransportType(school_id=school_id, name=t.name, description=t.description, capacity=t.capacity,
                              sort_order=t.sort_order, is_active=t.is_active) for t in template]
    else:
        rows = [TransportType(school_id=school_id, name=name, description=description, capacity=capacity,
                              sort_order=order) for name, description, capacity, order in DEFAULT_TYPES]
    db.add_all(rows)
    await db.flush()
    return {"transport_types": len(rows)}
