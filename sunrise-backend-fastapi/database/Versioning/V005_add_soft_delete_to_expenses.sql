-- V005: Add soft delete columns to expenses table
-- This script adds is_active, is_deleted and deleted_date columns for soft delete functionality

-- Add is_active column (boolean, defaults to true for existing records)
ALTER TABLE expenses
ADD COLUMN "is_active" BOOLEAN NOT NULL DEFAULT TRUE;

-- Add is_deleted column (boolean, nullable, defaults to false for existing records)
ALTER TABLE expenses
ADD COLUMN "is_deleted" BOOLEAN NULL DEFAULT FALSE;

-- Add deleted_date column (timestamp, nullable)
ALTER TABLE expenses
ADD COLUMN "deleted_date" TIMESTAMP WITH TIME ZONE NULL;

-- Update existing records to have proper values (for consistency)
UPDATE expenses
SET "is_active" = TRUE, "is_deleted" = FALSE
WHERE "is_active" IS NULL OR "is_deleted" IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN expenses."is_active" IS 'Active status flag - true if record is active, false if deactivated';
COMMENT ON COLUMN expenses."is_deleted" IS 'Soft delete flag - true if record is deleted, false if active';
COMMENT ON COLUMN expenses."deleted_date" IS 'Timestamp when record was soft deleted, NULL if not deleted';

-- Create indexes for better performance on soft delete queries
CREATE INDEX idx_expenses_is_active ON expenses("is_active");
CREATE INDEX idx_expenses_is_deleted ON expenses("is_deleted");
CREATE INDEX idx_expenses_deleted_date ON expenses("deleted_date");

-- Create composite index for common queries (active and not deleted)
CREATE INDEX idx_expenses_active_not_deleted ON expenses("is_active", "is_deleted") 
WHERE "is_active" = TRUE AND ("is_deleted" = FALSE OR "is_deleted" IS NULL);
