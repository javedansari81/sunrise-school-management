-- V004: Add soft delete columns to students table
-- This script adds is_deleted and deleted_date columns for soft delete functionality

-- Add is_deleted column (boolean, nullable, defaults to false for existing records)
ALTER TABLE students
ADD COLUMN "is_deleted" BOOLEAN NULL DEFAULT FALSE;

-- Add deleted_date column (timestamp, nullable)
ALTER TABLE students
ADD COLUMN "deleted_date" TIMESTAMP NULL;

-- Update existing records to have is_deleted = false (for consistency)
UPDATE students
SET "is_deleted" = FALSE
WHERE "is_deleted" IS NULL;

-- Add comment for documentation
COMMENT ON COLUMN students."is_deleted" IS 'Soft delete flag - true if record is deleted, false if active';
COMMENT ON COLUMN students."deleted_date" IS 'Timestamp when record was soft deleted, NULL if not deleted';

-- Create index for better performance on soft delete queries
CREATE INDEX idx_students_is_deleted ON students("is_deleted");
CREATE INDEX idx_students_deleted_date ON students("deleted_date");
