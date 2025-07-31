from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.crud.crud_user import CRUDUser
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.models.user import User

router = APIRouter()


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
