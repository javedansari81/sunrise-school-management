"""
Alert/Notification models for the school management system
Follows metadata-driven architecture pattern
Matches database schema in T800_alert_types.sql, T805_alert_statuses.sql, T810_alerts.sql
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AlertType(Base):
    """
    Alert type metadata table
    Stores alert type definitions (LEAVE_REQUEST_CREATED, FEE_PAYMENT_RECEIVED, etc.)
    """
    __tablename__ = "alert_types"

    id = Column(Integer, primary_key=True)  # Non-auto-increment (manually assigned)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(50), nullable=False)
    icon = Column(String(50))
    color_code = Column(String(10))
    priority_level = Column(Integer, default=1)
    default_expiry_days = Column(Integer, default=30)
    requires_acknowledgment = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    alerts = relationship("Alert", back_populates="alert_type")


class AlertStatus(Base):
    """
    Alert status metadata table
    Stores alert status options (UNREAD, READ, ACKNOWLEDGED, DISMISSED, EXPIRED)
    """
    __tablename__ = "alert_statuses"

    id = Column(Integer, primary_key=True)  # Non-auto-increment (manually assigned)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    color_code = Column(String(10))
    is_final = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    alerts = relationship("Alert", back_populates="alert_status")


class Alert(Base):
    """
    Main alert/notification table
    Stores all system alerts/notifications with actor, entity, and target information
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    # Alert Classification (FK to metadata)
    alert_type_id = Column(Integer, ForeignKey("alert_types.id"), nullable=False)
    alert_status_id = Column(Integer, ForeignKey("alert_statuses.id"), default=1)

    # Alert Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Actor Information (who triggered the alert)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    actor_type = Column(String(20))  # 'STUDENT', 'TEACHER', 'ADMIN', 'SYSTEM'
    actor_name = Column(String(200))  # Denormalized for display efficiency

    # Entity Information (what entity was affected)
    entity_type = Column(String(50), nullable=False)  # 'LEAVE_REQUEST', 'FEE_PAYMENT', etc.
    entity_id = Column(Integer, nullable=False)
    entity_display_name = Column(String(255))  # Denormalized for display efficiency

    # Target Audience
    target_role = Column(String(20))  # 'ADMIN', 'TEACHER', 'STUDENT', NULL=all roles
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Additional Context (JSON for extensibility)
    alert_metadata = Column(JSON, default={})

    # Priority & Timing
    priority_level = Column(Integer, default=2)  # 1=Low, 2=Normal, 3=High, 4=Critical
    expires_at = Column(DateTime(timezone=True))

    # Read/Acknowledgment Tracking
    read_at = Column(DateTime(timezone=True))
    read_by = Column(Integer, ForeignKey("users.id"))
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledged_by = Column(Integer, ForeignKey("users.id"))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Soft Delete
    is_deleted = Column(Boolean, default=False)
    deleted_date = Column(DateTime(timezone=True))

    # Relationships
    alert_type = relationship("AlertType", back_populates="alerts")
    alert_status = relationship("AlertStatus", back_populates="alerts")
    actor = relationship("User", foreign_keys=[actor_user_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
    reader = relationship("User", foreign_keys=[read_by])
    acknowledger = relationship("User", foreign_keys=[acknowledged_by])

