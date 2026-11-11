"""Request and response models of the unified fee module."""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from typing_extensions import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.fees.constants import (
    AppliesTo, ConcessionType, FeeHeadCategory, Frequency, PositionBasis, ValueType,
)

Money = Decimal
# Amount sent by a client: not negative, at most 2 decimal places
MoneyIn = Annotated[Decimal, Field(ge=0, max_digits=10, decimal_places=2)]
Percent = Annotated[Decimal, Field(gt=0, le=100, max_digits=5, decimal_places=2)]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Fee heads
# ---------------------------------------------------------------------------

class FeeHeadCreate(BaseModel):
    code: str = Field(min_length=1, max_length=30, pattern=r"^[A-Z0-9_]+$")
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    category: FeeHeadCategory = FeeHeadCategory.ACADEMIC
    default_frequency: Frequency = Frequency.MONTHLY
    sort_order: int = 0
    is_active: bool = True


class FeeHeadUpdate(BaseModel):
    code: Optional[str] = Field(default=None, min_length=1, max_length=30, pattern=r"^[A-Z0-9_]+$")
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[FeeHeadCategory] = None
    default_frequency: Optional[Frequency] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class FeeHeadOut(ORM):
    id: int
    code: str
    name: str
    description: Optional[str]
    category: str
    default_frequency: str
    is_system: bool
    sort_order: int
    is_active: bool


# ---------------------------------------------------------------------------
# Fee structures
# ---------------------------------------------------------------------------

class FeeStructureItemIn(BaseModel):
    fee_head_id: int
    class_id: Optional[int] = None
    amount: MoneyIn
    frequency: Frequency = Frequency.MONTHLY
    billing_months: Optional[List[int]] = None
    due_day: int = Field(default=10, ge=1, le=28)
    applies_to: AppliesTo = AppliesTo.ALL


class FeeStructureItemOut(ORM):
    id: int
    fee_head_id: int
    class_id: Optional[int]
    amount: Money
    frequency: str
    billing_months: Optional[List[int]]
    due_day: int
    applies_to: str


class FeeStructureCreate(BaseModel):
    session_year_id: int
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None
    items: List[FeeStructureItemIn] = []


class FeeStructureUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = None


class FeeStructureCopy(BaseModel):
    session_year_id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)


class FeeStructureSummary(ORM):
    id: int
    session_year_id: int
    name: str
    description: Optional[str]
    status: str
    copied_from_id: Optional[int]
    published_at: Optional[datetime]
    published_by: Optional[int]
    created_at: Optional[datetime]


class FeeStructureOut(FeeStructureSummary):
    items: List[FeeStructureItemOut]


# ---------------------------------------------------------------------------
# Concessions
# ---------------------------------------------------------------------------

class SiblingTier(BaseModel):
    """
    Which children of a family of a given size get how much off. Positions count
    the student's enrolled siblings ordered eldest first by date of birth, from
    the eldest (ELDEST) or from the youngest (YOUNGEST); 1 is the eldest or youngest.
    """
    min_siblings: int = Field(ge=2)
    max_siblings: Optional[int] = Field(default=None, ge=2)
    position_basis: PositionBasis = PositionBasis.ELDEST
    position_from: int = Field(ge=1)
    position_to: Optional[int] = Field(default=None, ge=1)
    percent: Percent

    @model_validator(mode="after")
    def _ranges(self):
        if self.max_siblings is not None and self.max_siblings < self.min_siblings:
            raise ValueError("max_siblings must not be below min_siblings")
        if self.position_to is not None and self.position_to < self.position_from:
            raise ValueError("position_to must not be below position_from")
        return self


class ConcessionRuleBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    value_type: ValueType = ValueType.PERCENT
    value: MoneyIn = Decimal("0")
    fee_head_ids: Optional[List[int]] = None
    tiers: Optional[List[SiblingTier]] = None
    is_active: bool = True


class ConcessionRuleCreate(ConcessionRuleBase):
    concession_type: ConcessionType

    @model_validator(mode="after")
    def _shape(self):
        if self.concession_type == ConcessionType.SIBLING:
            if not self.tiers:
                raise ValueError("a SIBLING rule needs tiers")
        else:
            if self.tiers:
                raise ValueError("only SIBLING rules have tiers")
            if self.value_type == ValueType.PERCENT and self.value > 100:
                raise ValueError("a percent must be 0 to 100")
        return self


class ConcessionRuleUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    value_type: Optional[ValueType] = None
    value: Optional[MoneyIn] = None
    fee_head_ids: Optional[List[int]] = None
    tiers: Optional[List[SiblingTier]] = None
    is_active: Optional[bool] = None


class ConcessionRuleOut(ORM):
    id: int
    name: str
    description: Optional[str]
    concession_type: str
    value_type: str
    value: Money
    fee_head_ids: Optional[List[int]]
    tiers: Optional[list]
    is_active: bool


class StudentConcessionCreate(BaseModel):
    session_year_id: int
    concession_rule_id: Optional[int] = None
    concession_type: Optional[ConcessionType] = None
    value_type: Optional[ValueType] = None
    value: Optional[MoneyIn] = None
    fee_head_ids: Optional[List[int]] = None
    start_period: Optional[date] = None
    end_period: Optional[date] = None
    reason: str = Field(min_length=1)


