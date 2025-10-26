"""
Gallery models for image management
Stores gallery categories and image metadata (actual images stored in Cloudinary)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class GalleryCategory(Base):
    """Gallery category model (e.g., Independence Day, School Premises)"""
    __tablename__ = "gallery_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    images = relationship("GalleryImage", back_populates="category", cascade="all, delete-orphan")


class GalleryImage(Base):
    """Gallery image model - stores metadata, actual images in Cloudinary"""
    __tablename__ = "gallery_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("gallery_categories.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    cloudinary_public_id = Column(String(255), nullable=False, unique=True)
    cloudinary_url = Column(Text, nullable=False)
    cloudinary_thumbnail_url = Column(Text, nullable=True)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_visible_on_home_page = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("GalleryCategory", back_populates="images")
    uploader = relationship("User", foreign_keys=[uploaded_by])

