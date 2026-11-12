"""
Settings screen for a school's admins (/api/v1/school-settings).

Everything here belongs to the calling school only: the session is bound to
the admin's school, so every read and write is scoped by app/core/tenant.py.

    GET    /profile                     the school's name, logo and contact details
    PATCH  /profile                     change them (code, status, currency and
                                        timezone stay with the platform admin)
    GET    /values                      every setting in SETTINGS_CATALOG with its
                                        stored value and default
    PUT    /values/{key}                store a value ({"value": null} resets it)
    GET    /lists                       the lists a school keeps for itself
    GET    /lists/{kind}                one list, including rows not in use
    POST   /lists/{kind}                add a row
    PATCH  /lists/{kind}/{id}           change a row (rows are never deleted,
                                        because students, staff and fees point at
                                        them: mark a row not in use instead)

Lists and settings feed /configuration and /public/school, so every change
clears this school's configuration cache.
"""
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin_user
from app.core.database import get_db
from app.core.tenant import get_session_school
from app.models.gallery import GalleryCategory
from app.models.inventory import InventoryItemCategory, InventoryItemType, InventorySizeType
from app.models.metadata import Class, Department, ExpenseCategory, LeaveType, Position, SessionYear
from app.models.school import School, SchoolSetting
from app.models.user import User
from app.services import school_settings as svc

router = APIRouter()


# ---------------------------------------------------------------- profile

PROFILE_FIELDS = ("name", "short_name", "address", "phone", "email", "website", "logo_url")


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    short_name: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=1000)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=1000)


def _profile(school: School) -> Dict[str, Any]:
    return {
        "code": school.code,
        **{field: getattr(school, field) for field in PROFILE_FIELDS},
        "currency": school.currency,
        "timezone": school.timezone,
        "academic_year_start_month": school.academic_year_start_month,
    }


async def _school(db: AsyncSession) -> School:
    return await db.get(School, get_session_school(db))


def _clear_cache(db: AsyncSession) -> None:
    from app.api.v1.endpoints.configuration import clear_school_configuration_cache

    clear_school_configuration_cache(get_session_school(db))


@router.get("/profile")
async def get_profile(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_admin_user)):
    return _profile(await _school(db))


@router.patch("/profile")
async def update_profile(
    body: ProfileUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_admin_user)
):
    school = await _school(db)
    for field, value in body.model_dump(exclude_unset=True).items():
        if isinstance(value, str):
            value = value.strip() or None
        if field == "name" and not value:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "The school needs a name")
        setattr(school, field, value)
    await db.commit()
    await db.refresh(school)
    return _profile(school)


# ---------------------------------------------------------------- settings

async def _values(db: AsyncSession) -> List[Dict[str, Any]]:
    stored = {row.key: row.value for row in (await db.execute(select(SchoolSetting))).scalars()}
    return [{**spec.as_dict(), "value": stored.get(spec.key)} for spec in svc.SETTINGS_CATALOG]


@router.get("/values")
async def list_values(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_admin_user)):
    return await _values(db)


@router.put("/values/{key}")
async def set_value(
    key: str,
    value: Optional[Any] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    spec = svc.SETTINGS_BY_KEY.get(key)
    if spec is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown setting: {key}")
    if isinstance(value, bool):
        value = "true" if value else "false"
    try:
        clean = svc.validate_value(spec, None if value is None else str(value))
    except ValueError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error))

    row = (await db.execute(select(SchoolSetting).where(SchoolSetting.key == key))).scalar_one_or_none()
    if clean is None:
        if row is not None:
            await db.delete(row)
    elif row is None:
        db.add(SchoolSetting(key=key, value=clean, description=spec.help))
    else:
        row.value = clean
    await db.commit()
    _clear_cache(db)
    return next(item for item in await _values(db) if item["key"] == key)


# ---------------------------------------------------------------- lists

def _field(name, label, type_="text", required=False, max_length=None, help="", ref=None):
    return {"name": name, "label": label, "type": type_, "required": required,
            "max_length": max_length, "help": help, "ref": ref}


NAME = _field("name", "Name", required=True, max_length=50)
DESCRIPTION = _field("description", "Description", max_length=500)

