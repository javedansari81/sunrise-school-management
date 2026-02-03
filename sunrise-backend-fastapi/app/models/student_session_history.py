"""
StudentSessionHistory model for tracking student progression across sessions
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class StudentSessionHistory(Base):
    """
    Tracks student progression history across academic session years.
    Records how a student moved from one session to another (promoted, retained, etc.)
    """
    __tablename__ = "student_session_history"

    id = Column(Integer, primary_key=True, index=True)

    # Student and Session Reference
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)

    # Session-Specific Academic Info
    section = Column(String(10), nullable=True)
    roll_number = Column(String(20), nullable=True)

    # Progression Details (references metadata table)
    progression_action_id = Column(Integer, ForeignKey("progression_actions.id"), nullable=False)
    from_session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=True)
    from_class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)

    # Batch Tracking (for bulk operations and rollback)
    progression_batch_id = Column(String(50), nullable=True, index=True)

    # Audit Fields
    progressed_at = Column(DateTime(timezone=True), server_default=func.now())
    progressed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    remarks = Column(Text, nullable=True)

    # Optional: Snapshot of student data at time of progression
    snapshot_data = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="session_histories")
    session_year = relationship("SessionYear", foreign_keys=[session_year_id])
    class_ref = relationship("Class", foreign_keys=[class_id])
    progression_action = relationship("ProgressionAction", back_populates="session_histories")
    from_session_year = relationship("SessionYear", foreign_keys=[from_session_year_id])
    from_class = relationship("Class", foreign_keys=[from_class_id])
    progressed_by_user = relationship("User", foreign_keys=[progressed_by])

    def __repr__(self):
        return f"<StudentSessionHistory(id={self.id}, student_id={self.student_id}, session_year_id={self.session_year_id})>"