class StudentConcessionOut(ORM):
    id: int
    student_id: int
    session_year_id: int
    concession_rule_id: Optional[int]
    concession_type: str
    value_type: str
    value: Money
    fee_head_ids: Optional[List[int]]
    start_period: Optional[date]
    end_period: Optional[date]
    reason: str
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    is_active: bool


class SiblingConcessionPreview(BaseModel):
    student_id: int
    session_year_id: int
    family_size: int
    position_from_eldest: int
    position_from_youngest: int
    sibling_ids_eldest_first: List[int]
    rule_id: Optional[int]
    fee_head_ids: Optional[List[int]]
    percent: Decimal


class RevokeRequest(BaseModel):
    reason: Optional[str] = None


# ---------------------------------------------------------------------------
# Plans
# ---------------------------------------------------------------------------

class PlanBuildRequest(BaseModel):
    session_year_id: int
    class_id: Optional[int] = None
    student_ids: Optional[List[int]] = None
    effective_from: Optional[date] = None


class PlanBuildResult(BaseModel):
    session_year_id: int
    fee_structure_id: int
    students: int
    created: int
    unchanged: int
    replaced: int
    ended: int
    dues_cancelled: int
    effective_from: Optional[date] = None


class PlanLineCreate(BaseModel):
    session_year_id: int
    fee_head_id: int
    amount: MoneyIn
    frequency: Frequency = Frequency.ONE_TIME
    billing_months: Optional[List[int]] = None
    due_day: int = Field(default=10, ge=1, le=28)
    start_period: Optional[date] = None
    end_period: Optional[date] = None
    remarks: Optional[str] = None


class PlanLineEnd(BaseModel):
    last_period: Optional[date] = None
    reason: Optional[str] = None


class PlanLineOut(ORM):
    id: int
    student_id: int
    session_year_id: int
    fee_head_id: int
    amount: Money
    frequency: str
    billing_months: Optional[List[int]]
    due_day: int
    start_period: date
    end_period: Optional[date]
    source: str
    source_ref_id: Optional[int]
    is_active: bool
    remarks: Optional[str]


# ---------------------------------------------------------------------------
# Dues
# ---------------------------------------------------------------------------

class DuesGenerateRequest(BaseModel):
    session_year_id: int
    class_id: Optional[int] = None
    student_id: Optional[int] = None
    through_period: Optional[date] = None


class DuesGenerateResult(BaseModel):
    session_year_id: int
    through_period: date
    students: int
    created: int
    repriced: int
    total_amount: Money
    late_fees: int = 0
    credit_applied: Money = Decimal("0")


class DueOut(ORM):
    id: int
    student_id: int
    session_year_id: int
    fee_head_id: int
    student_fee_plan_id: Optional[int]
    line_type: str
    related_due_id: Optional[int]
    period: date
    due_date: date
    description: Optional[str]
    gross_amount: Money
    concession_amount: Money
    net_amount: Money
    paid_amount: Money
    balance: Money
    status: str
    cancel_reason: Optional[str]


class DueCancel(BaseModel):
    reason: str = Field(min_length=1)


class LateFeeRequest(BaseModel):
    as_of: Optional[date] = None
    session_year_id: Optional[int] = None


class LateFeeResult(BaseModel):
    enabled: bool
    as_of: date
    created: int
    total_amount: Money


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

class AllocationIn(BaseModel):
    due_id: int
    amount: MoneyIn


class PaymentCreate(BaseModel):
    """
    Money received from a student. Allocation, in order of precedence:
    `allocations` (exact amounts per due), else `due_ids` (fill these dues in
    this order), else oldest due date first. Whatever is left is credit, used
    automatically for the student's next dues.
    """
    student_id: int
    session_year_id: Optional[int] = None
    amount: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
    payment_method_id: int
    payment_date: Optional[date] = None
    transaction_id: Optional[str] = Field(default=None, max_length=100)
    remarks: Optional[str] = None
    due_ids: Optional[List[int]] = None
    allocations: Optional[List[AllocationIn]] = None
    send_receipt: bool = Field(
        default=False, description="After saving, upload the receipt PDF and send it on WhatsApp (in the background)")


class ReversalCreate(BaseModel):
    """Reverse a payment, fully (no amount) or partly. Unallocated credit is taken back first."""
    amount: Optional[Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]] = None
    reversal_reason_id: int
    remarks: Optional[str] = None


class AllocationOut(ORM):
    id: int
    payment_id: int
    student_due_id: int
    amount: Money
    is_reversal: bool
    reversal_payment_id: Optional[int]


class PaymentOut(ORM):
    id: int
    student_id: int
    session_year_id: int
    kind: str
    receipt_number: Optional[str]
    amount: Money
    payment_method_id: Optional[int]
    payment_date: date
    transaction_id: Optional[str]
    remarks: Optional[str]
    reverses_payment_id: Optional[int]
    reversal_reason_id: Optional[int]
    receipt_url: Optional[str]
    created_by: Optional[int]
    created_at: Optional[datetime]
    allocations: List[AllocationOut] = []
    reversal_allocations: List[AllocationOut] = []


class PaymentDetail(PaymentOut):
    allocated: Money
    reversed: Money
    unallocated: Money


class StudentBalance(BaseModel):
    student_id: int
    total_due: Money
    total_paid: Money
    balance: Money
    overdue: Money
    credit: Money
    open_dues: int


class ReceiptSend(BaseModel):
    upload: bool = True
    whatsapp: bool = True
    phone: Optional[str] = Field(default=None, max_length=20)
