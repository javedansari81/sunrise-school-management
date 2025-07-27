import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    PROJECT_NAME: str = "Sunrise Backend FastAPI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sunrise_school.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "e4e9c822b488b0c741e8616712b415c1")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "a436afdbaade6c5ae255289d8aa80103adbd4f622b4a99077bb40ac9140b8368a")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]


settings = Settings()
