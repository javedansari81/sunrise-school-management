"""
Inventory Management API Endpoints
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from sqlalchemy.orm import joinedload, selectinload
from datetime import date
import cloudinary
import cloudinary.uploader

from app.core.database import get_db
from app.core.cloudinary_config import configure_cloudinary
from app.api.deps import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.inventory import (
    InventoryItemType, InventorySizeType, InventoryPricing,
    InventoryPurchase, InventoryPurchaseItem
)
from app.models.student import Student
from app.schemas.inventory import (
    InventoryPricingCreate, InventoryPricingUpdate, InventoryPricingResponse,
    InventoryPurchaseCreate, InventoryPurchaseUpdate, InventoryPurchaseResponse,
    InventoryPurchaseListResponse, StudentInventorySummary, InventoryStatistics
)
from app.crud.crud_inventory import crud_inventory_pricing, crud_inventory_purchase

router = APIRouter()


# =====================================================
# Pricing Management Endpoints
# =====================================================

@router.get("/pricing/", response_model=List[InventoryPricingResponse])
async def get_pricing(
    session_year_id: Optional[int] = None,
    item_type_id: Optional[int] = None,
    class_id: Optional[int] = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get inventory pricing with filters
    Admin only
    """
    pricing_list = await crud_inventory_pricing.get_pricing_list(
        db,
        session_year_id=session_year_id,
        item_type_id=item_type_id,
        class_id=class_id,
        is_active=is_active
    )
    
    # Convert to response schema
    result = []
    for pricing in pricing_list:
        result.append(InventoryPricingResponse(
            id=pricing.id,
            inventory_item_type_id=pricing.inventory_item_type_id,
            size_type_id=pricing.size_type_id,
            class_id=pricing.class_id,
            session_year_id=pricing.session_year_id,
            unit_price=pricing.unit_price,
            description=pricing.description,
            effective_from=pricing.effective_from,
            effective_to=pricing.effective_to,
            is_active=pricing.is_active,
            item_type_name=pricing.item_type.name,
            item_type_description=pricing.item_type.description,
            item_image_url=pricing.item_type.image_url,
            size_name=pricing.size_type.name if pricing.size_type else None,
            class_name=pricing.class_ref.name if pricing.class_ref else None,
            session_year_name=pricing.session_year.name,
            created_at=pricing.created_at
        ))

    return result


@router.post("/pricing/", response_model=InventoryPricingResponse, status_code=status.HTTP_201_CREATED)
async def create_pricing(
    pricing_data: InventoryPricingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create new pricing entry
    Admin only
    """
    pricing = await crud_inventory_pricing.create_pricing(
        db,
        pricing_data=pricing_data,
        created_by=current_user.id
    )
    
    # Refresh to load relationships
    await db.refresh(pricing, ['item_type', 'size_type', 'class_ref', 'session_year'])
    
    return InventoryPricingResponse(
        id=pricing.id,
        inventory_item_type_id=pricing.inventory_item_type_id,
        size_type_id=pricing.size_type_id,
        class_id=pricing.class_id,
        session_year_id=pricing.session_year_id,
        unit_price=pricing.unit_price,
        description=pricing.description,
        effective_from=pricing.effective_from,
        effective_to=pricing.effective_to,
        is_active=pricing.is_active,
        item_type_name=pricing.item_type.name,
        item_type_description=pricing.item_type.description,
        item_image_url=pricing.item_type.image_url,
        size_name=pricing.size_type.name if pricing.size_type else None,
        class_name=pricing.class_ref.name if pricing.class_ref else None,
        session_year_name=pricing.session_year.name,
        created_at=pricing.created_at
    )


@router.put("/pricing/{pricing_id}", response_model=InventoryPricingResponse)
async def update_pricing(
    pricing_id: int,
    pricing_data: InventoryPricingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update pricing entry
    Admin only
    """
    pricing = await crud_inventory_pricing.update_pricing(
        db,
        pricing_id=pricing_id,
        pricing_data=pricing_data
    )
    
    if not pricing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricing entry not found"
        )
    
    # Refresh to load relationships
    await db.refresh(pricing, ['item_type', 'size_type', 'class_ref', 'session_year'])
    
    return InventoryPricingResponse(
        id=pricing.id,
        inventory_item_type_id=pricing.inventory_item_type_id,
        size_type_id=pricing.size_type_id,
        class_id=pricing.class_id,
        session_year_id=pricing.session_year_id,
        unit_price=pricing.unit_price,
        description=pricing.description,
        effective_from=pricing.effective_from,
        effective_to=pricing.effective_to,
        is_active=pricing.is_active,
        item_type_name=pricing.item_type.name,
        item_type_description=pricing.item_type.description,
        item_image_url=pricing.item_type.image_url,
        size_name=pricing.size_type.name if pricing.size_type else None,
        class_name=pricing.class_ref.name if pricing.class_ref else None,
        session_year_name=pricing.session_year.name,
        created_at=pricing.created_at
    )


# =====================================================
# Item Type Image Upload Endpoint
# =====================================================

