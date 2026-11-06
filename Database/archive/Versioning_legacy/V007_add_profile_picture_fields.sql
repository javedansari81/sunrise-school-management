-- =====================================================
-- Version: V007
-- Description: Add profile picture fields to students and teachers tables
-- Dependencies: T310_students.sql, T320_teachers.sql
-- Author: System
-- Date: 2025-10-28
-- =====================================================

-- Add profile picture fields to students table
ALTER TABLE students 
ADD COLUMN IF NOT EXISTS profile_picture_url TEXT,
ADD COLUMN IF NOT EXISTS profile_picture_cloudinary_id TEXT;

-- Add comments for students table
COMMENT ON COLUMN students.profile_picture_url IS 'Cloudinary URL for student profile picture';
COMMENT ON COLUMN students.profile_picture_cloudinary_id IS 'Cloudinary public ID for profile picture management (deletion/replacement)';

-- Add profile picture fields to teachers table
ALTER TABLE teachers 
ADD COLUMN IF NOT EXISTS profile_picture_url TEXT,
ADD COLUMN IF NOT EXISTS profile_picture_cloudinary_id TEXT;

-- Add comments for teachers table
COMMENT ON COLUMN teachers.profile_picture_url IS 'Cloudinary URL for teacher profile picture';
COMMENT ON COLUMN teachers.profile_picture_cloudinary_id IS 'Cloudinary public ID for profile picture management (deletion/replacement)';

-- Verification queries
SELECT 'Students table updated' AS status, 
       COUNT(*) FILTER (WHERE profile_picture_url IS NOT NULL) AS students_with_pictures
FROM students;

SELECT 'Teachers table updated' AS status,
       COUNT(*) FILTER (WHERE profile_picture_url IS NOT NULL) AS teachers_with_pictures
FROM teachers;

