from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.core.config import settings
from app.core.logging import log_auth_step
from app.core.permissions import get_user_permissions, get_dashboard_permissions, filter_menu_items
from app.crud.crud_user import CRUDUser
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
    user_crud = CRUDUser()
    user = await user_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
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

    # Get user with metadata for permissions
    user_with_metadata = await user_crud.get_with_metadata(db, id=user.id)
    user_type_name = user_with_metadata.user_type.name if user_with_metadata.user_type else "STUDENT"

    # Convert to enum for permissions (backward compatibility)
    from app.models.user import UserTypeEnum
    try:
        user_type_enum = UserTypeEnum(user_type_name)
    except ValueError:
        user_type_enum = UserTypeEnum.STUDENT

    # Get user permissions
    permissions = get_user_permissions(user_type_enum)

    # Initialize profile data and IDs
    profile_data = None
    student_id = None
    teacher_id = None

    # Get profile data based on user type and extract IDs
    try:
        if user_type_enum == UserTypeEnum.STUDENT and user_with_metadata.student_profile:
            student_profile = user_with_metadata.student_profile
            student_id = student_profile.id
            profile_data = {
                "type": "student",
                "profile": {
                    "id": student_profile.id,
                    "admission_number": student_profile.admission_number,
                    "first_name": student_profile.first_name,
                    "last_name": student_profile.last_name,
                    "class_name": student_profile.class_name if hasattr(student_profile, 'class_name') else None,
                    "section": getattr(student_profile, 'section', None)
                }
            }
        elif user_type_enum == UserTypeEnum.TEACHER and user_with_metadata.teacher_profile:
            teacher_profile = user_with_metadata.teacher_profile
            teacher_id = teacher_profile.id
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
        log_auth_step("PROFILE_ERROR", f"Profile fetch error: {profile_error}", "error")
        profile_data = None

    # Convert SQLAlchemy model to Pydantic schema
    user_dict = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "mobile": user.phone,
        "email": user.email,
        "user_type": user.user_type_enum.value.lower(),  # Return lowercase string for frontend
        "user_type_id": user.user_type_id,  # Add missing field
        "student_id": student_id,
        "teacher_id": teacher_id,
        "is_active": user.is_active,
        "is_verified": user.is_verified,  # Add missing field
        "last_login": user.last_login,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }

    return UserLoginResponse(
        user=user_dict,
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
        log_auth_step("LOGIN_START", f"Login attempt for email: {login_data.email}", email=login_data.email)

        # Initialize user_crud instance
        user_crud = CRUDUser()

        # Step 1: Authenticate user
        try:
            user = await user_crud.authenticate(
                db, email=login_data.email, password=login_data.password
            )
            log_auth_step("AUTH_QUERY", f"User authentication query completed", email=login_data.email)
        except Exception as auth_error:
            log_auth_step("AUTH_ERROR", f"Database authentication error: {str(auth_error)}",
                         "error", email=login_data.email, error_type=type(auth_error).__name__)
            logging.exception("Full authentication error traceback:")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database authentication error: {str(auth_error)}"
            )

        # Step 2: Check if user exists
        if not user:
            log_auth_step("USER_NOT_FOUND", f"User not found or invalid password",
                         "warning", email=login_data.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        log_auth_step("USER_FOUND", f"User found successfully",
                     email=user.email, user_id=user.id, user_type=str(user.user_type_enum))

        # Step 3: Check if user is active
        try:
            is_active = user_crud.is_active(user)
            log_auth_step("ACTIVE_CHECK", f"User active status checked",
                         email=user.email, is_active=is_active)
        except Exception as active_error:
            log_auth_step("ACTIVE_ERROR", f"Error checking user active status: {str(active_error)}",
                         "error", email=user.email)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error checking user status: {str(active_error)}"
            )

        if not is_active:
            log_auth_step("USER_INACTIVE", f"User is inactive", "warning", email=user.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

    except HTTPException:
        # Re-raise HTTP exceptions (these are expected errors)
        raise
    except Exception as unexpected_error:
        log_auth_step("UNEXPECTED_ERROR", f"Unexpected error during authentication: {str(unexpected_error)}",
                     "error", email=login_data.email, error_type=type(unexpected_error).__name__)
        logging.exception("Full unexpected error traceback:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected authentication error: {str(unexpected_error)}"
        )

    # Step 4: Update last login
    try:
        log_auth_step("UPDATE_LOGIN", f"Updating last login", email=user.email)
        user.last_login = datetime.utcnow()
        await user_crud.update(db, db_obj=user, obj_in={"last_login": user.last_login})
        log_auth_step("UPDATE_LOGIN", f"Last login updated successfully", email=user.email)
    except Exception as update_error:
        log_auth_step("UPDATE_LOGIN", f"Warning: Could not update last login: {str(update_error)}",
                     "warning", email=user.email)
        # Don't fail login for this, just log the warning

    # Step 5: Create access token
    try:
        log_auth_step("CREATE_TOKEN", f"Creating access token", email=user.email)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )
        log_auth_step("CREATE_TOKEN", f"Access token created successfully", email=user.email)
    except Exception as token_error:
        log_auth_step("CREATE_TOKEN", f"Error creating access token: {str(token_error)}",
                     "error", email=user.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating access token: {str(token_error)}"
        )

    # Step 6: Get user permissions
    try:
        log_auth_step("GET_PERMISSIONS", f"Getting permissions",
                     email=user.email, user_type=str(user.user_type_enum))
        permissions = get_user_permissions(user.user_type_enum)
        log_auth_step("GET_PERMISSIONS", f"Permissions retrieved",
                     email=user.email, count=len(permissions))
    except Exception as perm_error:
        log_auth_step("GET_PERMISSIONS", f"Error getting user permissions: {str(perm_error)}",
                     "error", email=user.email)
        # Use empty permissions as fallback
        permissions = []

    # Step 6.5: Get student_id and teacher_id safely (temporarily disabled due to schema issues)
    student_id = None
    teacher_id = None
    # try:
    #     if hasattr(user, 'student_profile') and user.student_profile:
    #         student_id = user.student_profile.id
    # except:
    #     pass
    # try:
    #     if hasattr(user, 'teacher_profile') and user.teacher_profile:
    #         teacher_id = user.teacher_profile.id
    # except:
    #     pass

    # Step 7: Get profile data based on user type
    profile_data = None
    try:
        log_auth_step("GET_PROFILE", f"Getting profile data",
                     email=user.email, user_type=str(user.user_type_enum))

        if user.user_type_enum == UserTypeEnum.STUDENT and student_id:
            log_auth_step("GET_PROFILE", f"Fetching student profile",
                         email=user.email, student_id=student_id)
            try:
                student_profile = await student_crud.get(db, id=student_id)
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
                    log_auth_step("GET_PROFILE", f"Student profile loaded successfully",
                                 email=user.email, student_name=f"{student_profile.first_name} {student_profile.last_name}")
                else:
                    log_auth_step("GET_PROFILE", f"Student profile not found",
                                 "warning", email=user.email, student_id=student_id)
            except Exception as student_error:
                log_auth_step("GET_PROFILE", f"Error fetching student profile: {str(student_error)}",
                             "error", email=user.email)

        elif user.user_type_enum == UserTypeEnum.TEACHER and teacher_id:
            log_auth_step("GET_PROFILE", f"Fetching teacher profile",
                         email=user.email, teacher_id=teacher_id)
            try:
                teacher_profile = await teacher_crud.get(db, id=teacher_id)
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
                    log_auth_step("GET_PROFILE", f"Teacher profile loaded successfully",
                                 email=user.email, teacher_name=f"{teacher_profile.first_name} {teacher_profile.last_name}")
                else:
                    log_auth_step("GET_PROFILE", f"Teacher profile not found",
                                 "warning", email=user.email, teacher_id=teacher_id)
            except Exception as teacher_error:
                log_auth_step("GET_PROFILE", f"Error fetching teacher profile: {str(teacher_error)}",
                             "error", email=user.email)
        else:
            log_auth_step("GET_PROFILE", f"No profile data needed",
                         email=user.email, user_type=str(user.user_type_enum))

    except Exception as profile_error:
        log_auth_step("GET_PROFILE", f"Error in profile data section: {str(profile_error)}",
                     "error", email=user.email)
        profile_data = None

    # Step 8: Create and return response
    try:
        log_auth_step("CREATE_RESPONSE", f"Creating login response", email=user.email)

        # Get student_id and teacher_id safely
        student_id = None
        teacher_id = None
        try:
            if hasattr(user, 'student_profile') and user.student_profile:
                student_id = user.student_profile.id
        except:
            pass
        try:
            if hasattr(user, 'teacher_profile') and user.teacher_profile:
                teacher_id = user.teacher_profile.id
        except:
            pass

        # Convert SQLAlchemy model to Pydantic schema
        user_dict = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "mobile": user.phone,
            "email": user.email,
            "user_type": user.user_type_enum,  # Return enum for API consistency
            "user_type_id": user.user_type_id,  # Add missing field
            "student_id": student_id,
            "teacher_id": teacher_id,
            "is_active": user.is_active,
            "is_verified": user.is_verified,  # Add missing field
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }

        response = UserLoginResponse(
            user=user_dict,
            access_token=access_token,
            token_type="bearer",
            permissions=permissions,
            profile_data=profile_data
        )
        log_auth_step("LOGIN_SUCCESS", f"Login completed successfully", email=user.email)
        return response
    except Exception as response_error:
        log_auth_step("CREATE_RESPONSE", f"Error creating login response: {str(response_error)}",
                     "error", email=user.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating login response: {str(response_error)}"
        )


