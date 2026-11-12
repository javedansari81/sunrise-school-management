from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import json

from app.core.database import get_db
from app.api.deps import get_school_db
from app.crud import teacher_crud
from app.models.gallery import GalleryCategory, GalleryImage
from app.schemas.gallery import PublicGalleryCategory, PublicGalleryImage

router = APIRouter()


@router.get("/school")
async def get_public_school(request: Request, db: AsyncSession = Depends(get_school_db)):
    """
    Name, logo and contact details of the school this request is for (by
    subdomain or X-School-Code). The frontend brands itself with it before login.
    """
    school = request.state.school
    return {
        "code": school.code,
        "name": school.name,
        "short_name": school.short_name,
        "logo_url": school.logo_url,
        "address": school.address,
        "phone": school.phone,
        "email": school.email,
        "website": school.website,
        "currency": school.currency,
    }

@router.get("/fee-structure")
async def get_public_fee_structure(db: AsyncSession = Depends(get_school_db)):
    """
    What a new student pays per class, from the fee structure published for the
    school's current session. Shown on the public Admissions page.
    """
    from decimal import Decimal

    from app.models.metadata import Class, SessionYear
    from app.modules.fees import repository as fee_repo
    from app.modules.fees.audit import to_json
    from app.modules.fees.constants import AppliesTo, Frequency
    from app.modules.fees.models import FeeHead

    year = (await db.execute(select(SessionYear).where(SessionYear.is_current == True))).scalars().first()  # noqa: E712
    structure = await fee_repo.published_structure(db, year.id) if year else None
    if structure is None:
        return {"session_year": year.name if year else None, "classes": []}

    heads = {h.id: h for h in (await db.execute(select(FeeHead))).scalars()}
    # Per head: the price of a class, else the price for every class (as billing does)
    by_head: Dict[int, Dict[Optional[int], Any]] = {}
    for item in structure.items:
        if item.applies_to != AppliesTo.EXISTING_STUDENTS.value:
            by_head.setdefault(item.fee_head_id, {})[item.class_id] = item
    times = {Frequency.MONTHLY.value: 12, Frequency.QUARTERLY.value: 4, Frequency.HALF_YEARLY.value: 2}

    classes = (await db.execute(
        select(Class).where(Class.is_active == True).order_by(Class.sort_order, Class.id)  # noqa: E712
    )).scalars().all()
    rows = []
    for klass in classes:
        fees, monthly, one_time, first_year = [], Decimal("0"), Decimal("0"), Decimal("0")
        for head_id, prices in by_head.items():
            item, head = prices.get(klass.id) or prices.get(None), heads.get(head_id)
            if item is None or head is None:
                continue
            count = len(item.billing_months) if item.billing_months else times.get(item.frequency, 1)
            if item.frequency == Frequency.MONTHLY.value:
                monthly += item.amount
            elif item.frequency == Frequency.ONE_TIME.value:
                one_time += item.amount
            first_year += item.amount * count
            fees.append({"name": head.name, "amount": item.amount, "frequency": item.frequency, "sort": head.sort_order})
        if fees:
            fees.sort(key=lambda f: f.pop("sort"))
            rows.append({"class_id": klass.id, "class_name": klass.description or klass.name, "monthly": monthly,
                         "one_time": one_time, "first_year_total": first_year, "fees": fees})
    return to_json({"session_year": year.name, "classes": rows})


@router.get("/faculty", response_model=Dict[str, Any])
async def get_public_faculty(
    db: AsyncSession = Depends(get_school_db)
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
                "position": teacher.get("position_description"),  # Use description for human-readable text
                "department": teacher.get("department_description"),  # Use description for human-readable text
                "department_id": teacher.get("department_id"),  # Include department ID
                "subjects": subjects_list,
                "experience_years": teacher.get("experience_years", 0),
                "qualification_name": teacher.get("qualification_description"),  # Use description for consistency
                "joining_date": teacher.get("joining_date"),
                "email": teacher.get("email"),  # Include email for contact
                "profile_picture_url": teacher.get("profile_picture_url"),  # Include profile picture
            }
            public_teachers.append(public_teacher)
        
        # Group teachers by department for better organization
        departments = {}
        department_stats = []

        for teacher in public_teachers:
            dept = teacher.get("department") or "General"
            dept_id = teacher.get("department_id")

            if dept not in departments:
                departments[dept] = []
            departments[dept].append(teacher)

        # Create department statistics with unique subjects
        for dept_name, dept_teachers in departments.items():
            # Get unique subjects across all teachers in this department
            all_subjects = []
            for t in dept_teachers:
                all_subjects.extend(t.get("subjects", []))
            unique_subjects = list(set(all_subjects))

            # Get department ID from first teacher
            dept_id = dept_teachers[0].get("department_id") if dept_teachers else None

            department_stats.append({
                "id": dept_id,
                "name": dept_name,
                "faculty_count": len(dept_teachers),
                "subjects": unique_subjects,
                "description": f"Our {dept_name} comprises {len(dept_teachers)} dedicated faculty members teaching {len(unique_subjects)} subjects."
            })

        return {
            "teachers": public_teachers,
            "departments": departments,
            "department_stats": department_stats,
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
    db: AsyncSession = Depends(get_school_db)
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
    db: AsyncSession = Depends(get_school_db)
):
    """
    Get featured images for home page carousel
    Returns images where is_visible_on_home_page = TRUE
    Ordered by home_page_display_order (NULL values appear last), then upload_date
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
        GalleryImage.home_page_display_order.asc().nulls_last(),
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
            'home_page_display_order': img.home_page_display_order,
            'upload_date': img.upload_date
        }
        for img in images
    ]

    return response_images
