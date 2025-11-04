"""
Inventory Management Schemas
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# =====================================================
# Pricing Schemas
# =====================================================

class InventoryPricingBase(BaseModel):
    """Base schema for inventory pricing"""
    inventory_item_type_id: int = Field(..., description="Inventory item type ID")
    size_type_id: Optional[int] = Field(None, description="Size type ID (optional)")
    class_id: Optional[int] = Field(None, description="Class ID for class-specific pricing (optional)")
    session_year_id: int = Field(..., description="Session year ID")
    unit_price: Decimal = Field(..., gt=0, description="Price per unit")
    description: Optional[str] = Field(None, description="Additional description")
    effective_from: date = Field(..., description="Date from which this price is effective")
    effective_to: Optional[date] = Field(None, description="Date until which this price is effective")


class InventoryPricingCreate(InventoryPricingBase):
    """Schema for creating inventory pricing"""
    pass


class InventoryPricingUpdate(BaseModel):
    """Schema for updating inventory pricing"""
    unit_price: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    effective_to: Optional[date] = None


class InventoryPricingResponse(InventoryPricingBase):
    """Schema for inventory pricing response"""
    id: int
    is_active: bool
    item_type_name: str
    item_type_description: str
    item_image_url: Optional[str] = None
    size_name: Optional[str] = None
    class_name: Optional[str] = None
    session_year_name: str
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Purchase Item Schemas
# =====================================================

class InventoryPurchaseItemBase(BaseModel):
    """Base schema for purchase items"""
    inventory_item_type_id: int = Field(..., description="Inventory item type ID")
    size_type_id: Optional[int] = Field(None, description="Size type ID (optional)")
    quantity: int = Field(..., gt=0, description="Quantity of items")
    unit_price: Decimal = Field(..., gt=0, description="Price per unit")


class InventoryPurchaseItemCreate(InventoryPurchaseItemBase):
    """Schema for creating purchase items"""
    pass


class InventoryPurchaseItemResponse(InventoryPurchaseItemBase):
    """Schema for purchase item response"""
    id: int
    total_price: Decimal
    item_type_name: str
    item_type_description: str
    item_image_url: Optional[str] = None
    size_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# Purchase Schemas
# =====================================================

class InventoryPurchaseBase(BaseModel):
    """Base schema for inventory purchases"""
    student_id: int = Field(..., description="Student ID")
    session_year_id: int = Field(..., description="Session year ID")
    purchase_date: date = Field(..., description="Date of purchase")
    payment_method_id: int = Field(..., description="Payment method ID")
    payment_date: date = Field(..., description="Date of payment")
    transaction_id: Optional[str] = Field(None, max_length=100, description="Transaction ID for digital payments")
    remarks: Optional[str] = Field(None, description="Additional remarks")
    purchased_by: Optional[str] = Field(None, max_length=200, description="Name of parent/guardian")
    contact_number: Optional[str] = Field(None, max_length=20, description="Contact number")


class InventoryPurchaseCreate(InventoryPurchaseBase):
    """Schema for creating inventory purchases"""
    items: List[InventoryPurchaseItemCreate] = Field(..., min_length=1, description="List of items to purchase")
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one item is required')
        return v


class InventoryPurchaseUpdate(BaseModel):
    """Schema for updating inventory purchases"""
    remarks: Optional[str] = None
    transaction_id: Optional[str] = Field(None, max_length=100)


class InventoryPurchaseResponse(InventoryPurchaseBase):
    """Schema for inventory purchase response"""
    id: int
    total_amount: Decimal
    receipt_number: Optional[str] = None
    student_name: str
    student_admission_number: str
    student_class_name: str
    student_roll_number: Optional[str] = None
    session_year_name: str
    payment_method_name: str
    items: List[InventoryPurchaseItemResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True


class InventoryPurchaseListResponse(BaseModel):
    """Schema for paginated purchase list response"""
    purchases: List[InventoryPurchaseResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# =====================================================
# Summary Schemas
# =====================================================

class StudentInventorySummary(BaseModel):
    """Schema for student inventory summary"""
    student_id: int
    student_name: str
    admission_number: str
    class_name: str
    roll_number: Optional[str] = None
    total_purchases: int
    total_amount_spent: Decimal
    last_purchase_date: Optional[date] = None
    items_purchased: List[dict]  # [{item_name, quantity, total_price}]


class InventoryStatistics(BaseModel):
    """Schema for inventory statistics"""
    total_purchases: int
    total_revenue: float
    total_students: int
    items_sold_by_type: List[dict]  # [{item_name, quantity, revenue}]
    purchases_by_month: List[dict]  # [{month, count, revenue}]
    top_selling_items: List[dict]  # [{item_name, quantity}]

