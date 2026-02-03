"""
ProgressionAction model for session progression metadata
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProgressionAction(Base):
    """
    Metadata table for progression action types.
    Similar to alert_types, this stores the different types of progression actions
    that can be applied to students during session progression.
    """
    __tablename__ = "progression_actions"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, default=0)
    icon = Column(String(50), nullable=True)  # Material UI icon name
    color_code = Column(String(10), nullable=True)  # Hex color code
    is_positive = Column(Boolean, default=True)  # TRUE for positive actions (PROMOTED)
    creates_new_session = Column(Boolean, default=True)  # TRUE if action creates entry in new session
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    session_histories = relationship("StudentSessionHistory", back_populates="progression_action")

    def __repr__(self):
        return f"<ProgressionAction(id={self.id}, name='{self.name}')>"

