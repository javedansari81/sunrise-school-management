import os
import re
from typing import List, Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

_SCHEMA_RE = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")
# libpq sslmode values that require an encrypted connection
_SSL_REQUIRED = {"require", "verify-ca", "verify-full"}


def _normalize_db_url(url: str) -> str:
    # DigitalOcean and Heroku style URLs start with postgres://
    return "postgresql://" + url[len("postgres://"):] if url.startswith("postgres://") else url


def _split_sslmode(url: str):
    """Remove sslmode from a URL (asyncpg rejects it as a URL parameter) and return it separately."""
    parts = urlsplit(url)
    query = parse_qsl(parts.query, keep_blank_values=True)
    sslmode = next((v for k, v in query if k == "sslmode"), None)
    rest = [(k, v) for k, v in query if k != "sslmode"]
    return urlunsplit(parts._replace(query=urlencode(rest))), sslmode


class Settings:
    PROJECT_NAME: str = "Sunrise Backend FastAPI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = _normalize_db_url(os.getenv("DATABASE_URL", "sqlite:///./sunrise_school.db"))

    # PostgreSQL schema that holds every table of this application. The database
    # can be shared with other applications (for example warsi_db, which also
    # has the mart schema); this app only ever reads and writes this schema.
    DB_SCHEMA: str = os.getenv("DB_SCHEMA", "school").strip().lower()
    if not _SCHEMA_RE.match(DB_SCHEMA):
        raise ValueError(f"Invalid DB_SCHEMA {DB_SCHEMA!r}")

    # asyncpg does not accept ?sslmode=..., so it is split off and passed as ssl=
    ASYNCPG_DSN, _DB_SSLMODE = _split_sslmode(DATABASE_URL)
    DB_SSL: Optional[str] = "require" if (_DB_SSLMODE or "").lower() in _SSL_REQUIRED else None
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
    # Approved WhatsApp template SID for detailed fee receipt (school_fee_receipt_v3 - 13 variables)
    TWILIO_WHATSAPP_TEMPLATE_SID: str = os.getenv("TWILIO_WHATSAPP_TEMPLATE_SID", "")
    # Approved WhatsApp template SID for media receipt (school_fee_media_template_v4 - 3 variables)
    TWILIO_WHATSAPP_MEDIA_RECEIPT_SID: str = os.getenv("TWILIO_WHATSAPP_MEDIA_RECEIPT_SID", "")

    # Multi-tenancy: each school is served at <school code>.<BASE_DOMAIN>
    # BASE_DOMAIN example: "myschools.in". Leave empty until subdomains are live.
    BASE_DOMAIN: str = os.getenv("BASE_DOMAIN", "").strip().lower().lstrip(".")
    # School used when the request does not identify one (localhost, the current
    # single-domain deployment). Set to empty in production once subdomains are live
    # so that unidentified requests are rejected.
    DEFAULT_SCHOOL_CODE: str = os.getenv("DEFAULT_SCHOOL_CODE", "sunrise").strip().lower()
    # Subdomain labels that are never school codes
    RESERVED_SUBDOMAINS = frozenset(
        s.strip().lower()
        for s in os.getenv("RESERVED_SUBDOMAINS", "www,api,app,admin,platform").split(",")
        if s.strip()
    )

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
