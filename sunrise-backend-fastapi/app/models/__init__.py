# Models module
from .school import School, SchoolSetting
from .metadata import (
    UserType, SessionYear, Gender, Class, PaymentType, PaymentStatus, PaymentMethod,
    LeaveType, LeaveStatus, ExpenseCategory, ExpenseStatus, EmploymentStatus, Qualification
)
from .user import User
from .teacher import Teacher
from .student import Student
from .fee import FeeStructure, FeeRecord, FeePayment, MonthlyFeeTracking, MonthlyPaymentAllocation
from .leave import LeaveRequest, LeaveBalance, LeavePolicy, LeaveApprover
from .expense import Expense, Vendor, Budget, ExpenseReport
from .gallery import GalleryCategory, GalleryImage
from .inventory import InventoryItemType, InventorySizeType, InventoryPricing, InventoryPurchase, InventoryPurchaseItem
from .attendance import AttendanceStatus, AttendancePeriod, AttendanceRecord
from .alert import AlertType, AlertStatus, Alert
from .progression_action import ProgressionAction
from .student_session_history import StudentSessionHistory

__all__ = [
    # Metadata models
    "UserType", "SessionYear", "Gender", "Class",
    "PaymentType", "PaymentStatus", "PaymentMethod",
    "LeaveType", "LeaveStatus",
    "ExpenseCategory", "ExpenseStatus",
    "EmploymentStatus", "Qualification",
    "AttendanceStatus", "AttendancePeriod",
    "AlertType", "AlertStatus",
    "ProgressionAction",
    # Main models
    "User",
    "Teacher",
    "Student",
    "StudentSessionHistory",
    "FeeStructure",
    "FeeRecord",
    "FeePayment",
    "MonthlyFeeTracking",
    "MonthlyPaymentAllocation",
    "LeaveRequest",
    "LeaveBalance",
    "LeavePolicy",
    "LeaveApprover",
    "Expense",
    "Vendor",
    "Budget",
    "ExpenseReport",
    "GalleryCategory",
    "GalleryImage",
    "InventoryItemType",
    "InventorySizeType",
    "InventoryPricing",
    "InventoryPurchase",
    "InventoryPurchaseItem",
    "AttendanceRecord",
    "Alert"
]

# Unified fee module models live in their own package; importing them here
# registers them with SQLAlchemy whenever app.models is loaded.
from app.modules.fees import models as _unified_fee_models  # noqa: E402,F401
from app.modules.transport import models as _transport_ops_models  # noqa: E402,F401
