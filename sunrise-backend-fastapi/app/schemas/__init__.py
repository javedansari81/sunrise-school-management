# Schemas module
from .user import User, UserCreate, UserUpdate, UserInDB
from .teacher import Teacher, TeacherCreate, TeacherUpdate
from .auth import LoginRequest, LoginResponse, Token
from .student import Student, StudentCreate, StudentUpdate
from .fee import (
    FeeStructure, FeeStructureCreate, FeeStructureUpdate,
    FeeRecord, FeeRecordCreate, FeeRecordUpdate,
    FeePayment, FeePaymentCreate, FeePaymentUpdate
)
from .leave import LeaveRequest, LeaveRequestCreate, LeaveRequestUpdate
from .expense import Expense, ExpenseCreate, ExpenseUpdate
from .gallery import (
    GalleryCategoryResponse, GalleryCategoryCreate, GalleryCategoryUpdate,
    GalleryImageResponse, GalleryImageCreate, GalleryImageUpdate,
    GalleryImageWithCategory, GalleryImageUploadRequest,
    GalleryImageToggleHomePageRequest, GalleryConfigurationResponse
)
from .report import (
    StudentUDISEData, UDISEReportResponse, UDISEReportFilters,
    FeeTrackingData, FeeTrackingReportResponse, FeeTrackingReportFilters
)
from .inventory import (
    InventoryPricingCreate, InventoryPricingUpdate, InventoryPricingResponse,
    InventoryPurchaseCreate, InventoryPurchaseUpdate, InventoryPurchaseResponse,
    InventoryPurchaseListResponse, StudentInventorySummary, InventoryStatistics
)
from .session_progression import (
    ProgressionActionResponse,
    StudentProgressionPreviewRequest, StudentProgressionPreviewItem,
    StudentProgressionPreviewResponse, StudentProgressionItem,
    BulkProgressionRequest, BulkProgressionResultItem, BulkProgressionResponse,
    StudentProgressionHistoryItem, StudentProgressionHistoryResponse,
    RollbackRequest, RollbackResponse,
    ProgressionReportRequest, ProgressionStatsByAction, ProgressionStatsByClass,
    ProgressionReportResponse
)

__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "Teacher",
    "TeacherCreate",
    "TeacherUpdate",
    "Student",
    "StudentCreate",
    "StudentUpdate",
    "FeeStructure",
    "FeeStructureCreate",
    "FeeStructureUpdate",
    "FeeRecord",
    "FeeRecordCreate",
    "FeeRecordUpdate",
    "FeePayment",
    "FeePaymentCreate",
    "FeePaymentUpdate",
    "LeaveRequest",
    "LeaveRequestCreate",
    "LeaveRequestUpdate",
    "Expense",
    "ExpenseCreate",
    "ExpenseUpdate",
    "LoginRequest",
    "LoginResponse",
    "Token",
    "GalleryCategoryResponse",
    "GalleryCategoryCreate",
    "GalleryCategoryUpdate",
    "GalleryImageResponse",
    "GalleryImageCreate",
    "GalleryImageUpdate",
    "GalleryImageWithCategory",
    "GalleryImageUploadRequest",
    "GalleryImageToggleHomePageRequest",
    "GalleryConfigurationResponse",
    "StudentUDISEData",
    "UDISEReportResponse",
    "UDISEReportFilters",
    "FeeTrackingData",
    "FeeTrackingReportResponse",
    "FeeTrackingReportFilters",
    "InventoryPricingCreate",
    "InventoryPricingUpdate",
    "InventoryPricingResponse",
    "InventoryPurchaseCreate",
    "InventoryPurchaseUpdate",
    "InventoryPurchaseResponse",
    "InventoryPurchaseListResponse",
    "StudentInventorySummary",
    "InventoryStatistics",
    # Session Progression
    "ProgressionActionResponse",
    "StudentProgressionPreviewRequest",
    "StudentProgressionPreviewItem",
    "StudentProgressionPreviewResponse",
    "StudentProgressionItem",
    "BulkProgressionRequest",
    "BulkProgressionResultItem",
    "BulkProgressionResponse",
    "StudentProgressionHistoryItem",
    "StudentProgressionHistoryResponse",
    "RollbackRequest",
    "RollbackResponse",
    "ProgressionReportRequest",
    "ProgressionStatsByAction",
    "ProgressionStatsByClass",
    "ProgressionReportResponse"
]
