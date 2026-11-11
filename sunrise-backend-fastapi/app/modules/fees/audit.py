"""Fee audit log: one row per change, with old and new values as JSON."""
from decimal import Decimal
from typing import Any, Iterable, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fees.models import FeeAuditLog

# Money is stored exactly ("1500.00"), never as a float
_ENCODERS = {Decimal: str}


def to_json(value: Any) -> Any:
    """JSON-ready copy of a value, with decimals as strings."""
    return jsonable_encoder(value, custom_encoder=_ENCODERS)


def snapshot(obj: Any, fields: Iterable[str]) -> dict:
    """Plain dict of some attributes of a model, for old_values/new_values."""
    return to_json({f: getattr(obj, f) for f in fields})


async def record(
    db: AsyncSession,
    *,
    entity_type: str,
    entity_id: int,
    action: str,
    performed_by: Optional[int],
    old: Optional[dict] = None,
    new: Optional[dict] = None,
    remarks: Optional[str] = None,
) -> None:
    db.add(FeeAuditLog(
        entity_type=entity_type, entity_id=entity_id, action=action,
        old_values=to_json(old) if old is not None else None,
        new_values=to_json(new) if new is not None else None,
        remarks=remarks, performed_by=performed_by,
    ))
