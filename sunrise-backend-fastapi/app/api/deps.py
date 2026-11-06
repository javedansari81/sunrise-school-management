from typing import Generator, Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.school_resolver import resolve_school_code
from app.core.security import decode_access_token, decode_platform_token
from app.core.tenant import bind_platform_session, set_session_school
from app.crud.crud_user import CRUDUser
from app.models.school import School
from app.models.user import PLATFORM_ADMIN_USER_TYPE_ID, User

security = HTTPBearer()

_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def _load_active_school(db: AsyncSession, *, code: Optional[str] = None, school_id: Optional[int] = None) -> School:
    query = select(School)
    query = query.where(School.code == code) if code is not None else query.where(School.id == school_id)
    school = (await db.execute(query)).scalar_one_or_none()
    if school is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found")
    if not school.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This school is suspended")
    return school


async def get_current_school(request: Request, db: AsyncSession = Depends(get_db)) -> School:
    """
    School named by the request (X-School-Code header, Origin or Host subdomain),
    falling back to settings.DEFAULT_SCHOOL_CODE. Binds the request's DB session
    to that school. Used by routes that run before login (login, public pages).
    """
    code = resolve_school_code(request) or settings.DEFAULT_SCHOOL_CODE or None
    if code is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="School could not be identified")
    school = await _load_active_school(db, code=code)
    set_session_school(db, school.id)
    request.state.school = school
    return school


async def get_school_db(
    school: School = Depends(get_current_school),
    db: AsyncSession = Depends(get_db),
) -> AsyncSession:
    """DB session bound to the request's school, for routes without a logged-in user."""
    return db


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user.
    The token's school binds the DB session, so every query in the request is
    limited to that school. A token is only accepted on its own school's subdomain.
    """
    decoded = decode_access_token(credentials.credentials)
    if decoded is None:
        raise _CREDENTIALS_ERROR
    user_id, school_id = decoded
    if school_id is None:
        # Token issued before multi-tenancy: ask the user to log in again
        raise _CREDENTIALS_ERROR

    school = await _load_active_school(db, school_id=school_id)
    requested_code = resolve_school_code(request)
    if requested_code is not None and requested_code != school.code:
        raise _CREDENTIALS_ERROR
    set_session_school(db, school.id)
    request.state.school = school

    # Use the new CRUD instance and get user with metadata
    user_crud = CRUDUser()
    user = await user_crud.get_with_metadata(db, id=int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current admin user
    Requires user to be active and have admin role (user_type_id = 1) or super admin role (user_type_id = 6)
    SUPER_ADMIN has all ADMIN privileges
    """
    # Allow both ADMIN (1) and SUPER_ADMIN (6) user types
    if current_user.user_type_id not in [1, 6]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user


async def get_current_platform_admin(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Platform admin from a platform token (scope=platform, no school).
    Turns the request's DB session into a platform session that works across
    schools. School tokens are rejected, and platform tokens are rejected by
    get_current_user, so the two kinds of login never mix.
    """
    user_id = decode_platform_token(credentials.credentials)
    if user_id is None:
        raise _CREDENTIALS_ERROR
    bind_platform_session(db)
    user = (
        await db.execute(
            select(User).where(
                User.id == int(user_id),
                User.school_id.is_(None),
                User.user_type_id == PLATFORM_ADMIN_USER_TYPE_ID,
                (User.is_deleted == False) | (User.is_deleted.is_(None)),  # noqa: E712
            )
        )
    ).scalar_one_or_none()
    if user is None or not user.is_active:
        raise _CREDENTIALS_ERROR
    return user
