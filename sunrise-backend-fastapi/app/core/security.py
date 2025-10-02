from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
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
