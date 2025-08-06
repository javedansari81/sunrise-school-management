from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.core.database import get_db
from app.crud import teacher_crud

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
                "position": teacher["position"],
                "department": teacher.get("department"),
                "subjects": subjects_list,
                "experience_years": teacher.get("experience_years", 0),
                "qualification_name": teacher.get("qualification_name"),
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
