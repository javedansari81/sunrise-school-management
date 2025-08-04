-- =====================================================
-- Add Aadhar Number Columns to Students and Teachers Tables
-- Execute Date: [TO BE FILLED WHEN EXECUTED]
-- =====================================================

-- Add aadhar_no column to students table
ALTER TABLE students ADD COLUMN IF NOT EXISTS aadhar_no VARCHAR(12);

-- Add aadhar_no column to teachers table  
ALTER TABLE teachers ADD COLUMN IF NOT EXISTS aadhar_no VARCHAR(12);

-- Add comments for documentation
COMMENT ON COLUMN students.aadhar_no IS 'Aadhar card number (12 digits) - nullable for existing records';
COMMENT ON COLUMN teachers.aadhar_no IS 'Aadhar card number (12 digits) - nullable for existing records';

-- Optional: Add indexes for performance (uncomment if needed for frequent searches)
-- CREATE INDEX IF NOT EXISTS idx_students_aadhar_no ON students(aadhar_no) WHERE aadhar_no IS NOT NULL;
-- CREATE INDEX IF NOT EXISTS idx_teachers_aadhar_no ON teachers(aadhar_no) WHERE aadhar_no IS NOT NULL;

-- Optional: Add unique constraints (uncomment if Aadhar numbers should be unique across the system)
-- ALTER TABLE students ADD CONSTRAINT unique_student_aadhar UNIQUE (aadhar_no);
-- ALTER TABLE teachers ADD CONSTRAINT unique_teacher_aadhar UNIQUE (aadhar_no);

-- Verification queries (run after executing the ALTER statements)
-- SELECT column_name, data_type, is_nullable FROM information_schema.columns 
-- WHERE table_name = 'students' AND column_name = 'aadhar_no';

-- SELECT column_name, data_type, is_nullable FROM information_schema.columns 
-- WHERE table_name = 'teachers' AND column_name = 'aadhar_no';
