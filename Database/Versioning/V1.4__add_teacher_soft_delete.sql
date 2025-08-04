-- =====================================================
-- Teacher Soft Delete Support Migration
-- Version: 1.4
-- Description: Add soft delete columns to teachers table
-- =====================================================

-- Add soft delete columns to teachers table
ALTER TABLE teachers 
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS deleted_date TIMESTAMP WITH TIME ZONE;

-- Create index for soft delete queries
CREATE INDEX IF NOT EXISTS idx_teachers_is_deleted ON teachers(is_deleted) WHERE is_deleted IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_teachers_deleted_date ON teachers(deleted_date) WHERE deleted_date IS NOT NULL;

-- Create composite index for active teachers (most common query)
CREATE INDEX IF NOT EXISTS idx_teachers_active_not_deleted ON teachers(is_active, is_deleted) 
WHERE is_active = TRUE AND (is_deleted IS NULL OR is_deleted = FALSE);

-- Update existing records to ensure is_deleted is FALSE for active teachers
UPDATE teachers 
SET is_deleted = FALSE 
WHERE is_deleted IS NULL AND is_active = TRUE;

-- Comments
COMMENT ON COLUMN teachers.is_deleted IS 'Soft delete flag - TRUE when teacher is deleted but record is preserved';
COMMENT ON COLUMN teachers.deleted_date IS 'Timestamp when teacher was soft deleted';
