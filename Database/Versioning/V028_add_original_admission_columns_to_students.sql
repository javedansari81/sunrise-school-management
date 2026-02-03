-- =====================================================
-- Migration: V028_add_original_admission_columns_to_students
-- Description: Add original_session_year_id and original_class_id to students table
--              to track the student's first admission session and class
-- =====================================================

-- Add original_session_year_id column
ALTER TABLE students
ADD COLUMN IF NOT EXISTS original_session_year_id INTEGER;

-- Add original_class_id column
ALTER TABLE students
ADD COLUMN IF NOT EXISTS original_class_id INTEGER;

-- Add foreign key constraints
ALTER TABLE students
ADD CONSTRAINT fk_students_original_session_year 
    FOREIGN KEY (original_session_year_id) REFERENCES session_years(id);

ALTER TABLE students
ADD CONSTRAINT fk_students_original_class 
    FOREIGN KEY (original_class_id) REFERENCES classes(id);

-- Backfill existing students with their current values
-- This assumes current session_year_id and class_id represent their original admission
-- for students who haven't been progressed yet
UPDATE students
SET original_session_year_id = session_year_id,
    original_class_id = class_id
WHERE original_session_year_id IS NULL
  AND is_deleted = FALSE;

-- Create indexes for query optimization
CREATE INDEX IF NOT EXISTS idx_students_original_session 
    ON students(original_session_year_id);
CREATE INDEX IF NOT EXISTS idx_students_original_class 
    ON students(original_class_id);

-- Add comments
COMMENT ON COLUMN students.original_session_year_id IS 'The session year when student was first admitted';
COMMENT ON COLUMN students.original_class_id IS 'The class in which student was first admitted';

