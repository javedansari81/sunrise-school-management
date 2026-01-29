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

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

    # Twilio WhatsApp Configuration
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "")
    # Approved WhatsApp template SID for fee receipt notifications
    TWILIO_WHATSAPP_TEMPLATE_SID: str = os.getenv("TWILIO_WHATSAPP_TEMPLATE_SID", "")

    # CORS Origins - Support both environment variable and defaults
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "")
        if cors_origins:
            # Split by comma and strip whitespace
            origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
            # Add localhost for development
            origins.extend(["http://localhost:3000", "http://localhost:8080"])
            return origins
        else:
            # Default origins for development
            return ["http://localhost:3000", "http://localhost:8080"]


settings = Settings()
