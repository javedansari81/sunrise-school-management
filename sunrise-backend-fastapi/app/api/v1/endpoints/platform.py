"""
Platform admin API: log in as a platform admin and manage schools.

Platform admins belong to no school. Their token (scope=platform) only works on
these routes, and school tokens never work here. Every route except login runs on
a platform session, which reads and writes across schools.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_platform_admin
from app.core.database import get_db
from app.core.security import create_platform_token, get_password_hash, verify_password
from app.core.tenant import bind_platform_session
from app.models.school import School, SchoolStatus
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import PLATFORM_ADMIN_USER_TYPE_ID, User
from app.schemas.platform import (
    PlatformAdminCreate,
    PlatformAdminOut,
    PlatformLoginRequest,
    PlatformLoginResponse,
    SchoolCreate,
    SchoolCreated,
    SchoolList,
    SchoolOut,
    SchoolSummary,
    SchoolUpdate,
)
from app.services.school_provisioning import create_school

router = APIRouter()

_LOGIN_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password",
    headers={"WWW-Authenticate": "Bearer"},
)


def _not_deleted(model):
    return (model.is_deleted == False) | (model.is_deleted.is_(None))  # noqa: E712


async def _get_school(db: AsyncSession, school_id: int) -> School:
    school = await db.get(School, school_id)
    if school is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found")
    return school


async def _code_taken(db: AsyncSession, code: str, exclude_id: Optional[int] = None) -> bool:
    query = select(School.id).where(School.code == code)
    if exclude_id is not None:
        query = query.where(School.id != exclude_id)
    return (await db.execute(query)).first() is not None


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@router.post("/auth/login", response_model=PlatformLoginResponse)
async def platform_login(body: PlatformLoginRequest, db: AsyncSession = Depends(get_db)):
    """Log in as a platform admin. Returns a platform token (not valid for any school)."""
    bind_platform_session(db)
    user = (
        await db.execute(
            select(User).where(
                User.email == body.email,
                User.school_id.is_(None),
                User.user_type_id == PLATFORM_ADMIN_USER_TYPE_ID,
                _not_deleted(User),
            )
        )
    ).scalar_one_or_none()
    try:
        valid = user is not None and verify_password(body.password, user.password)
    except ValueError:
        valid = False
    if not valid:
        raise _LOGIN_ERROR
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return PlatformLoginResponse(access_token=create_platform_token(user.id), user=PlatformAdminOut.model_validate(user))


@router.get("/auth/me", response_model=PlatformAdminOut)
async def platform_me(admin: User = Depends(get_current_platform_admin)):
    return admin


# ---------------------------------------------------------------------------
# Platform admins
# ---------------------------------------------------------------------------

def _platform_admins():
    return select(User).where(
        User.school_id.is_(None), User.user_type_id == PLATFORM_ADMIN_USER_TYPE_ID, _not_deleted(User)
    )


@router.get("/admins", response_model=list[PlatformAdminOut])
async def list_platform_admins(
    admin: User = Depends(get_current_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    return (await db.execute(_platform_admins().order_by(User.id))).scalars().all()


@router.post("/admins", response_model=PlatformAdminOut, status_code=status.HTTP_201_CREATED)
async def create_platform_admin(
    body: PlatformAdminCreate,
    admin: User = Depends(get_current_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create another platform admin. The first one is created with scripts/create_platform_admin.py."""
    if (await db.execute(_platform_admins().where(User.email == body.email))).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Platform admin {body.email} already exists")
    new_admin = User(
        school_id=None,
        email=body.email,
        password=get_password_hash(body.password),
        first_name=body.first_name,
        last_name=body.last_name,
        user_type_id=PLATFORM_ADMIN_USER_TYPE_ID,
        is_active=True,
    )
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    return new_admin


# ---------------------------------------------------------------------------
# Schools
# ---------------------------------------------------------------------------

@router.get("/schools", response_model=SchoolList)
async def list_schools(
    status_filter: Optional[str] = Query(None, alias="status", pattern="^(ACTIVE|SUSPENDED)$"),
    search: Optional[str] = Query(None, description="Matches code or name"),
    admin: User = Depends(get_current_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    """All schools with their user, student and teacher counts."""
    query = select(School).order_by(School.id)
    if status_filter:
        query = query.where(School.status == status_filter)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(School.code.ilike(pattern) | School.name.ilike(pattern))
    schools = (await db.execute(query)).scalars().all()

    async def counts(model):
        rows = await db.execute(
            select(model.school_id, func.count()).where(_not_deleted(model)).group_by(model.school_id)
        )
        return dict(rows.all())

    users, students, teachers = await counts(User), await counts(Student), await counts(Teacher)
    summaries = [
        SchoolSummary(
            **SchoolOut.model_validate(s).model_dump(),
            users=users.get(s.id, 0),
            students=students.get(s.id, 0),
            teachers=teachers.get(s.id, 0),
        )
        for s in schools
    ]
    return SchoolList(schools=summaries, total=len(summaries))


@router.post("/schools", response_model=SchoolCreated, status_code=status.HTTP_201_CREATED)
async def create_school_endpoint(
    body: SchoolCreate,
    admin: User = Depends(get_current_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a school with its first admin login. Its lists (classes, session years,
    departments, inventory lists, ...) are copied from the template school.
    """
    if await _code_taken(db, body.code):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"School code '{body.code}' is already used")

    school_fields = body.model_dump(exclude={"admin", "copy_lists_from"}, exclude_none=True)
    try:
        school, school_admin, copied_from, copied = await create_school(
            db,
            school_fields=school_fields,
            admin_fields=body.admin.model_dump(),
            template_code=body.copy_lists_from,
        )
        await db.commit()
    except LookupError as error:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"School code '{body.code}' is already used")

    await db.refresh(school)
    return SchoolCreated(
        school=SchoolOut.model_validate(school),
        admin=PlatformAdminOut.model_validate(school_admin),
        copied_from=copied_from,
        copied_lists=copied,
    )


@router.get("/schools/{school_id}", response_model=SchoolOut)
async def get_school(
    school_id: int,
    admin: User = Depends(get_current_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    return await _get_school(db, school_id)


@router.patch("/schools/{school_id}", response_model=SchoolOut)
async def update_school(
    school_id: int,
    body: SchoolUpdate,
    admin: User = Depends(get_current_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    """Edit a school's details. Changing its code changes its subdomain."""
    school = await _get_school(db, school_id)
    changes = body.model_dump(exclude_unset=True)
    if "name" in changes and not changes["name"]:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="name cannot be empty")
    if changes.get("code") and await _code_taken(db, changes["code"], exclude_id=school.id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"School code '{changes['code']}' is already used")
    for field, value in changes.items():
        if value is None and field in ("code", "name", "timezone", "currency", "academic_year_start_month"):
            continue  # required columns cannot be cleared
        setattr(school, field, value)
    await db.commit()
    await db.refresh(school)
    return school


async def _set_status(db: AsyncSession, school_id: int, new_status: str) -> School:
    school = await _get_school(db, school_id)
    school.status = new_status
    await db.commit()
    await db.refresh(school)
    return school


@router.post("/schools/{school_id}/suspend", response_model=SchoolOut)
async def suspend_school(
    school_id: int,
    admin: User = Depends(get_current_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    """Suspend a school: its users cannot log in, and their existing tokens stop working at once."""
    return await _set_status(db, school_id, SchoolStatus.SUSPENDED)


@router.post("/schools/{school_id}/activate", response_model=SchoolOut)
async def activate_school(
    school_id: int,
    admin: User = Depends(get_current_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    return await _set_status(db, school_id, SchoolStatus.ACTIVE)
