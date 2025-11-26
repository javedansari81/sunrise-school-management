"""
Gallery Management API Endpoints
Handles image upload to Cloudinary and metadata management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
import cloudinary
import cloudinary.uploader

from app.core.database import get_db
from app.core.cloudinary_config import configure_cloudinary
from app.models.gallery import GalleryCategory, GalleryImage
from app.models.user import User
from app.schemas.gallery import (
    GalleryCategoryResponse, GalleryCategoryCreate, GalleryCategoryUpdate,
    GalleryImageResponse, GalleryImageWithCategory, GalleryImageToggleHomePageRequest,
    GalleryImageUpdate,
    PublicGalleryCategory, PublicGalleryImage
)
from app.api.deps import get_current_active_user, get_current_admin_user

router = APIRouter()

# Ensure Cloudinary is configured
configure_cloudinary()


# =====================================================
# Gallery Category Endpoints
# =====================================================
# NOTE: Public gallery endpoint moved to /api/v1/public/gallery
# This removes the duplicate endpoint and follows the pattern of other public endpoints

@router.get("/categories", response_model=List[GalleryCategoryResponse])
async def get_gallery_categories(
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all gallery categories
    Public endpoint - no authentication required
    """
    query = select(GalleryCategory)

    if is_active is not None:
        query = query.where(GalleryCategory.is_active == is_active)

    query = query.order_by(GalleryCategory.display_order.asc())

    result = await db.execute(query)
    categories = result.scalars().all()

    return categories


