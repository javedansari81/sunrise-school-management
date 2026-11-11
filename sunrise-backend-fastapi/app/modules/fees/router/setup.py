"""Routes: fee heads and fee structures (price lists)."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.modules.fees.constants import StructureStatus
from app.modules.fees.deps import can_configure, can_view
from app.modules.fees.schemas import (
    FeeHeadCreate, FeeHeadOut, FeeHeadUpdate, FeeStructureCopy, FeeStructureCreate,
    FeeStructureItemIn, FeeStructureOut, FeeStructureSummary, FeeStructureUpdate,
)
from app.modules.fees.service import heads as head_service
from app.modules.fees.service import structures as structure_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Fee heads
# ---------------------------------------------------------------------------

@router.get("/fee-heads", response_model=List[FeeHeadOut])
async def list_fee_heads(
    include_inactive: bool = False,
    user: User = Depends(can_view),
    db: AsyncSession = Depends(get_db),
):
    return await head_service.list_heads(db, include_inactive=include_inactive)


@router.post("/fee-heads", response_model=FeeHeadOut, status_code=status.HTTP_201_CREATED)
async def create_fee_head(body: FeeHeadCreate, user: User = Depends(can_configure), db: AsyncSession = Depends(get_db)):
    head = await head_service.create_head(db, body, user_id=user.id)
    await db.commit()
    return head


@router.patch("/fee-heads/{head_id}", response_model=FeeHeadOut)
async def update_fee_head(
    head_id: int, body: FeeHeadUpdate, user: User = Depends(can_configure), db: AsyncSession = Depends(get_db)
):
    head = await head_service.update_head(db, head_id, body, user_id=user.id)
    await db.commit()
    return head


@router.delete("/fee-heads/{head_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fee_head(head_id: int, user: User = Depends(can_configure), db: AsyncSession = Depends(get_db)):
    await head_service.delete_head(db, head_id, user_id=user.id)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Fee structures
# ---------------------------------------------------------------------------

@router.get("/fee-structures", response_model=List[FeeStructureSummary])
async def list_fee_structures(
    session_year_id: Optional[int] = None,
    status_filter: Optional[StructureStatus] = Query(default=None, alias="status"),
    user: User = Depends(can_view),
    db: AsyncSession = Depends(get_db),
):
    return await structure_service.list_structures(
        db, session_year_id=session_year_id, status=status_filter.value if status_filter else None
    )


@router.post("/fee-structures", response_model=FeeStructureOut, status_code=status.HTTP_201_CREATED)
async def create_fee_structure(
    body: FeeStructureCreate, user: User = Depends(can_configure), db: AsyncSession = Depends(get_db)
):
    structure = await structure_service.create_structure(db, body, user_id=user.id)
    await db.commit()
    return structure


@router.get("/fee-structures/{structure_id}", response_model=FeeStructureOut)
async def get_fee_structure(structure_id: int, user: User = Depends(can_view), db: AsyncSession = Depends(get_db)):
    return await structure_service.get_structure(db, structure_id)


@router.patch("/fee-structures/{structure_id}", response_model=FeeStructureOut)
async def update_fee_structure(
    structure_id: int, body: FeeStructureUpdate, user: User = Depends(can_configure), db: AsyncSession = Depends(get_db)
):
    structure = await structure_service.update_structure(db, structure_id, body, user_id=user.id)
    await db.commit()
    return structure


@router.put("/fee-structures/{structure_id}/items", response_model=FeeStructureOut)
async def replace_fee_structure_items(
    structure_id: int,
    body: List[FeeStructureItemIn],
    user: User = Depends(can_configure),
    db: AsyncSession = Depends(get_db),
):
    """Replace every price line of a draft structure (the UI edits the whole grid)."""
    structure = await structure_service.replace_items(db, structure_id, body, user_id=user.id)
    await db.commit()
    return structure


@router.delete("/fee-structures/{structure_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fee_structure(structure_id: int, user: User = Depends(can_configure), db: AsyncSession = Depends(get_db)):
    await structure_service.delete_structure(db, structure_id, user_id=user.id)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/fee-structures/{structure_id}/publish", response_model=FeeStructureOut)
async def publish_fee_structure(structure_id: int, user: User = Depends(can_configure), db: AsyncSession = Depends(get_db)):
    """Publish a draft. The session's previously published structure is archived."""
    structure = await structure_service.publish_structure(db, structure_id, user_id=user.id)
    await db.commit()
    return structure


@router.post("/fee-structures/{structure_id}/archive", response_model=FeeStructureOut)
async def archive_fee_structure(structure_id: int, user: User = Depends(can_configure), db: AsyncSession = Depends(get_db)):
    structure = await structure_service.archive_structure(db, structure_id, user_id=user.id)
    await db.commit()
    return structure


@router.post("/fee-structures/{structure_id}/copy", response_model=FeeStructureOut, status_code=status.HTTP_201_CREATED)
async def copy_fee_structure(
    structure_id: int, body: FeeStructureCopy, user: User = Depends(can_configure), db: AsyncSession = Depends(get_db)
):
    """Copy a structure (any status) into a new draft, optionally for another session."""
    structure = await structure_service.copy_structure(db, structure_id, body, user_id=user.id)
    await db.commit()
    return structure
