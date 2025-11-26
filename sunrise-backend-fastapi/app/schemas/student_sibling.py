from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class RelationshipTypeEnum:
    SIBLING = "SIBLING"
    TWIN = "TWIN"
    HALF_SIBLING = "HALF_SIBLING"


class StudentSiblingBase(BaseModel):
    student_id: int = Field(..., description="Primary student ID")
    sibling_student_id: int = Field(..., description="Sibling student ID")
    relationship_type: str = Field(default="SIBLING", description="Type of relationship")
    is_auto_detected: bool = Field(default=True, description="Whether auto-detected or manually added")
    birth_order: int = Field(..., ge=1, description="Birth order among siblings")
    fee_waiver_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, description="Fee waiver percentage")
    is_active: bool = Field(default=True, description="Whether relationship is active")


class StudentSiblingCreate(BaseModel):
    sibling_student_id: int = Field(..., description="Sibling student ID to link")
    relationship_type: str = Field(default="SIBLING", description="Type of relationship")
    is_auto_detected: bool = Field(default=False, description="Whether auto-detected")


class StudentSiblingUpdate(BaseModel):
    relationship_type: Optional[str] = Field(None, description="Type of relationship")
    is_active: Optional[bool] = Field(None, description="Whether relationship is active")


class StudentSibling(StudentSiblingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        orm_mode = True


class SiblingStudentInfo(BaseModel):
    """Information about a sibling student"""
    id: int
    admission_number: str
    first_name: str
    last_name: str
    full_name: str
    class_name: str
    class_id: int
    section: Optional[str] = None
    date_of_birth: Optional[str] = None
    is_active: bool


class StudentSiblingWithDetails(BaseModel):
    """Sibling relationship with full student details"""
    id: int
    student_id: int
    sibling_student_id: int
    relationship_type: str
    is_auto_detected: bool
    birth_order: int
    fee_waiver_percentage: Decimal
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Sibling details
    sibling_info: SiblingStudentInfo
    
    # Computed fields
    waiver_description: str
    birth_order_description: str

    class Config:
        from_attributes = True
        orm_mode = True


class DetectedSibling(BaseModel):
    """Detected sibling during student creation/update"""
    student_id: int
    admission_number: str
    first_name: str
    last_name: str
    full_name: str
    class_name: str
    section: Optional[str] = None
    date_of_birth: Optional[str] = None
    matching_criteria: str  # e.g., "Same father name and phone"


class SiblingDetectionResult(BaseModel):
    """Result of sibling detection"""
    detected_siblings: List[DetectedSibling]
    total_siblings_count: int  # Including the current student
    current_student_birth_order: int
    calculated_waiver_percentage: Decimal
    waiver_reason: Optional[str] = None


class SiblingWaiverInfo(BaseModel):
    """Fee waiver information for a student based on siblings"""
    has_siblings: bool
    total_siblings_count: int
    birth_order: int
    birth_order_description: str
    fee_waiver_percentage: Decimal
    waiver_reason: Optional[str] = None
    siblings: List[StudentSiblingWithDetails]


class BulkSiblingLinkRequest(BaseModel):
    """Request to link multiple siblings at once"""
    sibling_student_ids: List[int] = Field(..., description="List of sibling student IDs to link")
    relationship_type: str = Field(default="SIBLING", description="Type of relationship")


class SiblingRecalculationResult(BaseModel):
    """Result of recalculating sibling waivers"""
    student_id: int
    previous_waiver_percentage: Decimal
    new_waiver_percentage: Decimal
    previous_birth_order: int
    new_birth_order: int
    total_siblings_count: int
    message: str