# kind -> model, labels and the fields the screen edits (is_active is always there)
LISTS: Dict[str, Dict[str, Any]] = {
    "classes": {
        "model": Class, "label": "Classes", "group": "Academic", "order": "sort_order",
        "hint": "Classes students are admitted to. The order is used everywhere classes are listed.",
        "fields": [
            _field("name", "Code", required=True, max_length=50, help="Short code, e.g. CLASS_1"),
            _field("description", "Display name", required=True, max_length=100, help="e.g. Class 1"),
            _field("sort_order", "Order", "int"),
        ],
    },
    "session_years": {
        "model": SessionYear, "label": "Session years", "group": "Academic", "order": "start_date",
        "hint": "Academic years. Exactly one is current; it is the default on every screen.",
        "fields": [
            _field("name", "Session", required=True, max_length=20, help="e.g. 2027-28"),
            _field("description", "Display name", required=True, max_length=100, help="e.g. Academic Year 2027-28"),
            _field("start_date", "Starts", "date", required=True),
            _field("end_date", "Ends", "date", required=True),
            _field("is_current", "Current session", "bool"),
        ],
    },
    "departments": {
        "model": Department, "label": "Departments", "group": "Staff", "order": "name",
        "hint": "Departments teachers belong to; shown on the public Faculty page.",
        "fields": [NAME, DESCRIPTION],
    },
    "positions": {
        "model": Position, "label": "Positions", "group": "Staff", "order": "name",
        "hint": "Job titles for teachers and staff.",
        "fields": [NAME, DESCRIPTION],
    },
    "leave_types": {
        "model": LeaveType, "label": "Leave types", "group": "Staff", "order": "name",
        "hint": "Kinds of leave students and teachers can ask for.",
        "fields": [
            NAME, DESCRIPTION,
            _field("max_days_per_year", "Days allowed per year", "int"),
            _field("requires_medical_certificate", "Needs a medical certificate", "bool"),
        ],
    },
    "expense_categories": {
        "model": ExpenseCategory, "label": "Expense categories", "group": "Finance", "order": "name",
        "hint": "Categories for school expenses, with an optional budget.",
        "fields": [
            NAME, DESCRIPTION,
            _field("budget_limit", "Budget limit", "decimal"),
            _field("requires_approval", "Needs approval", "bool"),
        ],
    },
    "gallery_categories": {
        "model": GalleryCategory, "label": "Gallery categories", "group": "Website", "order": "display_order",
        "hint": "Albums on the public Gallery page.",
        "fields": [
            _field("name", "Name", required=True, max_length=100), DESCRIPTION,
            _field("icon", "Icon name", max_length=50, help="Material icon name, e.g. Event"),
            _field("display_order", "Order", "int"),
        ],
    },
    "inventory_item_categories": {
        "model": InventoryItemCategory, "label": "Shop categories", "group": "School Shop", "order": "display_order",
        "shop": True, "hint": "Groups of things the School Shop sells, e.g. Uniform, Books.",
        "fields": [NAME, DESCRIPTION, _field("display_order", "Order", "int")],
    },
    "inventory_item_types": {
        "model": InventoryItemType, "label": "Shop items", "group": "School Shop", "order": "name",
        "shop": True, "hint": "Items the School Shop sells. Prices are set on the Pricing page.",
        "fields": [
            NAME, DESCRIPTION,
            _field("inventory_item_category_id", "Category", "ref", required=True, ref="inventory_item_categories"),
        ],
    },
    "inventory_size_types": {
        "model": InventorySizeType, "label": "Uniform sizes", "group": "School Shop", "order": "sort_order",
        "shop": True, "hint": "Sizes uniforms are sold in.",
        "fields": [NAME, DESCRIPTION, _field("sort_order", "Order", "int")],
    },
}


def _list_spec(kind: str) -> Dict[str, Any]:
    spec = LISTS.get(kind)
    if spec is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown list: {kind}")
    return spec


def _row(spec: Dict[str, Any], row) -> Dict[str, Any]:
    data = {"id": row.id, "is_active": bool(row.is_active)}
    for field in spec["fields"]:
        value = getattr(row, field["name"])
        if isinstance(value, Decimal):
            value = float(value)
        elif isinstance(value, date):
            value = value.isoformat()
        data[field["name"]] = value
    return data


def _invalid(message: str) -> HTTPException:
    return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, message)


