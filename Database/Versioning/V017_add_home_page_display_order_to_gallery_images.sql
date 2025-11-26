-- =====================================================
-- Migration: V017_add_home_page_display_order_to_gallery_images
-- Description: Add home_page_display_order column to gallery_images table
--              to separate home page carousel ordering from category-based ordering
-- Date: 2025-11-26
-- =====================================================

-- Add the new column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'gallery_images' 
        AND column_name = 'home_page_display_order'
    ) THEN
        ALTER TABLE gallery_images 
        ADD COLUMN home_page_display_order INTEGER DEFAULT NULL;
        
        RAISE NOTICE 'Column home_page_display_order added to gallery_images table';
    ELSE
        RAISE NOTICE 'Column home_page_display_order already exists in gallery_images table';
    END IF;
END $$;

-- Add comment for the new column
COMMENT ON COLUMN gallery_images.home_page_display_order IS 'Order for displaying images on home page carousel (lower = first) - used for home page sorting only. NULL values appear after explicit ordering';

-- Update the comment for display_order to clarify its purpose
COMMENT ON COLUMN gallery_images.display_order IS 'Order for displaying images within their category (lower = first) - used for category-based sorting only';

-- Create index for the new column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'gallery_images' 
        AND indexname = 'idx_gallery_images_home_page_display_order'
    ) THEN
        CREATE INDEX idx_gallery_images_home_page_display_order 
        ON gallery_images(home_page_display_order);
        
        RAISE NOTICE 'Index idx_gallery_images_home_page_display_order created';
    ELSE
        RAISE NOTICE 'Index idx_gallery_images_home_page_display_order already exists';
    END IF;
END $$;

-- Drop old composite index if it exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'gallery_images' 
        AND indexname = 'idx_gallery_images_home_page_active'
    ) THEN
        DROP INDEX idx_gallery_images_home_page_active;
        RAISE NOTICE 'Old composite index idx_gallery_images_home_page_active dropped';
    END IF;
END $$;

-- Create new optimized composite index for home page queries
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'gallery_images' 
        AND indexname = 'idx_gallery_images_home_page_active'
    ) THEN
        CREATE INDEX idx_gallery_images_home_page_active 
        ON gallery_images(is_visible_on_home_page, is_active, home_page_display_order, upload_date DESC);
        
        RAISE NOTICE 'New composite index idx_gallery_images_home_page_active created with home_page_display_order';
    ELSE
        RAISE NOTICE 'Composite index idx_gallery_images_home_page_active already exists';
    END IF;
END $$;

-- Verification and completion message
DO $$
DECLARE
    col_count INTEGER;
    idx_count INTEGER;
BEGIN
    -- Check columns (verify new column was added)
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_name = 'gallery_images'
    AND column_name = 'home_page_display_order';

    RAISE NOTICE 'Found % home_page_display_order column in gallery_images table', col_count;

    -- Check indexes
    SELECT COUNT(*) INTO idx_count
    FROM pg_indexes
    WHERE tablename = 'gallery_images'
    AND indexname SIMILAR TO '%(display_order|home_page)%';

    RAISE NOTICE 'Found % display order indexes on gallery_images table', idx_count;

    RAISE NOTICE 'Migration V017 completed successfully';
END $$;

-- Display column details for verification
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'gallery_images'
AND column_name = 'home_page_display_order'
ORDER BY column_name;

-- Display index details for verification
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'gallery_images'
AND indexname LIKE '%display_order%'
ORDER BY indexname;

