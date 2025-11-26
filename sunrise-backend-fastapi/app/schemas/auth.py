from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import User


class LoginRequest(BaseModel):
    email: EmailStr  # Only accept valid email addresses
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "password123"
            }
        }


class LoginResponse(BaseModel):
    access_token: str
    user: User


class Token(BaseModel):
    access_token: str
    token_type: str


class PasswordResetRequest(BaseModel):
    """Request schema for admin password reset"""
    reset_to_default: bool = Field(default=True, description="Reset password to default value")

    class Config:
        json_schema_extra = {
            "example": {
                "reset_to_default": True
            }
        }


class PasswordResetResponse(BaseModel):
    """Response schema for admin password reset"""
    success: bool
    message: str
    user_id: int
    email: str
    default_password: str
    user_name: str = Field(description="Full name of the user")
    user_type: str = Field(description="User type (ADMIN, TEACHER, STUDENT)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Password reset successfully",
                "user_id": 123,
                "email": "john.smith.1503@sunrise.com",
                "default_password": "Sunrise@001",
                "user_name": "John Smith",
                "user_type": "STUDENT"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Request schema for user password change"""
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=72,
        description="New password (6-72 characters)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "Sunrise@001",
                "new_password": "MyNewSecure@Pass123"
            }
        }


class ChangePasswordResponse(BaseModel):
    """Response schema for password change"""
    success: bool
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Password changed successfully"
            }
        }
