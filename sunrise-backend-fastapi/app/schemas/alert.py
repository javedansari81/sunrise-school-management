"""
Pydantic schemas for alert/notification system
Matches database schema in T800_alert_types.sql, T805_alert_statuses.sql, T810_alerts.sql
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# Enums for API validation
class AlertCategoryEnum(str, Enum):
    """Alert category options"""
    LEAVE_MANAGEMENT = "LEAVE_MANAGEMENT"
    FINANCIAL = "FINANCIAL"
    ACADEMIC = "ACADEMIC"
    ADMINISTRATIVE = "ADMINISTRATIVE"
    SYSTEM = "SYSTEM"


class AlertEntityTypeEnum(str, Enum):
    """Alert entity type options"""
    LEAVE_REQUEST = "LEAVE_REQUEST"
    FEE_PAYMENT = "FEE_PAYMENT"
    TRANSPORT_PAYMENT = "TRANSPORT_PAYMENT"
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    ATTENDANCE = "ATTENDANCE"
    INVENTORY = "INVENTORY"


class ActorTypeEnum(str, Enum):
    """Actor type options"""
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"


class TargetRoleEnum(str, Enum):
    """Target role options"""
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"


# Metadata response schemas
class AlertTypeResponse(BaseModel):
    """Alert type metadata response"""
    id: int
    name: str
    description: Optional[str] = None
    category: str
    icon: Optional[str] = None
    color_code: Optional[str] = None
    priority_level: int
    default_expiry_days: int
    requires_acknowledgment: bool
    is_active: bool

    class Config:
        from_attributes = True


class AlertStatusResponse(BaseModel):
    """Alert status metadata response"""
    id: int
    name: str
    description: Optional[str] = None
    color_code: Optional[str] = None
    is_final: bool
    is_active: bool

    class Config:
        from_attributes = True


# Alert schemas
class AlertBase(BaseModel):
    """Base schema for alerts"""
    title: str = Field(..., max_length=255, description="Alert title")
    message: str = Field(..., description="Alert message")
    entity_type: str = Field(..., max_length=50, description="Type of entity affected")
    entity_id: int = Field(..., description="ID of the affected entity")
    entity_display_name: Optional[str] = Field(None, max_length=255, description="Display name of entity")
    target_role: Optional[str] = Field(None, max_length=20, description="Target role: ADMIN, TEACHER, STUDENT")
    target_user_id: Optional[int] = Field(None, description="Specific target user ID")
    alert_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    priority_level: Optional[int] = Field(2, description="Priority: 1=Low, 2=Normal, 3=High, 4=Critical")


class AlertCreate(AlertBase):
    """Schema for creating alerts (internal use by services)"""
    alert_type_id: int = Field(..., description="Alert type ID from metadata")
    actor_user_id: Optional[int] = Field(None, description="User ID who triggered the action")
    actor_type: Optional[str] = Field(None, max_length=20, description="Actor type: STUDENT, TEACHER, ADMIN, SYSTEM")
    actor_name: Optional[str] = Field(None, max_length=200, description="Actor name for display")
    expires_at: Optional[datetime] = Field(None, description="Alert expiration datetime")


class AlertUpdate(BaseModel):
    """Schema for updating alert status"""
    alert_status_id: Optional[int] = Field(None, description="New status ID from metadata")


class AlertResponse(BaseModel):
    """Full alert response"""
    id: int
    alert_type_id: int
    alert_status_id: int
    title: str
    message: str
    entity_type: str
    entity_id: int
    entity_display_name: Optional[str] = None
    target_role: Optional[str] = None
    target_user_id: Optional[int] = None
    alert_metadata: Optional[Dict[str, Any]] = None
    priority_level: int
    actor_user_id: Optional[int] = None
    actor_type: Optional[str] = None
    actor_name: Optional[str] = None
    read_at: Optional[datetime] = None
    read_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[int] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Enriched fields from relationships
    alert_type_name: Optional[str] = None
    alert_type_icon: Optional[str] = None
    alert_type_color: Optional[str] = None
    alert_type_category: Optional[str] = None
    alert_status_name: Optional[str] = None
    alert_status_color: Optional[str] = None

    class Config:
        from_attributes = True


class AlertWithDetails(AlertResponse):
    """Alert with full metadata details"""
    alert_type: Optional[AlertTypeResponse] = None
    alert_status: Optional[AlertStatusResponse] = None


class AlertListResponse(BaseModel):
    """Paginated alert list response"""
    alerts: List[AlertResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
    unread_count: int


class AlertFilters(BaseModel):
    """Filter parameters for alert queries"""
    alert_type_id: Optional[int] = None
    alert_status_id: Optional[int] = None
    category: Optional[str] = None
    entity_type: Optional[str] = None
    target_role: Optional[str] = None
    priority_level: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    is_read: Optional[bool] = None


class AlertStats(BaseModel):
    """Alert statistics for dashboard"""
    total_alerts: int
    unread_count: int
    by_category: Dict[str, int]
    by_priority: Dict[str, int]
    recent_count: int  # Last 24 hours


class AlertUnreadCountResponse(BaseModel):
    """Unread count response"""
    unread_count: int


class AlertActionResponse(BaseModel):
    """Response for alert actions (mark read, acknowledge, etc.)"""
    message: str
    alert_id: Optional[int] = None
    count: Optional[int] = None
