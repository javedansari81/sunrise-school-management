"""
Pydantic schemas for Session Progression feature
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date


# =====================================================
# Progression Action Schemas (Metadata)
# =====================================================

class ProgressionActionResponse(BaseModel):
    """Response schema for progression action metadata"""
    id: int
    name: str
    description: Optional[str] = None
    display_order: int = 0
    icon: Optional[str] = None
    color_code: Optional[str] = None
    is_positive: bool = True
    creates_new_session: bool = True
    is_active: bool = True

    class Config:
        from_attributes = True


# =====================================================
# Student Progression Preview Schemas
# =====================================================

class StudentProgressionPreviewRequest(BaseModel):
    """Request schema for previewing students eligible for progression"""
    from_session_year_id: int = Field(..., description="Current session year ID")
    to_session_year_id: int = Field(..., description="Target session year ID")
    class_ids: Optional[List[int]] = Field(None, description="Filter by specific class IDs")


class StudentProgressionPreviewItem(BaseModel):
    """Individual student in progression preview"""
    student_id: int
    admission_number: str
    first_name: str
    last_name: str
    current_class_id: int
    current_class_name: str
    current_section: Optional[str] = None
    current_roll_number: Optional[str] = None
    suggested_action_id: int = Field(default=2, description="Default to PROMOTED (2)")
    suggested_action_name: str = "PROMOTED"
    target_class_id: Optional[int] = None
    target_class_name: Optional[str] = None


class StudentProgressionPreviewResponse(BaseModel):
    """Response schema for progression preview"""
    from_session_year_id: int
    from_session_year_name: str
    to_session_year_id: int
    to_session_year_name: str
    total_students: int
    students: List[StudentProgressionPreviewItem]


# =====================================================
# Bulk Progression Request/Response Schemas
# =====================================================

class StudentProgressionItem(BaseModel):
    """Individual student progression action"""
    student_id: int
    progression_action_id: int = Field(..., description="ID from progression_actions table")
    target_class_id: Optional[int] = Field(None, description="Target class ID (required for PROMOTED/DEMOTED)")
    target_section: Optional[str] = None
    target_roll_number: Optional[str] = None
    remarks: Optional[str] = None


class BulkProgressionRequest(BaseModel):
    """Request schema for bulk student progression"""
    from_session_year_id: int
    to_session_year_id: int
    students: List[StudentProgressionItem]


class BulkProgressionResultItem(BaseModel):
    """Result for individual student progression"""
    student_id: int
    admission_number: str
    student_name: str
    success: bool
    progression_action_id: Optional[int] = None
    progression_action_name: Optional[str] = None
    from_class_name: Optional[str] = None
    to_class_name: Optional[str] = None
    error_message: Optional[str] = None


class BulkProgressionResponse(BaseModel):
    """Response schema for bulk progression"""
    batch_id: str
    from_session_year_id: int
    to_session_year_id: int
    total_processed: int
    successful_count: int
    failed_count: int
    results: List[BulkProgressionResultItem]


# =====================================================
# Progression History Schemas
# =====================================================

class StudentProgressionHistoryItem(BaseModel):
    """Individual history item for a student"""
    id: int
    session_year_id: int
    session_year_name: str
    class_id: int
    class_name: str
    section: Optional[str] = None
    roll_number: Optional[str] = None
    progression_action_id: int
    progression_action_name: str
    progression_action_icon: Optional[str] = None
    progression_action_color: Optional[str] = None
    from_session_year_id: Optional[int] = None
    from_session_year_name: Optional[str] = None
    from_class_id: Optional[int] = None
    from_class_name: Optional[str] = None
    progressed_at: datetime
    progressed_by_name: str
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class StudentProgressionHistoryResponse(BaseModel):
    """Response schema for student progression history"""
    student_id: int
    admission_number: str
    student_name: str
    original_session_year_id: Optional[int] = None
    original_session_year_name: Optional[str] = None
    original_class_id: Optional[int] = None
    original_class_name: Optional[str] = None
    history: List[StudentProgressionHistoryItem]


# =====================================================
# Rollback Schemas
# =====================================================

class RollbackRequest(BaseModel):
    """Request schema for rolling back a progression batch"""
    batch_id: str = Field(..., description="The progression batch ID to rollback")
    reason: Optional[str] = Field(None, description="Reason for rollback")


class RollbackResponse(BaseModel):
    """Response schema for rollback operation"""
    batch_id: str
    students_affected: int
    success: bool
    message: str


# =====================================================
# Progression Report Schemas
# =====================================================

class ProgressionReportRequest(BaseModel):
    """Request schema for progression report"""
    session_year_id: int
    class_ids: Optional[List[int]] = None


class ProgressionStatsByAction(BaseModel):
    """Statistics by progression action"""
    action_id: int
    action_name: str
    action_icon: Optional[str] = None
    action_color: Optional[str] = None
    count: int


class ProgressionStatsByClass(BaseModel):
    """Statistics by class"""
    class_id: int
    class_name: str
    total_students: int
    promoted_count: int
    retained_count: int
    demoted_count: int
    graduated_count: int
    transferred_out_count: int
    withdrawn_count: int


class ProgressionReportResponse(BaseModel):
    """Response schema for progression report"""
    session_year_id: int
    session_year_name: str
    total_students_progressed: int
    by_action: List[ProgressionStatsByAction]
    by_class: List[ProgressionStatsByClass]
    generated_at: datetime
