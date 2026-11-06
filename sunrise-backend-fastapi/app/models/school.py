"""
School (tenant) models.
"""
from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.tenant import TenantMixin


class SchoolStatus:
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


class School(Base):
    """A school served by the platform. Not tenant-scoped itself."""

    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(63), nullable=False, unique=True)  # subdomain label
    name = Column(String(255), nullable=False)
    short_name = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    logo_url = Column(Text, nullable=True)
    timezone = Column(String(64), nullable=False, default="Asia/Kolkata")
    currency = Column(String(3), nullable=False, default="INR")
    academic_year_start_month = Column(Integer, nullable=False, default=4)
    status = Column(String(20), nullable=False, default=SchoolStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def is_active(self) -> bool:
        return self.status == SchoolStatus.ACTIVE


class SchoolSetting(TenantMixin, Base):
    """Per-school key/value setting."""

    __tablename__ = "school_settings"
    __table_args__ = (UniqueConstraint("school_id", "key", name="school_settings_school_key_unique"),)

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
