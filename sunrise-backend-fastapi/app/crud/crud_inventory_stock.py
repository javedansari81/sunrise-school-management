"""
CRUD operations for Inventory Stock Management
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import joinedload, selectinload
from datetime import date

from app.models.inventory import (
    InventoryStock, InventoryStockProcurement, InventoryStockProcurementItem,
    InventoryItemType, InventorySizeType
)
from app.models.expense import Vendor
from app.schemas.inventory import (
    InventoryStockCreate, InventoryStockUpdate,
    InventoryStockProcurementCreate, InventoryStockProcurementUpdate
)


class CRUDInventoryStock:
    """CRUD operations for inventory stock"""
    
    async def get_stock_list(
        self,
        db: AsyncSession,
        item_type_id: Optional[int] = None,
        size_type_id: Optional[int] = None,
        low_stock_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[InventoryStock], int]:
        """Get stock list with filters and pagination"""
        query = select(InventoryStock).options(
            joinedload(InventoryStock.item_type),
            joinedload(InventoryStock.size_type)
        )
        
        filters = []
        if item_type_id:
            filters.append(InventoryStock.inventory_item_type_id == item_type_id)
        if size_type_id:
            filters.append(InventoryStock.size_type_id == size_type_id)
        if low_stock_only:
            filters.append(InventoryStock.current_quantity <= InventoryStock.minimum_threshold)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(func.count()).select_from(InventoryStock)
        if filters:
            count_query = count_query.where(and_(*filters))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(InventoryStock.id)
        result = await db.execute(query)
        stocks = result.scalars().all()
        
        return list(stocks), total
    
    async def get_stock_by_id(
        self,
        db: AsyncSession,
        stock_id: int
    ) -> Optional[InventoryStock]:
        """Get stock by ID"""
        query = select(InventoryStock).options(
            joinedload(InventoryStock.item_type),
            joinedload(InventoryStock.size_type)
        ).where(InventoryStock.id == stock_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_stock_by_item(
        self,
        db: AsyncSession,
        item_type_id: int,
        size_type_id: Optional[int] = None
    ) -> Optional[InventoryStock]:
        """Get stock for specific item-size combination"""
        filters = [InventoryStock.inventory_item_type_id == item_type_id]
        
        if size_type_id is not None:
            filters.append(InventoryStock.size_type_id == size_type_id)
        else:
            filters.append(InventoryStock.size_type_id.is_(None))
        
        query = select(InventoryStock).where(and_(*filters))
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_stock(
        self,
        db: AsyncSession,
        stock_data: InventoryStockCreate
    ) -> InventoryStock:
        """Create new stock record"""
        stock = InventoryStock(**stock_data.model_dump())
        db.add(stock)
        await db.commit()
        await db.refresh(stock)
        return stock
    
    async def update_stock(
        self,
        db: AsyncSession,
        stock_id: int,
        stock_data: InventoryStockUpdate
    ) -> Optional[InventoryStock]:
        """Update stock record"""
        stock = await self.get_stock_by_id(db, stock_id)
        if not stock:
            return None
        
        update_data = stock_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(stock, field, value)
        
        await db.commit()
        await db.refresh(stock)
        return stock
    
    async def adjust_stock_quantity(
        self,
        db: AsyncSession,
        item_type_id: int,
        size_type_id: Optional[int],
        quantity_change: int,
        restock_date: Optional[date] = None
    ) -> Optional[InventoryStock]:
        """
        Adjust stock quantity (positive for increase, negative for decrease)
        Creates stock record if it doesn't exist
        """
        stock = await self.get_stock_by_item(db, item_type_id, size_type_id)
        
        if not stock:
            # Create new stock record
            stock = InventoryStock(
                inventory_item_type_id=item_type_id,
                size_type_id=size_type_id,
                current_quantity=max(0, quantity_change),
                minimum_threshold=10,
                reorder_quantity=50
            )
            db.add(stock)
        else:
            # Update existing stock
            stock.current_quantity = max(0, stock.current_quantity + quantity_change)
        
        # Update restock date if provided and quantity increased
        if restock_date and quantity_change > 0:
            stock.last_restocked_date = restock_date
        
        await db.commit()
        await db.refresh(stock)
        return stock
    
    async def get_low_stock_alerts(
        self,
        db: AsyncSession
    ) -> List[InventoryStock]:
        """Get items with stock below minimum threshold"""
        query = select(InventoryStock).options(
            joinedload(InventoryStock.item_type),
            joinedload(InventoryStock.size_type)
        ).where(
            InventoryStock.current_quantity <= InventoryStock.minimum_threshold
        ).order_by(InventoryStock.current_quantity)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def check_stock_availability(
        self,
        db: AsyncSession,
        item_type_id: int,
        size_type_id: Optional[int],
        required_quantity: int
    ) -> Tuple[bool, int]:
        """
        Check if sufficient stock is available
        Returns (is_available, current_quantity)
        """
        stock = await self.get_stock_by_item(db, item_type_id, size_type_id)
        
        if not stock:
            return False, 0
        
        return stock.current_quantity >= required_quantity, stock.current_quantity


class CRUDInventoryStockProcurement:
    """CRUD operations for stock procurements"""
    
    async def get_procurement_list(
        self,
        db: AsyncSession,
        vendor_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        payment_status_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[InventoryStockProcurement], int]:
        """Get procurement list with filters and pagination"""
        query = select(InventoryStockProcurement).options(
            joinedload(InventoryStockProcurement.vendor),
            joinedload(InventoryStockProcurement.payment_method),
            joinedload(InventoryStockProcurement.payment_status),
            selectinload(InventoryStockProcurement.items).joinedload(InventoryStockProcurementItem.item_type),
            selectinload(InventoryStockProcurement.items).joinedload(InventoryStockProcurementItem.size_type)
        )
        
        filters = []
        if vendor_id:
            filters.append(InventoryStockProcurement.vendor_id == vendor_id)
        if from_date:
            filters.append(InventoryStockProcurement.procurement_date >= from_date)
        if to_date:
            filters.append(InventoryStockProcurement.procurement_date <= to_date)
        if payment_status_id:
            filters.append(InventoryStockProcurement.payment_status_id == payment_status_id)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(func.count()).select_from(InventoryStockProcurement)
        if filters:
            count_query = count_query.where(and_(*filters))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(InventoryStockProcurement.procurement_date.desc())
        result = await db.execute(query)
        procurements = result.scalars().all()
        
        return list(procurements), total
    
    async def get_procurement_by_id(
        self,
        db: AsyncSession,
        procurement_id: int
    ) -> Optional[InventoryStockProcurement]:
        """Get procurement by ID"""
        query = select(InventoryStockProcurement).options(
            joinedload(InventoryStockProcurement.vendor),
            joinedload(InventoryStockProcurement.payment_method),
            joinedload(InventoryStockProcurement.payment_status),
            selectinload(InventoryStockProcurement.items).joinedload(InventoryStockProcurementItem.item_type),
            selectinload(InventoryStockProcurement.items).joinedload(InventoryStockProcurementItem.size_type)
        ).where(InventoryStockProcurement.id == procurement_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create_procurement(
        self,
        db: AsyncSession,
        procurement_data: InventoryStockProcurementCreate,
        created_by: int
    ) -> InventoryStockProcurement:
        """
        Create new procurement and update stock levels
        """
        # Calculate total amount
        total_amount = sum(
            item.quantity * item.unit_cost
            for item in procurement_data.items
        )

        # Create procurement record
        procurement = InventoryStockProcurement(
            vendor_id=procurement_data.vendor_id,
            procurement_date=procurement_data.procurement_date,
            invoice_number=procurement_data.invoice_number,
            total_amount=total_amount,
            payment_method_id=procurement_data.payment_method_id,
            payment_status_id=procurement_data.payment_status_id,
            payment_date=procurement_data.payment_date,
            payment_reference=procurement_data.payment_reference,
            remarks=procurement_data.remarks,
            invoice_url=procurement_data.invoice_url,
            created_by=created_by
        )
        db.add(procurement)
        await db.flush()  # Get procurement ID

        # Create procurement items and update stock
        stock_crud = CRUDInventoryStock()
        for item_data in procurement_data.items:
            # Create procurement item
            item = InventoryStockProcurementItem(
                procurement_id=procurement.id,
                inventory_item_type_id=item_data.inventory_item_type_id,
                size_type_id=item_data.size_type_id,
                quantity=item_data.quantity,
                unit_cost=item_data.unit_cost,
                total_cost=item_data.quantity * item_data.unit_cost
            )
            db.add(item)

            # Update stock quantity
            await stock_crud.adjust_stock_quantity(
                db=db,
                item_type_id=item_data.inventory_item_type_id,
                size_type_id=item_data.size_type_id,
                quantity_change=item_data.quantity,
                restock_date=procurement_data.procurement_date
            )

        await db.commit()
        await db.refresh(procurement)

        # Load relationships
        await db.refresh(procurement, ['vendor', 'payment_method', 'payment_status', 'items'])
        for item in procurement.items:
            await db.refresh(item, ['item_type', 'size_type'])

        return procurement

    async def update_procurement(
        self,
        db: AsyncSession,
        procurement_id: int,
        procurement_data: InventoryStockProcurementUpdate
    ) -> Optional[InventoryStockProcurement]:
        """Update procurement (payment details only, not items)"""
        procurement = await self.get_procurement_by_id(db, procurement_id)
        if not procurement:
            return None

        update_data = procurement_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(procurement, field, value)

        await db.commit()
        await db.refresh(procurement)
        return procurement


# Create singleton instances
crud_inventory_stock = CRUDInventoryStock()
crud_inventory_stock_procurement = CRUDInventoryStockProcurement()
