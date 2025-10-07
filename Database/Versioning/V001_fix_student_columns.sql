-- =====================================================
-- Version: V001
-- Description: Add aadhar_no column to students table
-- Date: 2025-10-07
-- Changes:
--   1. Add aadhar_no column for storing 12-digit Aadhar identification number
-- =====================================================

-- Add aadhar_no column if it doesn't exist
ALTER TABLE students
ADD COLUMN IF NOT EXISTS aadhar_no VARCHAR(12);

-- Add comment for new column
COMMENT ON COLUMN students.aadhar_no IS '12-digit Aadhar identification number';