def _clean(spec: Dict[str, Any], body: Dict[str, Any], creating: bool) -> Dict[str, Any]:
    """Values from the request, converted to each field's type and checked."""
    fields = {field["name"]: field for field in spec["fields"]}
    clean: Dict[str, Any] = {}
    for name, value in body.items():
        if name == "is_active":
            clean[name] = bool(value)
            continue
        field = fields.get(name)
        if field is None:
            continue  # ids, timestamps and unknown keys are ignored
        if isinstance(value, str):
            value = value.strip()
        if value in ("", None):
            value = None
        elif field["type"] in ("int", "ref"):
            try:
                value = int(value)
            except (TypeError, ValueError):
                raise _invalid(f"{field['label']}: enter a whole number")
        elif field["type"] == "decimal":
            try:
                value = Decimal(str(value))
            except InvalidOperation:
                raise _invalid(f"{field['label']}: enter a number")
            if value < 0:
                raise _invalid(f"{field['label']}: cannot be negative")
        elif field["type"] == "date":
            try:
                value = date.fromisoformat(str(value)[:10])
            except ValueError:
                raise _invalid(f"{field['label']}: enter a date")
        elif field["type"] == "bool":
            value = bool(value)
        elif field["max_length"] and len(value) > field["max_length"]:
            raise _invalid(f"{field['label']}: at most {field['max_length']} characters")
        if value is None and field["required"]:
            raise _invalid(f"{field['label']} is required")
        clean[name] = value
    if creating:
        missing = [field["label"] for field in spec["fields"] if field["required"] and clean.get(field["name"]) is None]
        if missing:
            raise _invalid(f"{', '.join(missing)} required")
    return clean


async def _check(db: AsyncSession, kind: str, spec: Dict[str, Any], row, values: Dict[str, Any]) -> None:
    model = spec["model"]
    name = values.get("name")
    if name is not None:
        taken = select(model.id).where(func.lower(model.name) == name.lower())
        if row is not None:
            taken = taken.where(model.id != row.id)
        if (await db.execute(taken)).first():
            raise HTTPException(status.HTTP_409_CONFLICT, f'"{name}" is already in {spec["label"].lower()}')

    for field in spec["fields"]:
        if field["type"] == "ref" and values.get(field["name"]) is not None:
            target = LISTS[field["ref"]]["model"]
            if await db.get(target, values[field["name"]]) is None:
                raise _invalid(f"{field['label']}: not found")

    if kind == "session_years":
        start = values.get("start_date", getattr(row, "start_date", None))
        end = values.get("end_date", getattr(row, "end_date", None))
        if start and end and end <= start:
            raise _invalid("The session must end after it starts")
        current = values.get("is_current", getattr(row, "is_current", False))
        active = values.get("is_active", getattr(row, "is_active", True))
        if current and not active:
            raise _invalid("The current session must stay in use")
        if row is not None and row.is_current and values.get("is_current") is False:
            raise _invalid("Make another session current instead; one session is always current")


@router.get("/lists")
async def list_kinds(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_admin_user)):
    shop = await svc.shop_enabled(db)
    return [
        {"kind": kind, "label": spec["label"], "group": spec["group"], "hint": spec["hint"], "fields": spec["fields"]}
        for kind, spec in LISTS.items()
        if shop or not spec.get("shop")
    ]


@router.get("/lists/{kind}")
async def list_rows(kind: str, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_admin_user)):
    spec = _list_spec(kind)
    model = spec["model"]
    order = getattr(model, spec["order"])
    rows = (await db.execute(select(model).order_by(order.asc().nulls_last(), model.id))).scalars().all()
    return [_row(spec, row) for row in rows]


async def _save(db: AsyncSession, kind: str, spec: Dict[str, Any], row) -> Dict[str, Any]:
    if kind == "session_years" and row.is_current:
        await db.execute(
            update(SessionYear).where(SessionYear.id != row.id, SessionYear.is_current.is_(True)).values(is_current=False)
        )
    await db.commit()
    await db.refresh(row)
    _clear_cache(db)
    return _row(spec, row)


@router.post("/lists/{kind}", status_code=status.HTTP_201_CREATED)
async def create_row(
    kind: str,
    body: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    spec = _list_spec(kind)
    values = _clean(spec, body, creating=True)
    values.setdefault("is_active", True)
    await _check(db, kind, spec, None, values)
    row = spec["model"](**values)
    db.add(row)
    await db.flush()
    return await _save(db, kind, spec, row)


@router.patch("/lists/{kind}/{row_id}")
async def update_row(
    kind: str,
    row_id: int,
    body: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    spec = _list_spec(kind)
    row = await db.get(spec["model"], row_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    values = _clean(spec, body, creating=False)
    await _check(db, kind, spec, row, values)
    for name, value in values.items():
        setattr(row, name, value)
    return await _save(db, kind, spec, row)
