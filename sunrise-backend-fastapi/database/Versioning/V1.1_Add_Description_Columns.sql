-- =====================================================
-- Database Schema Update: Add Description Columns
-- Version: 1.1
-- Date: 2025-08-01
-- Description: Add missing description columns to tables for metadata consistency
-- =====================================================

-- Start transaction
BEGIN;

-- =====================================================
-- 1. Add description column to session_years table
-- =====================================================
ALTER TABLE session_years 
ADD COLUMN description TEXT;

-- Update existing records with meaningful descriptions
UPDATE session_years 
SET description = CASE 
    WHEN name = '2022-23' THEN 'Academic session from April 2022 to March 2023'
    WHEN name = '2023-24' THEN 'Academic session from April 2023 to March 2024'
    WHEN name = '2024-25' THEN 'Academic session from April 2024 to March 2025'
    WHEN name = '2025-26' THEN 'Academic session from April 2025 to March 2026'
    WHEN name = '2026-27' THEN 'Academic session from April 2026 to March 2027'
    ELSE 'Academic session for ' || name
END;

-- Make description column NOT NULL after updating existing records
ALTER TABLE session_years 
ALTER COLUMN description SET NOT NULL;

-- =====================================================
-- 2. Add description column to classes table
-- =====================================================
ALTER TABLE classes 
ADD COLUMN description TEXT;

-- Update existing records with meaningful descriptions
UPDATE classes 
SET description = CASE 
    WHEN name = 'Nursery' THEN 'Pre-primary education for ages 3-4 years'
    WHEN name = 'LKG' THEN 'Lower Kindergarten for ages 4-5 years'
    WHEN name = 'UKG' THEN 'Upper Kindergarten for ages 5-6 years'
    WHEN name = 'Class 1' THEN 'Primary education - Grade 1'
    WHEN name = 'Class 2' THEN 'Primary education - Grade 2'
    WHEN name = 'Class 3' THEN 'Primary education - Grade 3'
    WHEN name = 'Class 4' THEN 'Primary education - Grade 4'
    WHEN name = 'Class 5' THEN 'Primary education - Grade 5'
    WHEN name = 'Class 6' THEN 'Middle school - Grade 6'
    WHEN name = 'Class 7' THEN 'Middle school - Grade 7'
    WHEN name = 'Class 8' THEN 'Middle school - Grade 8'
    WHEN name = 'Class 9' THEN 'Secondary education - Grade 9'
    WHEN name = 'Class 10' THEN 'Secondary education - Grade 10'
    WHEN name = 'Class 11' THEN 'Higher secondary education - Grade 11'
    WHEN name = 'Class 12' THEN 'Higher secondary education - Grade 12'
    ELSE 'Academic class: ' || name
END;

-- Make description column NOT NULL after updating existing records
ALTER TABLE classes 
ALTER COLUMN description SET NOT NULL;

-- =====================================================
-- 3. Verify the changes
-- =====================================================

-- Check session_years table structure and data
SELECT 'session_years' as table_name, 
       column_name, 
       data_type, 
       is_nullable 
FROM information_schema.columns 
WHERE table_name = 'session_years' 
  AND table_schema = 'public'
ORDER BY ordinal_position;

-- Check classes table structure and data
SELECT 'classes' as table_name, 
       column_name, 
       data_type, 
       is_nullable 
FROM information_schema.columns 
WHERE table_name = 'classes' 
  AND table_schema = 'public'
ORDER BY ordinal_position;

-- Sample data verification
SELECT 'session_years_sample' as info, id, name, description, is_active 
FROM session_years 
WHERE is_active = true 
ORDER BY id 
LIMIT 5;

SELECT 'classes_sample' as info, id, name, description, display_name, sort_order, is_active 
FROM classes 
WHERE is_active = true 
ORDER BY sort_order 
LIMIT 10;

-- =====================================================
-- 4. Update table comments for documentation
-- =====================================================

COMMENT ON COLUMN session_years.description IS 'Detailed description of the academic session period';
COMMENT ON COLUMN classes.description IS 'Detailed description of the academic class/grade level';

-- Commit transaction
COMMIT;

-- =====================================================
-- Rollback script (for reference - DO NOT RUN)
-- =====================================================
/*
-- To rollback these changes if needed:
BEGIN;
ALTER TABLE session_years DROP COLUMN IF EXISTS description;
ALTER TABLE classes DROP COLUMN IF EXISTS description;
COMMIT;
*/

-- =====================================================
-- Verification queries to run after execution
-- =====================================================
/*
-- Run these queries to verify the changes:

-- 1. Check if columns were added successfully
SELECT table_name, column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name IN ('session_years', 'classes') 
  AND column_name = 'description'
  AND table_schema = 'public';

-- 2. Check sample data
SELECT id, name, description FROM session_years WHERE is_active = true ORDER BY id;
SELECT id, name, description, display_name FROM classes WHERE is_active = true ORDER BY sort_order;

-- 3. Test the metadata UNION query
SELECT 'session_years' as table_name, id, name, description, NULL::VARCHAR as display_name,
       NULL::INTEGER as sort_order, start_date, end_date, is_current,
       NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, 
       NULL::DECIMAL as budget_limit, NULL::BOOLEAN as requires_approval, 
       NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
       NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
FROM session_years WHERE is_active = true
UNION ALL
SELECT 'classes' as table_name, id, name, description, display_name,
       sort_order, NULL::DATE as start_date, NULL::DATE as end_date, NULL::BOOLEAN as is_current,
       NULL::INTEGER as max_days_per_year, NULL::BOOLEAN as requires_medical_certificate, 
       NULL::DECIMAL as budget_limit, NULL::BOOLEAN as requires_approval, 
       NULL::VARCHAR as color_code, NULL::BOOLEAN as is_final, NULL::INTEGER as level_order,
       NULL::BOOLEAN as requires_reference, is_active, created_at, updated_at
FROM classes WHERE is_active = true
ORDER BY table_name, id;
*/
