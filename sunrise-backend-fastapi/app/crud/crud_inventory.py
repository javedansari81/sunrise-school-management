"""
CRUD operations for Inventory Management
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, extract, desc
from sqlalchemy.orm import selectinload, joinedload
from datetime import date, datetime
from decimal import Decimal

from app.models.inventory import (
    InventoryItemType, InventorySizeType, InventoryPricing,
    InventoryPurchase, InventoryPurchaseItem
)
from app.models.student import Student
from app.models.metadata import SessionYear, Class, PaymentMethod
from app.schemas.inventory import (
    InventoryPricingCreate, InventoryPricingUpdate,
    InventoryPurchaseCreate, InventoryPurchaseUpdate
)


class CRUDInventoryPricing:
    """CRUD operations for inventory pricing"""
    
    async def get_pricing_list(
        self,
        db: AsyncSession,
        session_year_id: Optional[int] = None,
        item_type_id: Optional[int] = None,
        class_id: Optional[int] = None,
        is_active: bool = True
    ) -> List[InventoryPricing]:
        """Get pricing list with filters"""
        query = select(InventoryPricing).options(
            joinedload(InventoryPricing.item_type),
            joinedload(InventoryPricing.size_type),
            joinedload(InventoryPricing.class_ref),
            joinedload(InventoryPricing.session_year)
        )
        
        filters = []
        if session_year_id:
            filters.append(InventoryPricing.session_year_id == session_year_id)
        if item_type_id:
            filters.append(InventoryPricing.inventory_item_type_id == item_type_id)
        if class_id:
            filters.append(InventoryPricing.class_id == class_id)
        if is_active is not None:
            filters.append(InventoryPricing.is_active == is_active)
        
        if filters:
            query = query.where(and_(*filters))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create_pricing(
        self,
        db: AsyncSession,
        pricing_data: InventoryPricingCreate,
        created_by: int
    ) -> InventoryPricing:
        """Create new pricing entry"""
        pricing = InventoryPricing(
            **pricing_data.model_dump(),
            created_by=created_by
        )
        db.add(pricing)
        await db.commit()
        await db.refresh(pricing)
        return pricing
    
    async def update_pricing(
        self,
        db: AsyncSession,
        pricing_id: int,
        pricing_data: InventoryPricingUpdate
    ) -> Optional[InventoryPricing]:
        """Update pricing entry"""
        query = select(InventoryPricing).where(InventoryPricing.id == pricing_id)
        result = await db.execute(query)
        pricing = result.scalar_one_or_none()
        
        if not pricing:
            return None
        
        update_data = pricing_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pricing, field, value)
        
        await db.commit()
        await db.refresh(pricing)
        return pricing


class CRUDInventoryPurchase:
    """CRUD operations for inventory purchases"""
    
    async def get_purchases(
        self,
        db: AsyncSession,
        session_year_id: Optional[int] = None,
        student_id: Optional[int] = None,
        class_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 25
    ) -> Dict[str, Any]:
        """Get purchases with pagination and filters"""
        # Base query with eager loading
        query = select(InventoryPurchase).options(
            joinedload(InventoryPurchase.student).joinedload(Student.class_ref),
            joinedload(InventoryPurchase.session_year),
            joinedload(InventoryPurchase.payment_method),
            selectinload(InventoryPurchase.items).joinedload(InventoryPurchaseItem.item_type),
            selectinload(InventoryPurchase.items).joinedload(InventoryPurchaseItem.size_type)
        )
        
        # Build filters
        filters = []
        if session_year_id:
            filters.append(InventoryPurchase.session_year_id == session_year_id)
        if student_id:
            filters.append(InventoryPurchase.student_id == student_id)
        if class_id:
            filters.append(Student.class_id == class_id)
        if from_date:
            filters.append(InventoryPurchase.purchase_date >= from_date)
        if to_date:
            filters.append(InventoryPurchase.purchase_date <= to_date)
        if search:
            search_filter = or_(
                Student.first_name.ilike(f"%{search}%"),
                Student.last_name.ilike(f"%{search}%"),
                Student.admission_number.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        # Apply filters
        if filters:
            if class_id or search:
                query = query.join(Student)
            query = query.where(and_(*filters))
        
        # Order by purchase date descending
        query = query.order_by(desc(InventoryPurchase.purchase_date))
        
        # Count total
        count_query = select(func.count()).select_from(InventoryPurchase)
        if filters:
            if class_id or search:
                count_query = count_query.join(Student)
            count_query = count_query.where(and_(*filters))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        result = await db.execute(query)
        purchases = result.scalars().all()
        
        return {
            "purchases": purchases,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    
    async def get_purchase_by_id(
        self,
        db: AsyncSession,
        purchase_id: int
    ) -> Optional[InventoryPurchase]:
        """Get purchase by ID with all relationships"""
        query = select(InventoryPurchase).options(
            joinedload(InventoryPurchase.student).joinedload(Student.class_ref),
            joinedload(InventoryPurchase.session_year),
            joinedload(InventoryPurchase.payment_method),
            selectinload(InventoryPurchase.items).joinedload(InventoryPurchaseItem.item_type),
            selectinload(InventoryPurchase.items).joinedload(InventoryPurchaseItem.size_type)
        ).where(InventoryPurchase.id == purchase_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_purchase(
        self,
        db: AsyncSession,
        purchase_data: InventoryPurchaseCreate,
        created_by: int
    ) -> InventoryPurchase:
        """Create new purchase with items"""
        # Calculate total amount
        total_amount = sum(
            item.quantity * item.unit_price
            for item in purchase_data.items
        )
        
        # Generate receipt number
        receipt_number = await self._generate_receipt_number(db)
        
        # Create purchase
        purchase = InventoryPurchase(
            student_id=purchase_data.student_id,
            session_year_id=purchase_data.session_year_id,
            purchase_date=purchase_data.purchase_date,
            total_amount=total_amount,
            payment_method_id=purchase_data.payment_method_id,
            payment_date=purchase_data.payment_date,
            transaction_id=purchase_data.transaction_id,
            receipt_number=receipt_number,
            remarks=purchase_data.remarks,
            purchased_by=purchase_data.purchased_by,
            contact_number=purchase_data.contact_number,
            created_by=created_by
        )
        db.add(purchase)
        await db.flush()
        
        # Create purchase items
        for item_data in purchase_data.items:
            item_total = item_data.quantity * item_data.unit_price
            purchase_item = InventoryPurchaseItem(
                purchase_id=purchase.id,
                inventory_item_type_id=item_data.inventory_item_type_id,
                size_type_id=item_data.size_type_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                total_price=item_total
            )
            db.add(purchase_item)
        
        await db.commit()
        await db.refresh(purchase)
        return purchase
    
    async def _generate_receipt_number(self, db: AsyncSession) -> str:
        """Generate unique receipt number"""
        # Format: INV-YYYYMMDD-XXXX
        today = datetime.now()
        date_str = today.strftime("%Y%m%d")
        
        # Get count of purchases today
        query = select(func.count()).select_from(InventoryPurchase).where(
            func.date(InventoryPurchase.created_at) == today.date()
        )
        result = await db.execute(query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"INV-{date_str}-{sequence}"
    
    async def update_purchase(
        self,
        db: AsyncSession,
        purchase_id: int,
        purchase_data: InventoryPurchaseUpdate
    ) -> Optional[InventoryPurchase]:
        """Update purchase (limited fields)"""
        query = select(InventoryPurchase).where(InventoryPurchase.id == purchase_id)
        result = await db.execute(query)
        purchase = result.scalar_one_or_none()

        if not purchase:
            return None

        update_data = purchase_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(purchase, field, value)

        await db.commit()
        await db.refresh(purchase)
        return purchase


# Create instances
crud_inventory_pricing = CRUDInventoryPricing()
crud_inventory_purchase = CRUDInventoryPurchase()

