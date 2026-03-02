-- V033: Add parent_called_at and parent_called_by fields to attendance_records
-- Purpose: Track when receptionist calls parents about student absences
-- This allows filtering out students who have been called within last 3 days

-- Add timestamp for when parent was called
ALTER TABLE attendance_records ADD COLUMN IF NOT EXISTS parent_called_at TIMESTAMP WITH TIME ZONE;

-- Add foreign key for who made the call
ALTER TABLE attendance_records ADD COLUMN IF NOT EXISTS parent_called_by INTEGER REFERENCES users(id);

-- Create index for efficient querying of recently called students
CREATE INDEX IF NOT EXISTS idx_attendance_records_parent_called_at 
ON attendance_records(parent_called_at) 
WHERE parent_called_at IS NOT NULL;

-- Add comment explaining the fields
COMMENT ON COLUMN attendance_records.parent_called_at IS 'Timestamp when receptionist called parent about this absence';
COMMENT ON COLUMN attendance_records.parent_called_by IS 'User ID of who called the parent';

