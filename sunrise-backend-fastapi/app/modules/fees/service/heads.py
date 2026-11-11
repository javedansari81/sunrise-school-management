"""Fee heads: the school's list of fee types."""
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fees import audit, repository as repo
from app.modules.fees.constants import AuditAction
from app.modules.fees.errors import Conflict, Invalid
from app.modules.fees.models import FeeHead
from app.modules.fees.schemas import FeeHeadCreate, FeeHeadUpdate

ENTITY = "fee_head"
FIELDS = ("code", "name", "description", "category", "default_frequency", "sort_order", "is_active")


async def list_heads(db: AsyncSession, *, include_inactive: bool = False) -> List[FeeHead]:
    query = select(FeeHead).order_by(FeeHead.sort_order, FeeHead.name)
    if not include_inactive:
        query = query.where(FeeHead.is_active)
    return list((await db.execute(query)).scalars())


async def _ensure_unique(db: AsyncSession, *, code=None, name=None, exclude_id=None) -> None:
    for column, value, label in ((FeeHead.code, code, "code"), (FeeHead.name, name, "name")):
        if value is None:
            continue
        query = select(FeeHead.id).where(column == value)
        if exclude_id is not None:
            query = query.where(FeeHead.id != exclude_id)
        if (await db.execute(query)).first():
            raise Conflict(f"A fee head with {label} '{value}' already exists")


async def create_head(db: AsyncSession, data: FeeHeadCreate, *, user_id: int) -> FeeHead:
    await _ensure_unique(db, code=data.code, name=data.name)
    head = FeeHead(**data.model_dump(mode="json"), is_system=False)
    db.add(head)
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=head.id, action=AuditAction.CREATE.value,
                       performed_by=user_id, new=audit.snapshot(head, FIELDS))
    return head


async def update_head(db: AsyncSession, head_id: int, data: FeeHeadUpdate, *, user_id: int) -> FeeHead:
    head = await repo.get_or_404(db, FeeHead, head_id, "Fee head")
    changes = data.model_dump(mode="json", exclude_unset=True)
    if head.is_system:
        for locked in ("code", "category"):
            if locked in changes and changes[locked] != getattr(head, locked):
                raise Invalid(f"The {locked} of system fee head {head.code} cannot be changed")
        if changes.get("is_active") is False:
            raise Invalid(f"System fee head {head.code} cannot be deactivated")
    await _ensure_unique(db, code=changes.get("code"), name=changes.get("name"), exclude_id=head.id)
    old = audit.snapshot(head, FIELDS)
    for key, value in changes.items():
        setattr(head, key, value)
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=head.id, action=AuditAction.UPDATE.value,
                       performed_by=user_id, old=old, new=audit.snapshot(head, FIELDS))
    return head


async def delete_head(db: AsyncSession, head_id: int, *, user_id: int) -> None:
    head = await repo.get_or_404(db, FeeHead, head_id, "Fee head")
    if head.is_system:
        raise Invalid(f"System fee head {head.code} cannot be deleted")
    if await repo.head_in_use(db, head.id):
        raise Conflict(f"Fee head {head.code} is used by fee structures, plans or dues; deactivate it instead")
    old = audit.snapshot(head, FIELDS)
    await db.delete(head)
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=head_id, action=AuditAction.DELETE.value,
                       performed_by=user_id, old=old)
