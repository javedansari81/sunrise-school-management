-- =====================================================
-- Fix Class Descriptions - Corrected Names
-- Run this to update the remaining class descriptions
-- =====================================================

-- Update classes with correct name matching
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
    -- Handle any other variations
    WHEN name LIKE 'Class %' THEN 'Academic class: ' || name
    ELSE description  -- Keep existing description if no match
END
WHERE name IN ('PG', 'NURSERY', 'CLASS_1', 'CLASS_2', 'CLASS_3', 'CLASS_4', 'CLASS_5', 
               'CLASS_6', 'CLASS_7', 'CLASS_8', 'CLASS_9', 'CLASS_10', 'CLASS_11', 'CLASS_12');

-- Verify the updates
SELECT id, name, description FROM classes WHERE is_active = true ORDER BY sort_order;
