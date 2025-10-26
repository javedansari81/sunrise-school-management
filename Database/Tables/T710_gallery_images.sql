-- =====================================================
-- Table: gallery_images
-- Description: Stores gallery image metadata (actual images stored in Cloudinary)
-- Dependencies: gallery_categories, users
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS gallery_images CASCADE;

-- Create table
CREATE TABLE gallery_images (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES gallery_categories(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    cloudinary_public_id VARCHAR(255) NOT NULL UNIQUE,
    cloudinary_url TEXT NOT NULL,
    cloudinary_thumbnail_url TEXT,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_visible_on_home_page BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE gallery_images IS 'Gallery image metadata (images stored in Cloudinary CDN)';
COMMENT ON COLUMN gallery_images.id IS 'Primary key - auto-generated';
COMMENT ON COLUMN gallery_images.category_id IS 'Foreign key to gallery_categories';
COMMENT ON COLUMN gallery_images.title IS 'Image title/caption';
COMMENT ON COLUMN gallery_images.description IS 'Detailed description of the image';
COMMENT ON COLUMN gallery_images.cloudinary_public_id IS 'Unique Cloudinary identifier for the image';
COMMENT ON COLUMN gallery_images.cloudinary_url IS 'Full Cloudinary URL for original image';
COMMENT ON COLUMN gallery_images.cloudinary_thumbnail_url IS 'Optimized thumbnail URL for faster loading';
COMMENT ON COLUMN gallery_images.uploaded_by IS 'User ID who uploaded the image';
COMMENT ON COLUMN gallery_images.display_order IS 'Order for displaying images (lower = first)';
COMMENT ON COLUMN gallery_images.is_active IS 'Flag to show/hide image in gallery';
COMMENT ON COLUMN gallery_images.is_visible_on_home_page IS 'Flag to display image on home page carousel/slider';

-- Create indexes
CREATE INDEX idx_gallery_images_category ON gallery_images(category_id);
CREATE INDEX idx_gallery_images_active ON gallery_images(is_active);
CREATE INDEX idx_gallery_images_home_page ON gallery_images(is_visible_on_home_page);
CREATE INDEX idx_gallery_images_display_order ON gallery_images(display_order);
CREATE INDEX idx_gallery_images_upload_date ON gallery_images(upload_date DESC);

-- Create composite index for home page queries
CREATE INDEX idx_gallery_images_home_page_active ON gallery_images(is_visible_on_home_page, is_active, display_order);

