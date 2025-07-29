from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging

from app.crud.base import CRUDBase
from app.models.user import User, UserTypeEnum
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.logging import log_crud_operation


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        try:
            log_crud_operation("GET_BY_EMAIL", f"Executing database query", email=email)
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            log_crud_operation("GET_BY_EMAIL", f"Database query completed",
                             email=email, found=user is not None)
            return user
        except Exception as db_error:
            log_crud_operation("GET_BY_EMAIL", f"Database error: {str(db_error)}",
                             "error", email=email, error_type=type(db_error).__name__)
            logging.exception("Full database error traceback:")
            raise

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            mobile=obj_in.mobile,
            email=obj_in.email,
            password=get_password_hash(obj_in.password),
            user_type=obj_in.user_type,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> Optional[User]:
        try:
            log_crud_operation("AUTHENTICATE", f"Authenticating user", email=email)

            # Step 1: Get user by email
            try:
                user = await self.get_by_email(db, email=email)
                log_crud_operation("AUTHENTICATE", f"User lookup completed",
                                 email=email, found=user is not None)
            except Exception as lookup_error:
                log_crud_operation("AUTHENTICATE", f"Error looking up user by email: {str(lookup_error)}",
                                 "error", email=email)
                raise

            if not user:
                log_crud_operation("AUTHENTICATE", f"User not found", "warning", email=email)
                return None

            log_crud_operation("AUTHENTICATE", f"User found successfully",
                             email=user.email, user_id=user.id, user_type=str(user.user_type_enum))

            # Step 2: Verify password
            try:
                password_valid = verify_password(password, user.password)
                log_crud_operation("AUTHENTICATE", f"Password verification completed",
                                 email=email, valid=password_valid)
            except Exception as password_error:
                log_crud_operation("AUTHENTICATE", f"Error verifying password: {str(password_error)}",
                                 "error", email=email)
                raise

            if not password_valid:
                log_crud_operation("AUTHENTICATE", f"Invalid password", "warning", email=email)
                return None

            log_crud_operation("AUTHENTICATE", f"Authentication successful", email=email)
            return user

        except Exception as auth_error:
            log_crud_operation("AUTHENTICATE", f"Unexpected error: {str(auth_error)}",
                             "error", email=email, error_type=type(auth_error).__name__)
            logging.exception("Full authentication error traceback:")
            raise

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.user_type_enum == UserTypeEnum.ADMIN


user_crud = CRUDUser(User)
