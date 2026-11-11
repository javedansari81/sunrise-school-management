"""Fixed values of the unified fee module. They match the CHECK constraints in Database/Tables/T900-T950."""
from enum import Enum


class FeeHeadCategory(str, Enum):
    ACADEMIC = "ACADEMIC"
    TRANSPORT = "TRANSPORT"
    ONE_TIME = "ONE_TIME"
    PENALTY = "PENALTY"
    OTHER = "OTHER"


class Frequency(str, Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    HALF_YEARLY = "HALF_YEARLY"
    ANNUAL = "ANNUAL"
    ONE_TIME = "ONE_TIME"


# Months between two billings, counted from the session start month
FREQUENCY_STEP = {
    Frequency.MONTHLY: 1,
    Frequency.QUARTERLY: 3,
    Frequency.HALF_YEARLY: 6,
    Frequency.ANNUAL: 12,
    Frequency.ONE_TIME: 12,
}


class StructureStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class AppliesTo(str, Enum):
    ALL = "ALL"
    NEW_STUDENTS = "NEW_STUDENTS"
    EXISTING_STUDENTS = "EXISTING_STUDENTS"


class PlanSource(str, Enum):
    CLASS = "CLASS"
    TRANSPORT = "TRANSPORT"
    MANUAL = "MANUAL"


class ConcessionType(str, Enum):
    SIBLING = "SIBLING"
    STAFF = "STAFF"
    SCHOLARSHIP = "SCHOLARSHIP"
    CUSTOM = "CUSTOM"


class ValueType(str, Enum):
    PERCENT = "PERCENT"
    FIXED = "FIXED"


class PositionBasis(str, Enum):
    ELDEST = "ELDEST"
    YOUNGEST = "YOUNGEST"


class DueLineType(str, Enum):
    REGULAR = "REGULAR"
    LATE_FEE = "LATE_FEE"
    ADJUSTMENT = "ADJUSTMENT"
    MANUAL = "MANUAL"


class DueStatus(str, Enum):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    WAIVED = "WAIVED"


OPEN_DUE_STATUSES = (DueStatus.PENDING.value, DueStatus.PARTIAL.value)


class PaymentKind(str, Enum):
    PAYMENT = "PAYMENT"
    REVERSAL = "REVERSAL"


# Fee head codes the system relies on
HEAD_TRANSPORT = "TRANSPORT"
HEAD_LATE_FEE = "LATE_FEE"
SYSTEM_HEAD_CODES = (HEAD_TRANSPORT, HEAD_LATE_FEE)

# school_settings keys
SETTING_RECEIPT_PREFIX = "fee.receipt_prefix"
SETTING_LATE_FEE_ENABLED = "fee.late_fee.enabled"
SETTING_LATE_FEE_MODE = "fee.late_fee.mode"
SETTING_LATE_FEE_VALUE = "fee.late_fee.value"
SETTING_LATE_FEE_GRACE_DAYS = "fee.late_fee.grace_days"
SETTING_TRANSPORT_CUTOFF_DAY = "fee.transport.cutoff_day"


class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    PUBLISH = "PUBLISH"
    ARCHIVE = "ARCHIVE"
    GENERATE = "GENERATE"
    CANCEL = "CANCEL"
    WAIVE = "WAIVE"
    PAY = "PAY"
    REVERSE = "REVERSE"
    APPLY_CREDIT = "APPLY_CREDIT"
    RECEIPT = "RECEIPT"
