-- =====================================================
-- Quick Script: Add Description Columns
-- Run this script directly in your PostgreSQL database
-- =====================================================

-- Add description column to session_years table
ALTER TABLE session_years ADD COLUMN description TEXT;

-- Update existing session_years records
UPDATE session_years SET description = 'Academic session for ' || name;

-- Make description NOT NULL
ALTER TABLE session_years ALTER COLUMN description SET NOT NULL;

-- Add description column to classes table  
ALTER TABLE classes ADD COLUMN description TEXT;

-- Update existing classes records
UPDATE classes SET description = 'Academic class: ' || name;

-- Make description NOT NULL
ALTER TABLE classes ALTER COLUMN description SET NOT NULL;

-- Verify the changes
SELECT 'session_years' as table_name, id, name, description FROM session_years WHERE is_active = true ORDER BY id LIMIT 5;
SELECT 'classes' as table_name, id, name, description FROM classes WHERE is_active = true ORDER BY sort_order LIMIT 10;
