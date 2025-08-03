from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import logging

from app.crud.base import CRUDBase
from app.models.user import User, UserTypeEnum
from app.models.metadata import UserType
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.logging import log_crud_operation


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)
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
        # Validate user_type_id exists
        user_type_result = await db.execute(select(UserType).where(UserType.id == obj_in.user_type_id))
        user_type = user_type_result.scalar_one_or_none()
        if not user_type:
            raise ValueError(f"Invalid user_type_id: {obj_in.user_type_id}")

        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            phone=obj_in.phone,
            user_type_id=obj_in.user_type_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_with_metadata(self, db: AsyncSession, id: int) -> Optional[User]:
        """Get user with metadata relationships loaded"""
        try:
            result = await db.execute(
                select(User)
                .options(selectinload(User.user_type))
                .where(User.id == id)
            )
            return result.scalar_one_or_none()
        except Exception as db_error:
            log_crud_operation("GET_WITH_METADATA", f"Database error: {str(db_error)}",
                             "error", user_id=id, error_type=type(db_error).__name__)
            logging.exception("Full database error traceback:")
            raise

    async def get_by_phone(self, db: AsyncSession, *, phone: str) -> Optional[User]:
        """Get user by phone number"""
        try:
            log_crud_operation("GET_BY_PHONE", f"Executing database query", phone=phone)
            result = await db.execute(select(User).where(User.phone == phone))
            user = result.scalar_one_or_none()
            log_crud_operation("GET_BY_PHONE", f"Database query completed",
                             phone=phone, found=user is not None)
            return user
        except Exception as db_error:
            log_crud_operation("GET_BY_PHONE", f"Database error: {str(db_error)}",
                             "error", phone=phone, error_type=type(db_error).__name__)
            logging.exception("Full database error traceback:")
            raise

    async def get_by_email_with_metadata(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Get user by email with metadata relationships loaded"""
        try:
            result = await db.execute(
                select(User)
                .options(
                    selectinload(User.user_type)
                    # Temporarily disabled due to schema issues:
                    # selectinload(User.student_profile),
                    # selectinload(User.teacher_profile)
                )
                .where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as db_error:
            log_crud_operation("GET_BY_EMAIL_WITH_METADATA", f"Database error: {str(db_error)}",
                             "error", email=email, error_type=type(db_error).__name__)
            logging.exception("Full database error traceback:")
            raise

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate user by email or phone number.
        For backward compatibility, the parameter is still called 'email' but can accept phone numbers.
        """
        try:
            identifier = email  # Can be email or phone
            log_crud_operation("AUTHENTICATE", f"Authenticating user", identifier=identifier)

            # Step 1: Try to get user by email first, then by phone if not found
            user = None
            try:
                # First try email lookup
                user = await self.get_by_email(db, email=identifier)
                if user:
                    log_crud_operation("AUTHENTICATE", f"User found by email",
                                     identifier=identifier, user_id=user.id)
                else:
                    # If not found by email, try phone lookup (for students)
                    user = await self.get_by_phone(db, phone=identifier)
                    if user:
                        log_crud_operation("AUTHENTICATE", f"User found by phone",
                                         identifier=identifier, user_id=user.id)

                log_crud_operation("AUTHENTICATE", f"User lookup completed",
                                 identifier=identifier, found=user is not None)
            except Exception as lookup_error:
                log_crud_operation("AUTHENTICATE", f"Error looking up user: {str(lookup_error)}",
                                 "error", identifier=identifier)
                raise

            if not user:
                log_crud_operation("AUTHENTICATE", f"User not found", "warning", identifier=identifier)
                return None

            log_crud_operation("AUTHENTICATE", f"User found successfully",
                             email=user.email, user_id=user.id, user_type=str(user.user_type_enum))

            # Step 2: Verify password
            try:
                password_valid = verify_password(password, user.hashed_password)
                log_crud_operation("AUTHENTICATE", f"Password verification completed",
                                 identifier=identifier, valid=password_valid)
            except Exception as password_error:
                log_crud_operation("AUTHENTICATE", f"Error verifying password: {str(password_error)}",
                                 "error", identifier=identifier)
                raise

            if not password_valid:
                log_crud_operation("AUTHENTICATE", f"Invalid password", "warning", identifier=identifier)
                return None

            log_crud_operation("AUTHENTICATE", f"Authentication successful", identifier=identifier)
            return user

        except Exception as auth_error:
            log_crud_operation("AUTHENTICATE", f"Unexpected error: {str(auth_error)}",
                             "error", identifier=email, error_type=type(auth_error).__name__)
            logging.exception("Full authentication error traceback:")
            raise

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.user_type_enum == UserTypeEnum.ADMIN


user_crud = CRUDUser()
