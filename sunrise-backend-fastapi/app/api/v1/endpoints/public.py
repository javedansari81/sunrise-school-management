from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import json

from app.core.database import get_db
from app.crud import teacher_crud
from app.models.gallery import GalleryCategory, GalleryImage
from app.schemas.gallery import PublicGalleryCategory, PublicGalleryImage

router = APIRouter()


@router.get("/faculty", response_model=Dict[str, Any])
async def get_public_faculty(
    db: AsyncSession = Depends(get_db)
):
    """
    Get active teachers for public Faculty page display
    No authentication required - public endpoint
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        logger.info("Public faculty endpoint called")

        # Get only active teachers with basic information for public display
        teachers, total = await teacher_crud.get_multi_with_filters(
            db,
            skip=0,
            limit=100,  # Get up to 100 teachers for faculty page
            is_active=True
        )

        logger.info(f"Retrieved {len(teachers)} teachers from database")
        
        # Filter and format data for public display
        public_teachers = []
        for teacher in teachers:
            # Parse subjects JSON if it exists
            subjects_list = []
            if teacher.get('subjects'):
                try:
                    subjects_list = json.loads(teacher['subjects'])
                except (json.JSONDecodeError, TypeError):
                    subjects_list = []

            # Create public teacher profile
            public_teacher = {
                "id": teacher["id"],
                "full_name": f"{teacher['first_name']} {teacher['last_name']}",
                "first_name": teacher["first_name"],
                "last_name": teacher["last_name"],
                "employee_id": teacher["employee_id"],
                "position": teacher.get("position_description"),  # Use description for human-readable text
                "department": teacher.get("department_description"),  # Use description for human-readable text
                "subjects": subjects_list,
                "experience_years": teacher.get("experience_years", 0),
                "qualification_name": teacher.get("qualification_description"),  # Use description for consistency
                "joining_date": teacher.get("joining_date"),
                "email": teacher.get("email"),  # Include email for contact
                "phone": teacher.get("phone"),  # Include phone for contact
            }
            public_teachers.append(public_teacher)
        
        # Group teachers by department for better organization
        departments = {}
        for teacher in public_teachers:
            dept = teacher.get("department") or "General"
            if dept not in departments:
                departments[dept] = []
            departments[dept].append(teacher)
        
        return {
            "teachers": public_teachers,
            "departments": departments,
            "total": len(public_teachers),
            "message": "Faculty information retrieved successfully"
        }
    
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Error in get_public_faculty: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

        return {
            "teachers": [],
            "departments": {},
            "total": 0,
            "error": str(e),
            "message": "Failed to retrieve faculty information"
        }


@router.get("/health")
async def public_health_check():
    """
    Simple health check endpoint for public API
    """
    return {"status": "ok", "message": "Public API is working"}


@router.get("/gallery", response_model=List[PublicGalleryCategory])
async def get_public_gallery(
    limit_categories: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get gallery images grouped by category for public display
    Returns only active categories and active images
    Public endpoint - no authentication required

    Args:
        limit_categories: Optional limit on number of categories to return (for lazy loading)
    """
    # Get active categories ordered by display_order
    category_query = select(GalleryCategory).where(
        GalleryCategory.is_active == True
    ).order_by(GalleryCategory.display_order.asc())

    if limit_categories:
        category_query = category_query.limit(limit_categories)

    category_result = await db.execute(category_query)
    categories = category_result.scalars().all()

    # For each category, get active images
    result = []
    for category in categories:
        image_query = select(GalleryImage).where(
            and_(
                GalleryImage.category_id == category.id,
                GalleryImage.is_active == True
            )
        ).order_by(
            GalleryImage.display_order.asc(),
            GalleryImage.upload_date.desc()
        )

        image_result = await db.execute(image_query)
        images = image_result.scalars().all()

        # Convert to response format
        category_dict = {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'icon': category.icon,
            'display_order': category.display_order,
            'images': [
                {
                    'id': img.id,
                    'title': img.title,
                    'description': img.description,
                    'cloudinary_url': img.cloudinary_url,
                    'cloudinary_thumbnail_url': img.cloudinary_thumbnail_url,
                    'display_order': img.display_order,
                    'upload_date': img.upload_date
                }
                for img in images
            ]
        }
        result.append(category_dict)

    return result


@router.get("/gallery/home-page", response_model=List[PublicGalleryImage])
async def get_public_home_page_images(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get featured images for home page carousel
    Returns images where is_visible_on_home_page = TRUE
    Public endpoint - no authentication required

    Args:
        limit: Maximum number of images to return (default: 10)
    """
    query = select(GalleryImage).join(GalleryCategory).where(
        and_(
            GalleryImage.is_visible_on_home_page == True,
            GalleryImage.is_active == True,
            GalleryCategory.is_active == True
        )
    ).order_by(
        GalleryImage.display_order.asc(),
        GalleryImage.upload_date.desc()
    ).limit(limit)

    result = await db.execute(query)
    images = result.scalars().all()

    # Convert to response format
    response_images = [
        {
            'id': img.id,
            'title': img.title,
            'description': img.description,
            'cloudinary_url': img.cloudinary_url,
            'cloudinary_thumbnail_url': img.cloudinary_thumbnail_url,
            'display_order': img.display_order,
            'upload_date': img.upload_date
        }
        for img in images
    ]

    return response_images