@router.post("/categories", response_model=GalleryCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_gallery_category(
    category: GalleryCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new gallery category
    Admin only endpoint
    """
    new_category = GalleryCategory(**category.model_dump())
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    
    return new_category


# =====================================================
# Gallery Image Endpoints
# =====================================================

@router.get("/images", response_model=List[GalleryImageWithCategory])
async def get_gallery_images(
    category_id: Optional[int] = None,
    is_active: Optional[bool] = True,
    is_visible_on_home_page: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all gallery images (optionally filtered by category and home page visibility)
    Public endpoint - no authentication required
    """
    query = select(GalleryImage).join(GalleryCategory).options(
        selectinload(GalleryImage.category),
        selectinload(GalleryImage.uploader)
    )

    if category_id:
        query = query.where(GalleryImage.category_id == category_id)

    if is_active is not None:
        query = query.where(
            and_(
                GalleryImage.is_active == is_active,
                GalleryCategory.is_active == is_active
            )
        )

    if is_visible_on_home_page is not None:
        query = query.where(GalleryImage.is_visible_on_home_page == is_visible_on_home_page)

    query = query.order_by(
        GalleryImage.display_order.asc(),
        GalleryImage.upload_date.desc()
    )

    result = await db.execute(query)
    images = result.scalars().all()

    # Add computed fields
    response_images = []
    for image in images:
        image_dict = {
            **{k: v for k, v in image.__dict__.items() if not k.startswith('_')},
            'category': image.category,
            'category_name': image.category.description if image.category else None,
            'uploaded_by_name': f"{image.uploader.first_name} {image.uploader.last_name}" if image.uploader else None
        }
        response_images.append(image_dict)

    return response_images


@router.get("/images/home-page", response_model=List[GalleryImageWithCategory])
async def get_home_page_images(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get featured images for home page carousel
    Returns images where is_visible_on_home_page = TRUE
    Ordered by home_page_display_order (NULL values appear last), then upload_date
    Public endpoint - no authentication required
    """
    query = select(GalleryImage).join(GalleryCategory).options(
        selectinload(GalleryImage.category),
        selectinload(GalleryImage.uploader)
    ).where(
        and_(
            GalleryImage.is_visible_on_home_page == True,
            GalleryImage.is_active == True,
            GalleryCategory.is_active == True
        )
    ).order_by(
        GalleryImage.home_page_display_order.asc().nulls_last(),
        GalleryImage.upload_date.desc()
    ).limit(limit)

    result = await db.execute(query)
    images = result.scalars().all()

    # Add computed fields
    response_images = []
    for image in images:
        image_dict = {
            **{k: v for k, v in image.__dict__.items() if not k.startswith('_')},
            'category': image.category,
            'category_name': image.category.description if image.category else None,
            'uploaded_by_name': f"{image.uploader.first_name} {image.uploader.last_name}" if image.uploader else None
        }
        response_images.append(image_dict)

    return response_images


@router.get("/images/{image_id}", response_model=GalleryImageWithCategory)
async def get_gallery_image(
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific gallery image by ID
    Public endpoint - no authentication required
    """
    query = select(GalleryImage).options(
        selectinload(GalleryImage.category),
        selectinload(GalleryImage.uploader)
    ).where(GalleryImage.id == image_id)
    result = await db.execute(query)
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Add computed fields
    image_dict = {
        **{k: v for k, v in image.__dict__.items() if not k.startswith('_')},
        'category': image.category,
        'category_name': image.category.description if image.category else None,
        'uploaded_by_name': f"{image.uploader.first_name} {image.uploader.last_name}" if image.uploader else None
    }

    return image_dict


@router.post("/images/upload", response_model=GalleryImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_gallery_image(
    file: UploadFile = File(...),
    category_id: int = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    is_visible_on_home_page: bool = Form(False),
    display_order: int = Form(0),
    home_page_display_order: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Upload image to Cloudinary and save metadata to database
    Admin only endpoint
    """
    # Validate category exists
    category_query = select(GalleryCategory).where(GalleryCategory.id == category_id)
    category_result = await db.execute(category_query)
    category = category_result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Upload to Cloudinary
        cloudinary_response = cloudinary.uploader.upload(
            file.file,
            folder="gallery",
            resource_type="image",
            transformation=[
                {'quality': 'auto', 'fetch_format': 'auto'}
            ]
        )
        
        # Generate thumbnail URL
        thumbnail_url = cloudinary_response['secure_url'].replace(
            '/upload/',
            '/upload/w_400,h_300,c_fill,q_auto,f_auto/'
        )
        
        # Create database record
        new_image = GalleryImage(
            category_id=category_id,
            title=title,
            description=description,
            cloudinary_public_id=cloudinary_response['public_id'],
            cloudinary_url=cloudinary_response['secure_url'],
            cloudinary_thumbnail_url=thumbnail_url,
            uploaded_by=current_user.id,
            is_visible_on_home_page=is_visible_on_home_page,
            display_order=display_order,
            home_page_display_order=home_page_display_order
        )
        
        db.add(new_image)
        await db.commit()
        await db.refresh(new_image)
        
        return new_image
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.patch("/images/{image_id}/toggle-home-page", response_model=GalleryImageResponse)
async def toggle_home_page_visibility(
    image_id: int,
    request: GalleryImageToggleHomePageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Toggle whether image appears on home page carousel
    Admin only endpoint
    """
    query = select(GalleryImage).where(GalleryImage.id == image_id)
    result = await db.execute(query)
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image.is_visible_on_home_page = request.is_visible
    await db.commit()
    await db.refresh(image)
    
    return image


@router.put("/images/{image_id}", response_model=GalleryImageResponse)
async def update_gallery_image(
    image_id: int,
    image_update: GalleryImageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update gallery image metadata
    Validates that display_order is unique within the same category
    Admin only endpoint
    """
    # Get the image
    image = await db.get(GalleryImage, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Store original category_id for validation
    original_category_id = image.category_id
    target_category_id = image_update.category_id if image_update.category_id is not None else original_category_id

    # If display_order is being updated, check for duplicates within the same category
    if image_update.display_order is not None:
        # Check if another image in the same category has this display_order
        duplicate_query = select(GalleryImage).where(
            and_(
                GalleryImage.category_id == target_category_id,
                GalleryImage.display_order == image_update.display_order,
                GalleryImage.id != image_id  # Exclude current image
            )
        )
        duplicate_result = await db.execute(duplicate_query)
        duplicate_image = duplicate_result.scalar_one_or_none()

        if duplicate_image:
            raise HTTPException(
                status_code=400,
                detail=f"Display order {image_update.display_order} is already used by another image in this category. Please choose a different display order."
            )

    # If category is being changed, also validate display_order in new category
    if image_update.category_id is not None and image_update.category_id != original_category_id:
        # Verify new category exists
        new_category = await db.get(GalleryCategory, image_update.category_id)
        if not new_category:
            raise HTTPException(status_code=404, detail="Category not found")

        # Check if display_order conflicts in new category
        current_display_order = image_update.display_order if image_update.display_order is not None else image.display_order
        duplicate_query = select(GalleryImage).where(
            and_(
                GalleryImage.category_id == image_update.category_id,
                GalleryImage.display_order == current_display_order,
                GalleryImage.id != image_id
            )
        )
        duplicate_result = await db.execute(duplicate_query)
        duplicate_image = duplicate_result.scalar_one_or_none()

        if duplicate_image:
            raise HTTPException(
                status_code=400,
                detail=f"Display order {current_display_order} is already used by another image in the target category. Please choose a different display order."
            )

    # Update fields
    if image_update.category_id is not None:
        image.category_id = image_update.category_id
    if image_update.title is not None:
        image.title = image_update.title
    if image_update.description is not None:
        image.description = image_update.description
    if image_update.display_order is not None:
        image.display_order = image_update.display_order
    if image_update.is_active is not None:
        image.is_active = image_update.is_active
    if image_update.is_visible_on_home_page is not None:
        image.is_visible_on_home_page = image_update.is_visible_on_home_page
    if image_update.home_page_display_order is not None:
        image.home_page_display_order = image_update.home_page_display_order

    await db.commit()
    await db.refresh(image)

    return image


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gallery_image(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete image from Cloudinary and database
    Admin only endpoint
    """
    query = select(GalleryImage).where(GalleryImage.id == image_id)
    result = await db.execute(query)
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        # Delete from Cloudinary
        cloudinary.uploader.destroy(image.cloudinary_public_id)
        
        # Delete from database
        await db.delete(image)
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete image: {str(e)}"
        )


# =====================================================
# Statistics Endpoint
# =====================================================

@router.get("/statistics")
async def get_gallery_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get gallery statistics
    Admin only endpoint
    """
    # Total images
    total_query = select(func.count(GalleryImage.id))
    total_result = await db.execute(total_query)
    total_images = total_result.scalar()
    
    # Active images
    active_query = select(func.count(GalleryImage.id)).where(GalleryImage.is_active == True)
    active_result = await db.execute(active_query)
    active_images = active_result.scalar()
    
    # Home page images
    home_page_query = select(func.count(GalleryImage.id)).where(
        and_(
            GalleryImage.is_visible_on_home_page == True,
            GalleryImage.is_active == True
        )
    )
    home_page_result = await db.execute(home_page_query)
    home_page_images = home_page_result.scalar()
    
    # Total categories
    categories_query = select(func.count(GalleryCategory.id)).where(GalleryCategory.is_active == True)
    categories_result = await db.execute(categories_query)
    total_categories = categories_result.scalar()
    
    return {
        "total_images": total_images,
        "active_images": active_images,
        "home_page_images": home_page_images,
        "total_categories": total_categories
    }

