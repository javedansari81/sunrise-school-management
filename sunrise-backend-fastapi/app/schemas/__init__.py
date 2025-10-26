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
    "GalleryConfigurationResponse"
]
