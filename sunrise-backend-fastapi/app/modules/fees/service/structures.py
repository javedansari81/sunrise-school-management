"""
Fee structures: a price list per session, DRAFT -> PUBLISHED -> ARCHIVED.

Only a draft can be edited or deleted. Publishing a draft archives the session's
currently published structure, so a session has at most one published price
list. To change a published list, copy it into a new draft, edit, publish.
"""
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fees import audit, repository as repo
from app.modules.fees.constants import AuditAction, StructureStatus
from app.modules.fees.errors import Conflict, Invalid
from app.modules.fees.models import FeeStructure, FeeStructureItem
from app.modules.fees.periods import validate_billing_months
from app.modules.fees.schemas import (
    FeeStructureCopy, FeeStructureCreate, FeeStructureItemIn, FeeStructureUpdate,
)

ENTITY = "fee_structure"
FIELDS = ("session_year_id", "name", "description", "status")
ITEM_FIELDS = ("fee_head_id", "class_id", "amount", "frequency", "billing_months", "due_day", "applies_to")


async def list_structures(
    db: AsyncSession, *, session_year_id: Optional[int] = None, status: Optional[str] = None
) -> List[FeeStructure]:
    query = select(FeeStructure).order_by(FeeStructure.session_year_id.desc(), FeeStructure.id.desc())
    if session_year_id is not None:
        query = query.where(FeeStructure.session_year_id == session_year_id)
    if status is not None:
        query = query.where(FeeStructure.status == status)
    return list((await db.execute(query)).scalars())


async def get_structure(db: AsyncSession, structure_id: int) -> FeeStructure:
    return await repo.get_or_404(db, FeeStructure, structure_id, "Fee structure")


def _require_draft(structure: FeeStructure) -> None:
    if structure.status != StructureStatus.DRAFT.value:
        raise Conflict(
            f"Fee structure {structure.id} is {structure.status}; only a draft can be changed. Copy it into a new draft."
        )


async def _validate_items(db: AsyncSession, items: List[FeeStructureItemIn]) -> None:
    heads = await repo.heads_by_id(db, (i.fee_head_id for i in items))
    classes = await repo.existing_class_ids(db, (i.class_id for i in items))
    seen = set()
    for n, item in enumerate(items, start=1):
        head = heads.get(item.fee_head_id)
        if head is None:
            raise Invalid(f"Item {n}: fee head {item.fee_head_id} not found")
        if item.class_id is not None and item.class_id not in classes:
            raise Invalid(f"Item {n}: class {item.class_id} not found")
        error = validate_billing_months(item.frequency.value, item.billing_months)
        if error:
            raise Invalid(f"Item {n}: {error}")
        key = (item.fee_head_id, item.class_id)
        if key in seen:
            raise Invalid(f"Item {n}: {head.code} is listed twice for the same class")
        seen.add(key)


def _new_item(item: FeeStructureItemIn) -> FeeStructureItem:
    return FeeStructureItem(**item.model_dump(mode="json"))


def _items_snapshot(structure: FeeStructure) -> list:
    return [audit.snapshot(i, ITEM_FIELDS) for i in structure.items]


async def create_structure(db: AsyncSession, data: FeeStructureCreate, *, user_id: int) -> FeeStructure:
    await repo.session_year_or_404(db, data.session_year_id)
    await _validate_items(db, data.items)
    structure = FeeStructure(
        session_year_id=data.session_year_id, name=data.name, description=data.description,
        status=StructureStatus.DRAFT.value, created_by=user_id,
        items=[_new_item(i) for i in data.items],
    )
    db.add(structure)
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=structure.id, action=AuditAction.CREATE.value,
                       performed_by=user_id, new={**audit.snapshot(structure, FIELDS), "items": _items_snapshot(structure)})
    return structure


