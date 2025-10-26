"""
Pydantic schemas for gallery models
These schemas are used for API requests/responses and validation
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# =====================================================
# Gallery Category Schemas
# =====================================================

class GalleryCategoryBase(BaseModel):
    """Base schema for gallery category"""
    name: str = Field(..., max_length=100, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    icon: Optional[str] = Field(None, max_length=50, description="Material-UI icon name")
    display_order: int = Field(0, description="Display order (lower = first)")
    is_active: bool = Field(True, description="Active status")


class GalleryCategoryCreate(GalleryCategoryBase):
    """Schema for creating a gallery category"""
    pass


class GalleryCategoryUpdate(BaseModel):
    """Schema for updating a gallery category"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class GalleryCategoryResponse(GalleryCategoryBase):
    """Schema for gallery category response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =====================================================
# Gallery Image Schemas
# =====================================================

class GalleryImageBase(BaseModel):
    """Base schema for gallery image"""
    category_id: int = Field(..., description="Category ID")
    title: str = Field(..., max_length=200, description="Image title")
    description: Optional[str] = Field(None, description="Image description")
    display_order: int = Field(0, description="Display order (lower = first)")
    is_active: bool = Field(True, description="Active status")
    is_visible_on_home_page: bool = Field(False, description="Show on home page carousel")


class GalleryImageCreate(GalleryImageBase):
    """Schema for creating a gallery image (used internally after upload)"""
    cloudinary_public_id: str = Field(..., max_length=255)
    cloudinary_url: str
    cloudinary_thumbnail_url: Optional[str] = None
    uploaded_by: Optional[int] = None


class GalleryImageUpdate(BaseModel):
    """Schema for updating a gallery image"""
    category_id: Optional[int] = None
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None
    is_visible_on_home_page: Optional[bool] = None


class GalleryImageResponse(GalleryImageBase):
    """Schema for gallery image response"""
    id: int
    cloudinary_public_id: str
    cloudinary_url: str
    cloudinary_thumbnail_url: Optional[str] = None
    upload_date: datetime
    uploaded_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GalleryImageWithCategory(GalleryImageResponse):
    """Schema for gallery image with category details"""
    category: GalleryCategoryResponse
    category_name: Optional[str] = Field(None, description="Category name for display")
    uploaded_by_name: Optional[str] = Field(None, description="Uploader name for display")

    class Config:
        from_attributes = True


# =====================================================
# Upload Schemas
# =====================================================

class GalleryImageUploadRequest(BaseModel):
    """Schema for image upload request (form data)"""
    category_id: int = Field(..., description="Category ID")
    title: str = Field(..., max_length=200, description="Image title")
    description: Optional[str] = Field(None, description="Image description")
    is_visible_on_home_page: bool = Field(False, description="Show on home page")


class GalleryImageToggleHomePageRequest(BaseModel):
    """Schema for toggling home page visibility"""
    is_visible: bool = Field(..., description="Visibility on home page")


# =====================================================
# Public Gallery Schemas
# =====================================================

class PublicGalleryImage(BaseModel):
    """Schema for public gallery image (simplified)"""
    id: int
    title: str
    description: Optional[str] = None
    cloudinary_url: str
    cloudinary_thumbnail_url: Optional[str] = None
    display_order: int
    upload_date: datetime

    class Config:
        from_attributes = True


class PublicGalleryCategory(BaseModel):
    """Schema for public gallery category with images"""
    id: int
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    display_order: int
    images: List[PublicGalleryImage] = []

    class Config:
        from_attributes = True


# =====================================================
# Configuration Schema (for frontend)
# =====================================================

class GalleryConfigurationResponse(BaseModel):
    """Schema for gallery configuration endpoint"""
    categories: list[GalleryCategoryResponse]

    class Config:
        from_attributes = True

