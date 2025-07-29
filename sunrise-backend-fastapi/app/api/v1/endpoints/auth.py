from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.core.config import settings
from app.core.permissions import get_user_permissions, get_dashboard_permissions, filter_menu_items
from app.crud.crud_user import user_crud
from app.crud import student_crud, teacher_crud
from app.schemas.auth import LoginRequest, LoginResponse, Token
from app.schemas.user import User as UserSchema, UserCreate, UserLoginResponse, UserProfile, UserTypeEnum
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/login", response_model=UserLoginResponse)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Enhanced user login endpoint with role-based permissions
    """
    user = await user_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    await user_crud.update(db, db_obj=user, obj_in={"last_login": user.last_login})

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    # Get user permissions
    permissions = get_user_permissions(user.user_type)

    # Get profile data based on user type
    profile_data = None
    try:
        if user.user_type == UserTypeEnum.STUDENT and user.student_id:
            student_profile = await student_crud.get(db, id=user.student_id)
            if student_profile:
                profile_data = {
                    "type": "student",
                    "profile": {
                        "id": student_profile.id,
                        "admission_number": student_profile.admission_number,
                        "first_name": student_profile.first_name,
                        "last_name": student_profile.last_name,
                        "current_class": student_profile.current_class,
                        "section": getattr(student_profile, 'section', None)
                    }
                }
        elif user.user_type == UserTypeEnum.TEACHER and user.teacher_id:
            teacher_profile = await teacher_crud.get(db, id=user.teacher_id)
            if teacher_profile:
                profile_data = {
                    "type": "teacher",
                    "profile": {
                        "id": teacher_profile.id,
                        "employee_id": teacher_profile.employee_id,
                        "first_name": teacher_profile.first_name,
                        "last_name": teacher_profile.last_name,
                        "department": getattr(teacher_profile, 'department', None),
                        "position": getattr(teacher_profile, 'position', None)
                    }
                }
    except Exception as profile_error:
        # If profile fetching fails, continue without profile data
        print(f"Profile fetch error: {profile_error}")
        profile_data = None

    return UserLoginResponse(
        user=user,
        access_token=access_token,
        token_type="bearer",
        permissions=permissions,
        profile_data=profile_data
    )


@router.post("/login-json", response_model=UserLoginResponse)
async def login_json(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Enhanced user login endpoint using JSON payload with role-based permissions
    """
    try:
        user = await user_crud.authenticate(
            db, email=login_data.email, password=login_data.password
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif not user_crud.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and return a generic error message
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    await user_crud.update(db, db_obj=user, obj_in={"last_login": user.last_login})

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    # Get user permissions
    permissions = get_user_permissions(user.user_type)

    # Get profile data based on user type
    profile_data = None
    try:
        if user.user_type == UserTypeEnum.STUDENT and user.student_id:
            student_profile = await student_crud.get(db, id=user.student_id)
            if student_profile:
                profile_data = {
                    "type": "student",
                    "profile": {
                        "id": student_profile.id,
                        "admission_number": student_profile.admission_number,
                        "first_name": student_profile.first_name,
                        "last_name": student_profile.last_name,
                        "current_class": student_profile.current_class,
                        "section": getattr(student_profile, 'section', None)
                    }
                }
        elif user.user_type == UserTypeEnum.TEACHER and user.teacher_id:
            teacher_profile = await teacher_crud.get(db, id=user.teacher_id)
            if teacher_profile:
                profile_data = {
                    "type": "teacher",
                    "profile": {
                        "id": teacher_profile.id,
                        "employee_id": teacher_profile.employee_id,
                        "first_name": teacher_profile.first_name,
                        "last_name": teacher_profile.last_name,
                        "department": getattr(teacher_profile, 'department', None),
                        "position": getattr(teacher_profile, 'position', None)
                    }
                }
    except Exception as profile_error:
        # If profile fetching fails, continue without profile data
        print(f"Profile fetch error: {profile_error}")
        profile_data = None

    return UserLoginResponse(
        user=user,
        access_token=access_token,
        token_type="bearer",
        permissions=permissions,
        profile_data=profile_data
    )


@router.post("/register", response_model=UserSchema)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    User registration endpoint
    """
    # Check if user already exists
    existing_user = await user_crud.get_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user = await user_crud.create(db, obj_in=user_data)
    return user


@router.get("/me", response_model=UserProfile)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user information with profile data
    """
    # Get linked profile data
    student_profile = None
    teacher_profile = None

    if current_user.user_type == UserTypeEnum.STUDENT and current_user.student_id:
        student = await student_crud.get(db, id=current_user.student_id)
        if student:
            student_profile = student.__dict__

    if current_user.user_type == UserTypeEnum.TEACHER and current_user.teacher_id:
        teacher = await teacher_crud.get(db, id=current_user.teacher_id)
        if teacher:
            teacher_profile = teacher.__dict__

    user_dict = current_user.__dict__.copy()
    user_dict['student_profile'] = student_profile
    user_dict['teacher_profile'] = teacher_profile

    return user_dict


@router.post("/logout")
async def logout():
    """
    User logout endpoint
    Note: With JWT tokens, logout is typically handled client-side
    by removing the token from storage
    """
    return {"message": "Successfully logged out"}


@router.get("/permissions")
async def get_user_permissions_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's permissions and dashboard configuration
    """
    permissions = get_user_permissions(current_user.user_type)
    dashboard_config = get_dashboard_permissions(current_user.user_type)
    menu_items = filter_menu_items(current_user.user_type)

    return {
        "user_type": current_user.user_type,
        "permissions": permissions,
        "dashboard_config": dashboard_config,
        "menu_items": menu_items
    }


@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user profile with role-specific data
    """
    profile_data = {
        "user_info": {
            "id": current_user.id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "email": current_user.email,
            "mobile": current_user.mobile,
            "user_type": current_user.user_type,
            "last_login": current_user.last_login,
            "created_at": current_user.created_at
        }
    }

    # Add role-specific profile data
    if current_user.user_type == UserTypeEnum.STUDENT and current_user.student_id:
        student = await student_crud.get_with_fees(db, id=current_user.student_id)
        if student:
            # Calculate fee summary
            total_fees_due = sum(fee.balance_amount for fee in student.fee_records)
            total_fees_paid = sum(fee.paid_amount for fee in student.fee_records)

            profile_data["student_profile"] = {
                "admission_number": student.admission_number,
                "current_class": student.current_class,
                "section": student.section,
                "roll_number": student.roll_number,
                "date_of_birth": student.date_of_birth,
                "gender": student.gender,
                "address": student.address,
                "father_name": student.father_name,
                "mother_name": student.mother_name,
                "admission_date": student.admission_date,
                "fee_summary": {
                    "total_due": total_fees_due,
                    "total_paid": total_fees_paid,
                    "status": "Paid" if total_fees_due == 0 else "Pending"
                }
            }

    elif current_user.user_type == UserTypeEnum.TEACHER and current_user.teacher_id:
        teacher = await teacher_crud.get(db, id=current_user.teacher_id)
        if teacher:
            profile_data["teacher_profile"] = {
                "employee_id": teacher.employee_id,
                "position": teacher.position,
                "department": teacher.department,
                "qualification": teacher.qualification,
                "experience_years": teacher.experience_years,
                "joining_date": teacher.joining_date,
                "employment_status": teacher.employment_status,
                "subjects": teacher.subjects,
                "specializations": teacher.specializations,
                "bio": teacher.bio
            }

    return profile_data


@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_active_user)
):
    """
    Protected route for testing authentication
    """
    return {
        "message": "This is a protected route",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "user_type": current_user.user_type
        }
    }
