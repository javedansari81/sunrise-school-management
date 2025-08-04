from pydantic import BaseModel, EmailStr, validator
from app.schemas.user import User
import re


class LoginRequest(BaseModel):
    email: str  # Changed from EmailStr to str to accept phone numbers
    password: str

    @validator('email')
    def validate_email_or_phone(cls, v):
        """Validate that the input is either a valid email or phone number"""
        if not v:
            raise ValueError('Email or phone number is required')

        # Check if it's a valid email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, v):
            return v

        # Check if it's a valid phone number (10 digits)
        phone_pattern = r'^\d{10}$'
        if re.match(phone_pattern, v):
            return v

        # If neither email nor phone, raise error
        raise ValueError('Must be a valid email address or 10-digit phone number')

    class Config:
        schema_extra = {
            "example": {
                "email": "student@example.com or 9876543210",
                "password": "password123"
            }
        }


class LoginResponse(BaseModel):
    access_token: str
    user: User


class Token(BaseModel):
    access_token: str
    token_type: str
