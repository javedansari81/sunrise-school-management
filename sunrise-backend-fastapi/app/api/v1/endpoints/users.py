from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import logging

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.crud.crud_user import CRUDUser
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.schemas.auth import (
    PasswordResetRequest,
    PasswordResetResponse,
    ChangePasswordRequest,
    ChangePasswordResponse
)
from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.core.password_config import DEFAULT_PASSWORD
from app.core.logging import log_crud_operation

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[UserSchema])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all users with metadata
    """
    # Check if user is admin
    if not current_user.user_type or current_user.user_type.name != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view all users"
        )

    user_crud = CRUDUser()
    users = await user_crud.get_multi(db, skip=skip, limit=limit)

    # Convert to response schema with metadata
    result = []
    for user in users:
        user_with_metadata = await user_crud.get_with_metadata(db, id=user.id)
        result.append(UserSchema.from_orm_with_metadata(user_with_metadata))

    return result


@router.post("/", response_model=UserSchema)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new user
    """
    # Check if user is admin
    if not current_user.user_type or current_user.user_type.name != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create users"
        )

    user_crud = CRUDUser()

    # Check if user already exists
    existing_user = await user_crud.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Create user
    user = await user_crud.create(db, obj_in=user_in)
    user_with_metadata = await user_crud.get_with_metadata(db, id=user.id)

    return UserSchema.from_orm_with_metadata(user_with_metadata)


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user by ID with metadata
    """
    # Users can only view their own profile unless they're admin
    if current_user.id != user_id and (not current_user.user_type or current_user.user_type.name != "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    user_crud = CRUDUser()
    user = await user_crud.get_with_metadata(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserSchema.from_orm_with_metadata(user)


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update user by ID
    """
    # Users can only update their own profile unless they're admin
    if current_user.id != user_id and (not current_user.user_type or current_user.user_type.name != "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    user_crud = CRUDUser()
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update user
    user = await user_crud.update(db, db_obj=user, obj_in=user_in)
    user_with_metadata = await user_crud.get_with_metadata(db, id=user.id)

    return UserSchema.from_orm_with_metadata(user_with_metadata)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete user by ID (soft delete - set is_active = False)
    """
    # Only admins can delete users
    if not current_user.user_type or current_user.user_type.name != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete users"
        )

    user_crud = CRUDUser()
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Soft delete
    await user_crud.update(db, db_obj=user, obj_in={"is_active": False})

    return {"message": "User deleted successfully"}


@router.put("/{user_id}/reset-password", response_model=PasswordResetResponse)
async def reset_user_password(
    user_id: int,
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Reset user password to default (Admin only)

    This endpoint allows administrators to reset any user's password to the default password.
    The user can then login with the default password and optionally change it later.
    """
    # Only admins can reset passwords
    if not current_user.user_type or current_user.user_type.name != "ADMIN":
        log_crud_operation(
            "PASSWORD_RESET_DENIED",
            f"Non-admin user attempted password reset",
            "warning",
            admin_id=current_user.id,
            target_user_id=user_id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can reset user passwords"
        )

    user_crud = CRUDUser()

    # Get target user
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get user with metadata for full information
    user_with_metadata = await user_crud.get_with_metadata(db, id=user_id)

    try:
        # Hash the default password
        new_password_hash = get_password_hash(DEFAULT_PASSWORD)

        # Update password
        await user_crud.update(
            db,
            db_obj=user,
            obj_in={"password": new_password_hash}
        )

        # Log the password reset action
        log_crud_operation(
            "PASSWORD_RESET_SUCCESS",
            f"Admin reset password for user",
            admin_id=current_user.id,
            admin_email=current_user.email,
            target_user_id=user.id,
            target_user_email=user.email,
            target_user_type=user_with_metadata.user_type.name if user_with_metadata.user_type else "UNKNOWN"
        )

        logger.info(
            f"Password reset by admin {current_user.id} ({current_user.email}) "
            f"for user {user.id} ({user.email})"
        )

        # Return success response with credentials
        return PasswordResetResponse(
            success=True,
            message="Password reset successfully",
            user_id=user.id,
            email=user.email,
            default_password=DEFAULT_PASSWORD,
            user_name=f"{user.first_name} {user.last_name}",
            user_type=user_with_metadata.user_type.name if user_with_metadata.user_type else "UNKNOWN"
        )

    except Exception as e:
        log_crud_operation(
            "PASSWORD_RESET_ERROR",
            f"Error resetting password: {str(e)}",
            "error",
            admin_id=current_user.id,
            target_user_id=user_id
        )
        logger.error(f"Error resetting password for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )


@router.put("/me/change-password", response_model=ChangePasswordResponse)
async def change_own_password(
    password_request: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Change current user's password

    Allows authenticated users to change their own password by providing
    their current password and a new password.
    """
    user_crud = CRUDUser()

    try:
        # Verify current password
        if not verify_password(password_request.current_password, current_user.password):
            log_crud_operation(
                "PASSWORD_CHANGE_FAILED",
                "Incorrect current password provided",
                "warning",
                user_id=current_user.id,
                user_email=current_user.email
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Check if new password is same as current
        if verify_password(password_request.new_password, current_user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password"
            )

        # Hash new password
        new_password_hash = get_password_hash(password_request.new_password)

        # Update password and track change time
        await user_crud.update(
            db,
            db_obj=current_user,
            obj_in={
                "password": new_password_hash,
                "password_last_changed": datetime.now(timezone.utc)
            }
        )

        # Log successful password change
        log_crud_operation(
            "PASSWORD_CHANGE_SUCCESS",
            "User changed their password",
            user_id=current_user.id,
            user_email=current_user.email
        )

        logger.info(f"User {current_user.id} ({current_user.email}) changed their password")

        return ChangePasswordResponse(
            success=True,
            message="Password changed successfully"
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as ve:
        # Handle password validation errors (e.g., too long for bcrypt)
        log_crud_operation(
            "PASSWORD_CHANGE_ERROR",
            f"Password validation error: {str(ve)}",
            "error",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        log_crud_operation(
            "PASSWORD_CHANGE_ERROR",
            f"Error changing password: {str(e)}",
            "error",
            user_id=current_user.id
        )
        logger.error(f"Error changing password for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )
