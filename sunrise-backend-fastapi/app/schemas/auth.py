from pydantic import BaseModel, EmailStr
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
