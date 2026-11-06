from datetime import datetime, timedelta
from typing import Any, Union, Optional, Tuple
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SCHOOL_CLAIM = "sid"
SCOPE_CLAIM = "scope"
PLATFORM_SCOPE = "platform"


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None, *, school_id: int
) -> str:
    """Create a JWT for a user of one school. The school travels in the ``sid`` claim."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject), SCHOOL_CLAIM: int(school_id)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def _validate_password_length(password: str) -> None:
    """
    Validate password length to comply with bcrypt limitations.
    bcrypt has a maximum password length of 72 bytes.
    Raises ValueError if password is too long.
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        raise ValueError(
            f"Password is too long ({len(password_bytes)} bytes). "
            f"Maximum allowed length is 72 bytes. "
            f"Please use a shorter password."
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    Raises ValueError if password exceeds 72 bytes for bcrypt compatibility.
    """
    _validate_password_length(plain_password)
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a hash for a password.
    Raises ValueError if password exceeds 72 bytes for bcrypt compatibility.
    """
    _validate_password_length(password)
    return pwd_context.hash(password)


def create_platform_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    JWT for a platform admin. It carries scope=platform and no school claim, so
    school routes (get_current_user) reject it, and platform routes reject school tokens.
    """
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"exp": expire, "sub": str(subject), SCOPE_CLAIM: PLATFORM_SCOPE}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_platform_token(token: str) -> Optional[str]:
    """User id from a platform admin token, or None for any other token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.JWTError:
        return None
    if payload.get(SCOPE_CLAIM) != PLATFORM_SCOPE or payload.get(SCHOOL_CLAIM) is not None:
        return None
    user_id = payload.get("sub")
    return str(user_id) if user_id is not None else None


def decode_access_token(token: str) -> Optional[Tuple[str, Optional[int]]]:
    """
    Verify a JWT and return ``(user_id, school_id)``.
    ``school_id`` is None for tokens issued before multi-tenancy.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.JWTError:
        return None
    user_id = payload.get("sub")
    if user_id is None:
        return None
    school_id = payload.get(SCHOOL_CLAIM)
    try:
        school_id = int(school_id) if school_id is not None else None
    except (TypeError, ValueError):
        return None
    return str(user_id), school_id


def verify_token(token: str) -> Optional[str]:
    """
    Verify a JWT token and return the user ID if valid.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except jwt.JWTError:
        return None