@router.post("/item-types/{item_type_id}/upload-image")
async def upload_item_type_image(
    item_type_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Upload image for inventory item type to Cloudinary
    Admin only
    """
    # Validate item type exists
    item_type = await db.get(InventoryItemType, item_type_id)
    if not item_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item type not found"
        )

    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload JPEG, PNG, GIF, or WebP image."
        )

    # Validate file size (10MB limit)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10MB limit"
        )

    # Reset file pointer
    await file.seek(0)

    try:
        # Delete old image from Cloudinary if exists
        if item_type.image_url:
            try:
                # Extract public_id from URL
                # URL format: https://res.cloudinary.com/{cloud_name}/image/upload/{transformations}/{public_id}.{format}
                url_parts = item_type.image_url.split('/')
                if 'inventory' in url_parts:
                    idx = url_parts.index('inventory')
                    public_id = 'inventory/' + url_parts[idx + 1].split('.')[0]
                    cloudinary.uploader.destroy(public_id)
            except Exception as e:
                # Log but don't fail if deletion fails
                print(f"Warning: Could not delete old image: {e}")

        # Upload to Cloudinary
        cloudinary_response = cloudinary.uploader.upload(
            file.file,
            folder="inventory",
            public_id=f"item_{item_type_id}_{item_type.name}",
            resource_type="image",
            transformation=[
                {'width': 400, 'height': 400, 'crop': 'fill'},
                {'quality': 'auto', 'fetch_format': 'auto'}
            ],
            overwrite=True
        )

        # Update item type with new image URL
        item_type.image_url = cloudinary_response['secure_url']
        await db.commit()
        await db.refresh(item_type)

        return {
            "message": "Image uploaded successfully",
            "item_type_id": item_type_id,
            "image_url": item_type.image_url,
            "cloudinary_public_id": cloudinary_response['public_id']
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


# =====================================================
# Purchase Management Endpoints
# =====================================================

@router.get("/purchases/", response_model=InventoryPurchaseListResponse)
async def get_purchases(
    session_year_id: Optional[int] = None,
    student_id: Optional[int] = None,
    class_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = Query(None, description="Search by student name or admission number"),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get purchases with pagination and filters
    """
    result = await crud_inventory_purchase.get_purchases(
        db,
        session_year_id=session_year_id,
        student_id=student_id,
        class_id=class_id,
        from_date=from_date,
        to_date=to_date,
        search=search,
        page=page,
        per_page=per_page
    )
    
    # Convert to response schema
    purchases_response = []
    for purchase in result["purchases"]:
        items_response = [
            {
                "id": item.id,
                "inventory_item_type_id": item.inventory_item_type_id,
                "size_type_id": item.size_type_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
                "item_type_name": item.item_type.name,
                "item_type_description": item.item_type.description,
                "item_image_url": item.item_type.image_url,
                "size_name": item.size_type.name if item.size_type else None,
                "created_at": item.created_at
            }
            for item in purchase.items
        ]
        
        purchases_response.append(InventoryPurchaseResponse(
            id=purchase.id,
            student_id=purchase.student_id,
            session_year_id=purchase.session_year_id,
            purchase_date=purchase.purchase_date,
            total_amount=purchase.total_amount,
            payment_method_id=purchase.payment_method_id,
            payment_date=purchase.payment_date,
            transaction_id=purchase.transaction_id,
            receipt_number=purchase.receipt_number,
            remarks=purchase.remarks,
            purchased_by=purchase.purchased_by,
            contact_number=purchase.contact_number,
            student_name=f"{purchase.student.first_name} {purchase.student.last_name}",
            student_admission_number=purchase.student.admission_number,
            student_class_name=purchase.student.class_ref.name,
            student_roll_number=purchase.student.roll_number,
            session_year_name=purchase.session_year.name,
            payment_method_name=purchase.payment_method.description,
            items=items_response,
            created_at=purchase.created_at
        ))
    
    return InventoryPurchaseListResponse(
        purchases=purchases_response,
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
        total_pages=result["total_pages"]
    )


@router.post("/purchases/", response_model=InventoryPurchaseResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase(
    purchase_data: InventoryPurchaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create new purchase transaction
    Admin only
    """
    purchase = await crud_inventory_purchase.create_purchase(
        db,
        purchase_data=purchase_data,
        created_by=current_user.id
    )
    
    # Refresh to load all relationships
    await db.refresh(purchase, ['student', 'session_year', 'payment_method', 'items'])
    
    # Load nested relationships
    for item in purchase.items:
        await db.refresh(item, ['item_type', 'size_type'])
    
    await db.refresh(purchase.student, ['class_ref'])
    
    items_response = [
        {
            "id": item.id,
            "inventory_item_type_id": item.inventory_item_type_id,
            "size_type_id": item.size_type_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item.total_price,
            "item_type_name": item.item_type.name,
            "item_type_description": item.item_type.description,
            "item_image_url": item.item_type.image_url,
            "size_name": item.size_type.name if item.size_type else None,
            "created_at": item.created_at
        }
        for item in purchase.items
    ]
    
    return InventoryPurchaseResponse(
        id=purchase.id,
        student_id=purchase.student_id,
        session_year_id=purchase.session_year_id,
        purchase_date=purchase.purchase_date,
        total_amount=purchase.total_amount,
        payment_method_id=purchase.payment_method_id,
        payment_date=purchase.payment_date,
        transaction_id=purchase.transaction_id,
        receipt_number=purchase.receipt_number,
        remarks=purchase.remarks,
        purchased_by=purchase.purchased_by,
        contact_number=purchase.contact_number,
        student_name=f"{purchase.student.first_name} {purchase.student.last_name}",
        student_admission_number=purchase.student.admission_number,
        student_class_name=purchase.student.class_ref.name,
        student_roll_number=purchase.student.roll_number,
        session_year_name=purchase.session_year.name,
        payment_method_name=purchase.payment_method.description,
        items=items_response,
        created_at=purchase.created_at
    )


@router.get("/purchases/{purchase_id}", response_model=InventoryPurchaseResponse)
async def get_purchase(
    purchase_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get purchase details by ID
    """
    purchase = await crud_inventory_purchase.get_purchase_by_id(db, purchase_id=purchase_id)

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase not found"
        )

    items_response = [
        {
            "id": item.id,
            "inventory_item_type_id": item.inventory_item_type_id,
            "size_type_id": item.size_type_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item.total_price,
            "item_type_name": item.item_type.name,
            "item_type_description": item.item_type.description,
            "item_image_url": item.item_type.image_url,
            "size_name": item.size_type.name if item.size_type else None,
            "created_at": item.created_at
        }
        for item in purchase.items
    ]

    return InventoryPurchaseResponse(
        id=purchase.id,
        student_id=purchase.student_id,
        session_year_id=purchase.session_year_id,
        purchase_date=purchase.purchase_date,
        total_amount=purchase.total_amount,
        payment_method_id=purchase.payment_method_id,
        payment_date=purchase.payment_date,
        transaction_id=purchase.transaction_id,
        receipt_number=purchase.receipt_number,
        remarks=purchase.remarks,
        purchased_by=purchase.purchased_by,
        contact_number=purchase.contact_number,
        student_name=f"{purchase.student.first_name} {purchase.student.last_name}",
        student_admission_number=purchase.student.admission_number,
        student_class_name=purchase.student.class_ref.name,
        student_roll_number=purchase.student.roll_number,
        session_year_name=purchase.session_year.name,
        payment_method_name=purchase.payment_method.description,
        items=items_response,
        created_at=purchase.created_at
    )


# =====================================================
# Statistics Endpoints
# =====================================================

@router.get("/statistics/", response_model=InventoryStatistics)
async def get_statistics(
    session_year_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get inventory statistics
    Admin only
    """
    # Build base query
    query = select(InventoryPurchase).options(
        selectinload(InventoryPurchase.items).joinedload(InventoryPurchaseItem.item_type)
    )

    filters = []
    if session_year_id:
        filters.append(InventoryPurchase.session_year_id == session_year_id)
    if from_date:
        filters.append(InventoryPurchase.purchase_date >= from_date)
    if to_date:
        filters.append(InventoryPurchase.purchase_date <= to_date)

    if filters:
        query = query.where(and_(*filters))

    result = await db.execute(query)
    purchases = result.scalars().all()

    # Calculate statistics
    total_purchases = len(purchases)
    total_revenue = sum(p.total_amount for p in purchases)
    unique_students = len(set(p.student_id for p in purchases))

    # Items sold by type
    items_by_type = {}
    for purchase in purchases:
        for item in purchase.items:
            item_name = item.item_type.description
            if item_name not in items_by_type:
                items_by_type[item_name] = {"quantity": 0, "revenue": 0}
            items_by_type[item_name]["quantity"] += item.quantity
            items_by_type[item_name]["revenue"] += float(item.total_price)

    items_sold_by_type = [
        {"item_name": name, "quantity": data["quantity"], "revenue": data["revenue"]}
        for name, data in items_by_type.items()
    ]

    # Purchases by month
    purchases_by_month_dict = {}
    for purchase in purchases:
        month_key = purchase.purchase_date.strftime("%Y-%m")
        if month_key not in purchases_by_month_dict:
            purchases_by_month_dict[month_key] = {"count": 0, "revenue": 0}
        purchases_by_month_dict[month_key]["count"] += 1
        purchases_by_month_dict[month_key]["revenue"] += float(purchase.total_amount)

    purchases_by_month = [
        {"month": month, "count": data["count"], "revenue": data["revenue"]}
        for month, data in sorted(purchases_by_month_dict.items())
    ]

    # Top selling items
    top_selling_items = sorted(
        [{"item_name": name, "quantity": data["quantity"]} for name, data in items_by_type.items()],
        key=lambda x: x["quantity"],
        reverse=True
    )[:10]

    return InventoryStatistics(
        total_purchases=total_purchases,
        total_revenue=float(total_revenue) if total_revenue else 0.0,
        total_students=unique_students,
        items_sold_by_type=items_sold_by_type,
        purchases_by_month=purchases_by_month,
        top_selling_items=top_selling_items
    )


