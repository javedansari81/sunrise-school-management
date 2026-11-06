"""
Create a school: the school row, its first admin login, and its default lists.

The lists (classes, session years, departments, ...) are copied from a template
school, by default settings.TEMPLATE_SCHOOL_CODE (sunrise). Every column the
table really has is copied, read from the database catalog rather than the ORM
models, so nothing is lost when a model is behind its table. Foreign keys between
copied lists (inventory item type -> category) are remapped to the new rows.

Runs on a platform session (cross-school) inside the caller's transaction.
"""
from typing import Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.school import School
from app.models.user import User

ADMIN_USER_TYPE_ID = 1

# Copy order matters: a table is copied after the tables it references.
# (table, {column: referenced list table}) for columns that need remapping.
LIST_TABLES: List[Tuple[str, Dict[str, str]]] = [
    ("classes", {}),
    ("session_years", {}),
    ("departments", {}),
    ("positions", {}),
    ("expense_categories", {}),
    ("gallery_categories", {}),
    ("leave_types", {}),
    ("inventory_size_types", {}),
    ("inventory_item_category", {}),
    ("inventory_item_types", {"inventory_item_category_id": "inventory_item_category"}),
]

_NOT_COPIED = {"id", "school_id", "created_at", "updated_at"}


async def _copyable_columns(db: AsyncSession, table: str) -> List[str]:
    rows = await db.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = current_schema() AND table_name = :table ORDER BY ordinal_position"
        ),
        {"table": table},
    )
    return [r[0] for r in rows if r[0] not in _NOT_COPIED]


async def copy_lists(db: AsyncSession, *, from_school_id: int, to_school_id: int) -> Dict[str, int]:
    """Copy every list row of one school to another. Returns rows copied per table."""
    id_maps: Dict[str, Dict[int, int]] = {}
    copied: Dict[str, int] = {}
    for table, remap in LIST_TABLES:
        columns = await _copyable_columns(db, table)
        if not columns:
            continue
        column_sql = ", ".join(f'"{c}"' for c in columns)
        source = (
            await db.execute(
                text(f'SELECT id, {column_sql} FROM "{table}" WHERE school_id = :school ORDER BY id'),
                {"school": from_school_id},
            )
        ).mappings().all()

        insert_sql = text(
            f'INSERT INTO "{table}" (school_id, {column_sql}) '
            f'VALUES (:__school_id, {", ".join(":" + c for c in columns)}) RETURNING id'
        )
        mapping: Dict[int, int] = {}
        for row in source:
            values = {c: row[c] for c in columns}
            for column, referenced in remap.items():
                if values.get(column) is not None:
                    values[column] = id_maps[referenced][values[column]]
            values["__school_id"] = to_school_id
            new_id = (await db.execute(insert_sql, values)).scalar_one()
            mapping[row["id"]] = new_id
        id_maps[table] = mapping
        copied[table] = len(mapping)
    return copied


async def create_school(
    db: AsyncSession,
    *,
    school_fields: dict,
    admin_fields: dict,
    template_code: Optional[str],
) -> Tuple[School, User, Optional[str], Dict[str, int]]:
    """
    Create the school, its admin and its lists. Raises LookupError when an explicitly
    named template school does not exist. Does not commit.
    """
    explicit_template = template_code is not None
    template_code = (template_code or settings.TEMPLATE_SCHOOL_CODE or "").strip().lower() or None
    template_id = None
    if template_code:
        template_id = (
            await db.execute(text("SELECT id FROM schools WHERE code = :code"), {"code": template_code})
        ).scalar_one_or_none()
        if template_id is None:
            if explicit_template:
                raise LookupError(f"Template school '{template_code}' not found")
            template_code = None  # default template missing: create the school with empty lists

    school = School(**school_fields)
    db.add(school)
    await db.flush()

    admin = User(
        school_id=school.id,
        email=admin_fields["email"],
        password=get_password_hash(admin_fields["password"]),
        first_name=admin_fields["first_name"],
        last_name=admin_fields["last_name"],
        phone=admin_fields.get("phone"),
        user_type_id=ADMIN_USER_TYPE_ID,
        is_active=True,
    )
    db.add(admin)
    await db.flush()

    copied: Dict[str, int] = {}
    if template_id is not None:
        copied = await copy_lists(db, from_school_id=template_id, to_school_id=school.id)
    return school, admin, template_code, copied
