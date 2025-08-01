-- =====================================================
-- Update Descriptions with Detailed Information
-- Run this after the Quick_Add_Description_Columns.sql
-- =====================================================

-- Update session_years with detailed descriptions
UPDATE session_years 
SET description = CASE 
    WHEN name = '2022-23' THEN 'Academic session from April 2022 to March 2023'
    WHEN name = '2023-24' THEN 'Academic session from April 2023 to March 2024'
    WHEN name = '2024-25' THEN 'Academic session from April 2024 to March 2025'
    WHEN name = '2025-26' THEN 'Academic session from April 2025 to March 2026'
    WHEN name = '2026-27' THEN 'Academic session from April 2026 to March 2027'
    ELSE 'Academic session for ' || name
END;

-- Update classes with detailed descriptions
UPDATE classes 
SET description = CASE 
    WHEN name = 'PG' THEN 'Pre-primary education for ages 2-3 years'
    WHEN name = 'NURSERY' THEN 'Pre-primary education for ages 3-4 years'
    WHEN name = 'LKG' THEN 'Lower Kindergarten for ages 4-5 years'
    WHEN name = 'UKG' THEN 'Upper Kindergarten for ages 5-6 years'
    WHEN name = 'CLASS_1' THEN 'Primary education - Grade 1'
    WHEN name = 'CLASS_2' THEN 'Primary education - Grade 2'
    WHEN name = 'CLASS_3' THEN 'Primary education - Grade 3'
    WHEN name = 'CLASS_4' THEN 'Primary education - Grade 4'
    WHEN name = 'CLASS_5' THEN 'Primary education - Grade 5'
    WHEN name = 'CLASS_6' THEN 'Middle school - Grade 6'
    WHEN name = 'CLASS_7' THEN 'Middle school - Grade 7'
    WHEN name = 'CLASS_8' THEN 'Middle school - Grade 8'
    WHEN name = 'CLASS_9' THEN 'Secondary education - Grade 9'
    WHEN name = 'CLASS_10' THEN 'Secondary education - Grade 10'
    WHEN name = 'CLASS_11' THEN 'Higher secondary education - Grade 11'
    WHEN name = 'CLASS_12' THEN 'Higher secondary education - Grade 12'
    ELSE 'Academic class: ' || name
END;

-- Verify the updates
SELECT 'session_years' as table_name, id, name, description FROM session_years WHERE is_active = true ORDER BY id;
SELECT 'classes' as table_name, id, name, description FROM classes WHERE is_active = true ORDER BY sort_order;
