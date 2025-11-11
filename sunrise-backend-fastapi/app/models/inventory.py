"""
Inventory Management Models
Aligned with metadata-driven architecture
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, DateTime, DECIMAL, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class InventoryItemType(Base):
    """Inventory item type metadata"""
    __tablename__ = "inventory_item_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # 'UNIFORM', 'ACCESSORY'
    image_url = Column(String(500))  # URL/path to item image
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    pricing = relationship("InventoryPricing", back_populates="item_type")
    purchase_items = relationship("InventoryPurchaseItem", back_populates="item_type")
    stock = relationship("InventoryStock", back_populates="item_type")
    procurement_items = relationship("InventoryStockProcurementItem", back_populates="item_type")


class InventorySizeType(Base):
    """Size type metadata"""
    __tablename__ = "inventory_size_types"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    pricing = relationship("InventoryPricing", back_populates="size_type")
    purchase_items = relationship("InventoryPurchaseItem", back_populates="size_type")
    stock = relationship("InventoryStock", back_populates="size_type")
    procurement_items = relationship("InventoryStockProcurementItem", back_populates="size_type")


class InventoryPricing(Base):
    """Pricing for inventory items"""
    __tablename__ = "inventory_pricing"
    
    id = Column(Integer, primary_key=True, index=True)
    inventory_item_type_id = Column(Integer, ForeignKey("inventory_item_types.id"), nullable=False)
    size_type_id = Column(Integer, ForeignKey("inventory_size_types.id"), nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    
    # Pricing Details
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    description = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    item_type = relationship("InventoryItemType", back_populates="pricing")
    size_type = relationship("InventorySizeType", back_populates="pricing")
    class_ref = relationship("Class", foreign_keys=[class_id])
    session_year = relationship("SessionYear", foreign_keys=[session_year_id])
    creator = relationship("User", foreign_keys=[created_by])


class InventoryPurchase(Base):
    """Main purchase transaction"""
    __tablename__ = "inventory_purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    
    # Purchase Details
    purchase_date = Column(Date, nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    
    # Payment Details
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    payment_date = Column(Date, nullable=False)
    transaction_id = Column(String(100), nullable=True)
    receipt_number = Column(String(50), nullable=True)
    
    # Additional Info
    remarks = Column(Text, nullable=True)
    purchased_by = Column(String(200), nullable=True)  # Parent/Guardian name
    contact_number = Column(String(20), nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="inventory_purchases")
    session_year = relationship("SessionYear", foreign_keys=[session_year_id])
    payment_method = relationship("PaymentMethod", foreign_keys=[payment_method_id])
    items = relationship("InventoryPurchaseItem", back_populates="purchase", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])


class InventoryPurchaseItem(Base):
    """Purchase line items"""
    __tablename__ = "inventory_purchase_items"
    
    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("inventory_purchases.id"), nullable=False)
    inventory_item_type_id = Column(Integer, ForeignKey("inventory_item_types.id"), nullable=False)
    size_type_id = Column(Integer, ForeignKey("inventory_size_types.id"), nullable=True)
    
    # Item Details
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    purchase = relationship("InventoryPurchase", back_populates="items")
    item_type = relationship("InventoryItemType", back_populates="purchase_items")
    size_type = relationship("InventorySizeType", back_populates="purchase_items")


class InventoryStock(Base):
    """Current stock levels for inventory items"""
    __tablename__ = "inventory_stock"

    id = Column(Integer, primary_key=True, index=True)
    inventory_item_type_id = Column(Integer, ForeignKey("inventory_item_types.id"), nullable=False)
    size_type_id = Column(Integer, ForeignKey("inventory_size_types.id"), nullable=True)

    # Stock Levels
    current_quantity = Column(Integer, nullable=False, default=0)
    minimum_threshold = Column(Integer, nullable=False, default=10)
    reorder_quantity = Column(Integer, nullable=False, default=50)

    # Metadata
    last_restocked_date = Column(Date, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    item_type = relationship("InventoryItemType", back_populates="stock")
    size_type = relationship("InventorySizeType", back_populates="stock")


class InventoryStockProcurement(Base):
    """Stock procurement from vendors"""
    __tablename__ = "inventory_stock_procurements"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    procurement_date = Column(Date, nullable=False)
    invoice_number = Column(String(100), nullable=True)
    total_amount = Column(DECIMAL(12, 2), nullable=False)

    # Payment Details
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    payment_status_id = Column(Integer, ForeignKey("payment_statuses.id"), default=1)
    payment_date = Column(Date, nullable=True)
    payment_reference = Column(String(100), nullable=True)

    # Additional Info
    remarks = Column(Text, nullable=True)
    invoice_url = Column(String(500), nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    vendor = relationship("Vendor", foreign_keys=[vendor_id])
    payment_method = relationship("PaymentMethod", foreign_keys=[payment_method_id])
    payment_status = relationship("PaymentStatus", foreign_keys=[payment_status_id])
    items = relationship("InventoryStockProcurementItem", back_populates="procurement", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])


class InventoryStockProcurementItem(Base):
    """Line items for stock procurements"""
    __tablename__ = "inventory_stock_procurement_items"

    id = Column(Integer, primary_key=True, index=True)
    procurement_id = Column(Integer, ForeignKey("inventory_stock_procurements.id"), nullable=False)
    inventory_item_type_id = Column(Integer, ForeignKey("inventory_item_types.id"), nullable=False)
    size_type_id = Column(Integer, ForeignKey("inventory_size_types.id"), nullable=True)

    # Item Details
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(DECIMAL(10, 2), nullable=False)
    total_cost = Column(DECIMAL(10, 2), nullable=False)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    procurement = relationship("InventoryStockProcurement", back_populates="items")
    item_type = relationship("InventoryItemType", back_populates="procurement_items")
    size_type = relationship("InventorySizeType", back_populates="procurement_items")