async def update_structure(db: AsyncSession, structure_id: int, data: FeeStructureUpdate, *, user_id: int) -> FeeStructure:
    structure = await get_structure(db, structure_id)
    _require_draft(structure)
    old = audit.snapshot(structure, FIELDS)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(structure, key, value)
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=structure.id, action=AuditAction.UPDATE.value,
                       performed_by=user_id, old=old, new=audit.snapshot(structure, FIELDS))
    return structure


async def replace_items(
    db: AsyncSession, structure_id: int, items: List[FeeStructureItemIn], *, user_id: int
) -> FeeStructure:
    structure = await get_structure(db, structure_id)
    _require_draft(structure)
    await _validate_items(db, items)
    old = _items_snapshot(structure)
    structure.items.clear()
    await db.flush()  # delete the old lines before inserting new ones (unique key per head and class)
    structure.items.extend(_new_item(i) for i in items)
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=structure.id, action=AuditAction.UPDATE.value,
                       performed_by=user_id, old={"items": old}, new={"items": _items_snapshot(structure)})
    return structure


async def delete_structure(db: AsyncSession, structure_id: int, *, user_id: int) -> None:
    structure = await get_structure(db, structure_id)
    _require_draft(structure)
    old = {**audit.snapshot(structure, FIELDS), "items": _items_snapshot(structure)}
    await db.delete(structure)
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=structure_id, action=AuditAction.DELETE.value,
                       performed_by=user_id, old=old)


async def publish_structure(db: AsyncSession, structure_id: int, *, user_id: int) -> FeeStructure:
    structure = await get_structure(db, structure_id)
    _require_draft(structure)
    if not structure.items:
        raise Invalid("A fee structure needs at least one item before it can be published")
    inactive = [h.code for h in (await repo.heads_by_id(db, (i.fee_head_id for i in structure.items))).values()
                if not h.is_active]
    if inactive:
        raise Invalid(f"Inactive fee heads cannot be published: {', '.join(sorted(inactive))}")

    current = await repo.published_structure(db, structure.session_year_id)
    if current is not None:
        current.status = StructureStatus.ARCHIVED.value
        await db.flush()  # free the one-published-per-session slot first
        await audit.record(db, entity_type=ENTITY, entity_id=current.id, action=AuditAction.ARCHIVE.value,
                           performed_by=user_id, remarks=f"Replaced by fee structure {structure.id}")

    structure.status = StructureStatus.PUBLISHED.value
    structure.published_at = datetime.now(timezone.utc)
    structure.published_by = user_id
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=structure.id, action=AuditAction.PUBLISH.value,
                       performed_by=user_id, remarks=f"Replaced fee structure {current.id}" if current else None)
    return structure


async def archive_structure(db: AsyncSession, structure_id: int, *, user_id: int) -> FeeStructure:
    structure = await get_structure(db, structure_id)
    if structure.status != StructureStatus.PUBLISHED.value:
        raise Conflict(f"Only a published fee structure can be archived; {structure.id} is {structure.status}")
    structure.status = StructureStatus.ARCHIVED.value
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=structure.id, action=AuditAction.ARCHIVE.value,
                       performed_by=user_id)
    return structure


async def copy_structure(db: AsyncSession, structure_id: int, data: FeeStructureCopy, *, user_id: int) -> FeeStructure:
    source = await get_structure(db, structure_id)
    session_year_id = data.session_year_id or source.session_year_id
    await repo.session_year_or_404(db, session_year_id)
    copy = FeeStructure(
        session_year_id=session_year_id,
        name=data.name or f"{source.name} (copy)",
        description=source.description,
        status=StructureStatus.DRAFT.value,
        copied_from_id=source.id,
        created_by=user_id,
        items=[FeeStructureItem(**{f: getattr(i, f) for f in ITEM_FIELDS}) for i in source.items],
    )
    db.add(copy)
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=copy.id, action=AuditAction.CREATE.value,
                       performed_by=user_id, remarks=f"Copied from fee structure {source.id}")
    return copy
