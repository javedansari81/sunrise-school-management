"""
Cloudinary Configuration Module
Initializes Cloudinary SDK with credentials from environment variables
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.core.config import settings


def configure_cloudinary():
    """
    Configure Cloudinary with credentials from settings
    """
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )


# Initialize Cloudinary on module import
configure_cloudinary()

