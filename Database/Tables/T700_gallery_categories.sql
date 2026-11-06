-- =====================================================
-- Table: gallery_categories
-- Description: Stores gallery category definitions (Independence Day, School Premises, etc.)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS gallery_categories CASCADE;

-- Create table
CREATE TABLE gallery_categories (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE gallery_categories IS 'Gallery category definitions (events, locations, activities)';
COMMENT ON COLUMN gallery_categories.id IS 'Primary key - auto-generated';
COMMENT ON COLUMN gallery_categories.name IS 'Unique category name (e.g., Independence Day, School Premises)';
COMMENT ON COLUMN gallery_categories.description IS 'Human-readable description of the category';
COMMENT ON COLUMN gallery_categories.icon IS 'Material-UI icon name for display';
COMMENT ON COLUMN gallery_categories.display_order IS 'Order for displaying categories (lower = first)';
COMMENT ON COLUMN gallery_categories.is_active IS 'Flag to show/hide category';

-- Create indexes
CREATE INDEX idx_gallery_categories_active ON gallery_categories(is_active);
CREATE INDEX idx_gallery_categories_display_order ON gallery_categories(display_order);

-- Multi-tenancy: every row belongs to one school
CREATE INDEX IF NOT EXISTS idx_gallery_categories_school_id ON gallery_categories (school_id);
CREATE UNIQUE INDEX IF NOT EXISTS gallery_categories_school_name_unique ON gallery_categories (school_id, name);
COMMENT ON COLUMN gallery_categories.school_id IS 'School (tenant) this row belongs to';