@router.post("/register", response_model=UserSchema)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    User registration endpoint
    """
    # Initialize user_crud instance
    user_crud = CRUDUser()

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
    # Get linked profile data using relationships
    student_profile = None
    teacher_profile = None

    if current_user.user_type_enum == UserTypeEnum.STUDENT:
        # Find student by user_id
        student = await student_crud.get_by_user_id(db, user_id=current_user.id)
        if student:
            student_profile = student.__dict__

    if current_user.user_type_enum == UserTypeEnum.TEACHER:
        # Find teacher by user_id
        teacher = await teacher_crud.get_by_user_id(db, user_id=current_user.id)
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
    permissions = get_user_permissions(current_user.user_type_enum)
    dashboard_config = get_dashboard_permissions(current_user.user_type_enum)
    menu_items = filter_menu_items(current_user.user_type_enum)

    return {
        "user_type": current_user.user_type_enum,
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
            "mobile": current_user.phone,
            "user_type": current_user.user_type_enum,
            "last_login": current_user.last_login,
            "created_at": current_user.created_at
        }
    }

    # Add role-specific profile data
    if current_user.user_type_enum == UserTypeEnum.STUDENT and current_user.student_id:
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

    elif current_user.user_type_enum == UserTypeEnum.TEACHER:
        # Find teacher by user_id
        teacher = await teacher_crud.get_by_user_id(db, user_id=current_user.id)
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
