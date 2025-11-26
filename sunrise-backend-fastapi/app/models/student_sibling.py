from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class RelationshipTypeEnum(str, enum.Enum):
    SIBLING = "SIBLING"
    TWIN = "TWIN"
    HALF_SIBLING = "HALF_SIBLING"


class StudentSibling(Base):
    __tablename__ = "student_siblings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Student References
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    sibling_student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    
    # Relationship Details
    relationship_type = Column(String(20), default="SIBLING", nullable=False)
    is_auto_detected = Column(Boolean, default=True)
    
    # Birth Order and Fee Waiver
    birth_order = Column(Integer, nullable=False)
    fee_waiver_percentage = Column(DECIMAL(5, 2), default=0.00)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", foreign_keys=[student_id], backref="sibling_relationships")
    sibling = relationship("Student", foreign_keys=[sibling_student_id], backref="reverse_sibling_relationships")
    
    # Table constraints
    __table_args__ = (
        UniqueConstraint('student_id', 'sibling_student_id', name='uq_student_sibling_pair'),
        CheckConstraint('student_id != sibling_student_id', name='ck_different_students'),
        CheckConstraint('birth_order > 0', name='ck_birth_order_positive'),
        CheckConstraint('fee_waiver_percentage >= 0 AND fee_waiver_percentage <= 100', name='ck_waiver_percentage_range'),
        CheckConstraint("relationship_type IN ('SIBLING', 'TWIN', 'HALF_SIBLING')", name='ck_relationship_type'),
    )

    @property
    def waiver_description(self) -> str:
        """Get human-readable waiver description"""
        if self.fee_waiver_percentage == 0:
            return "No waiver"
        return f"{self.fee_waiver_percentage}% fee waiver"
    
    @property
    def birth_order_description(self) -> str:
        """Get human-readable birth order description"""
        if self.birth_order == 1:
            return "Eldest"
        elif self.birth_order == 2:
            return "2nd"
        elif self.birth_order == 3:
            return "3rd"
        else:
            return f"{self.birth_order}th"

