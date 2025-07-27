from pydantic import BaseModel, EmailStr
from app.schemas.user import User


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    user: User


class Token(BaseModel):
    access_token: str
    token_type: str
