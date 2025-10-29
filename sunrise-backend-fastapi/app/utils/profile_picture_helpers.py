"""
Profile Picture Upload Helpers
Handles profile picture upload, validation, and deletion for students and teachers
"""

from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status
import cloudinary
import cloudinary.uploader
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cloudinary_config import configure_cloudinary

# Ensure Cloudinary is configured
configure_cloudinary()

# Constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_CONTENT_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']


async def validate_profile_picture(file: UploadFile) -> None:
    """
    Validate profile picture file
    
    Args:
        file: Uploaded file
        
    Raises:
        HTTPException: If validation fails
    """
    # Validate file type
    if not file.content_type or file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )
    
    # Read file to check size
    contents = await file.read()
    file_size = len(contents)
    
    # Reset file pointer
    await file.seek(0)
    
    # Validate file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024 * 1024)}MB"
        )


async def upload_profile_picture_to_cloudinary(
    file: UploadFile,
    folder: str,
    identifier: str
) -> Tuple[str, str]:
    """
    Upload profile picture to Cloudinary
    
    Args:
        file: Uploaded file
        folder: Cloudinary folder (e.g., 'profiles/students' or 'profiles/teachers')
        identifier: Unique identifier for the file (e.g., student_id or teacher_id)
        
    Returns:
        Tuple of (cloudinary_url, cloudinary_public_id)
        
    Raises:
        HTTPException: If upload fails
    """
    try:
        # Upload to Cloudinary with transformations
        cloudinary_response = cloudinary.uploader.upload(
            file.file,
            folder=folder,
            public_id=f"{identifier}_{file.filename}",
            resource_type="image",
            transformation=[
                {
                    'width': 400,
                    'height': 400,
                    'crop': 'fill',
                    'gravity': 'face'  # Smart crop focusing on faces
                },
                {
                    'quality': 'auto',
                    'fetch_format': 'auto'
                }
            ],
            overwrite=True  # Overwrite if exists
        )
        
        return cloudinary_response['secure_url'], cloudinary_response['public_id']
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload profile picture: {str(e)}"
        )


async def delete_profile_picture_from_cloudinary(public_id: str) -> bool:
    """
    Delete profile picture from Cloudinary
    
    Args:
        public_id: Cloudinary public ID of the image
        
    Returns:
        True if deletion was successful, False otherwise
    """
    if not public_id:
        return False
        
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type="image")
        return result.get('result') == 'ok'
    except Exception as e:
        # Log error but don't raise exception
        print(f"Failed to delete profile picture from Cloudinary: {str(e)}")
        return False


async def update_student_profile_picture(
    db: AsyncSession,
    student_id: int,
    profile_picture_url: Optional[str],
    profile_picture_cloudinary_id: Optional[str]
) -> None:
    """
    Update student profile picture in database
    
    Args:
        db: Database session
        student_id: Student ID
        profile_picture_url: New profile picture URL (None to remove)
        profile_picture_cloudinary_id: New Cloudinary public ID (None to remove)
    """
    from app.models.student import Student
    from sqlalchemy import select
    
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    student.profile_picture_url = profile_picture_url
    student.profile_picture_cloudinary_id = profile_picture_cloudinary_id
    
    await db.commit()
    await db.refresh(student)


async def update_teacher_profile_picture(
    db: AsyncSession,
    teacher_id: int,
    profile_picture_url: Optional[str],
    profile_picture_cloudinary_id: Optional[str]
) -> None:
    """
    Update teacher profile picture in database
    
    Args:
        db: Database session
        teacher_id: Teacher ID
        profile_picture_url: New profile picture URL (None to remove)
        profile_picture_cloudinary_id: New Cloudinary public ID (None to remove)
    """
    from app.models.teacher import Teacher
    from sqlalchemy import select
    
    result = await db.execute(
        select(Teacher).where(Teacher.id == teacher_id)
    )
    teacher = result.scalar_one_or_none()
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    teacher.profile_picture_url = profile_picture_url
    teacher.profile_picture_cloudinary_id = profile_picture_cloudinary_id
    
    await db.commit()
    await db.refresh(teacher)

