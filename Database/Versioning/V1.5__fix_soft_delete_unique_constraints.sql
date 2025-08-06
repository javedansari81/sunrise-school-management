-- =====================================================
-- Fix Soft Delete Unique Constraints Migration
-- Version: 1.5
-- Description: Replace simple unique constraints with partial unique constraints
--              that only apply to non-deleted records for teachers and students
-- =====================================================

-- =====================================================
-- TEACHERS TABLE CONSTRAINTS
-- =====================================================

-- Drop existing unique constraints on teachers table
ALTER TABLE teachers DROP CONSTRAINT IF EXISTS uk_teachers_employee_id;
ALTER TABLE teachers DROP CONSTRAINT IF EXISTS teachers_employee_id_key;
ALTER TABLE teachers DROP CONSTRAINT IF EXISTS teachers_email_key;

-- Create partial unique constraints for teachers (only for non-deleted records)
-- These constraints only apply when is_deleted is FALSE or NULL
CREATE UNIQUE INDEX IF NOT EXISTS uk_teachers_employee_id_active 
ON teachers (employee_id) 
WHERE (is_deleted IS FALSE OR is_deleted IS NULL);

CREATE UNIQUE INDEX IF NOT EXISTS uk_teachers_email_active 
ON teachers (email) 
WHERE (is_deleted IS FALSE OR is_deleted IS NULL) AND email IS NOT NULL;

-- =====================================================
-- STUDENTS TABLE CONSTRAINTS
-- =====================================================

-- Drop existing unique constraints on students table
ALTER TABLE students DROP CONSTRAINT IF EXISTS uk_students_admission_number;
ALTER TABLE students DROP CONSTRAINT IF EXISTS students_admission_number_key;
ALTER TABLE students DROP CONSTRAINT IF EXISTS students_email_key;

-- Create partial unique constraints for students (only for non-deleted records)
CREATE UNIQUE INDEX IF NOT EXISTS uk_students_admission_number_active 
ON students (admission_number) 
WHERE (is_deleted IS FALSE OR is_deleted IS NULL);

CREATE UNIQUE INDEX IF NOT EXISTS uk_students_email_active 
ON students (email) 
WHERE (is_deleted IS FALSE OR is_deleted IS NULL) AND email IS NOT NULL;

-- =====================================================
-- USERS TABLE CONSTRAINTS (if needed)
-- =====================================================

-- Note: Users table doesn't have soft delete, so we keep the original unique constraint
-- But we should ensure it doesn't conflict with teacher/student email generation

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Verify the new constraints are in place (PostgreSQL)
-- Uncomment these to verify after running the migration:

-- SELECT 
--     schemaname,
--     tablename,
--     indexname,
--     indexdef
-- FROM pg_indexes 
-- WHERE tablename IN ('teachers', 'students') 
--   AND indexname LIKE '%_active'
-- ORDER BY tablename, indexname;

-- =====================================================
-- COMMENTS AND DOCUMENTATION
-- =====================================================

COMMENT ON INDEX uk_teachers_employee_id_active IS 'Partial unique constraint on employee_id for active (non-deleted) teachers only';
COMMENT ON INDEX uk_teachers_email_active IS 'Partial unique constraint on email for active (non-deleted) teachers only';
COMMENT ON INDEX uk_students_admission_number_active IS 'Partial unique constraint on admission_number for active (non-deleted) students only';
COMMENT ON INDEX uk_students_email_active IS 'Partial unique constraint on email for active (non-deleted) students only';

-- =====================================================
-- ROLLBACK INSTRUCTIONS (if needed)
-- =====================================================

-- To rollback this migration, run:
-- DROP INDEX IF EXISTS uk_teachers_employee_id_active;
-- DROP INDEX IF EXISTS uk_teachers_email_active;
-- DROP INDEX IF EXISTS uk_students_admission_number_active;
-- DROP INDEX IF EXISTS uk_students_email_active;
-- 
-- Then recreate the original constraints:
-- ALTER TABLE teachers ADD CONSTRAINT uk_teachers_employee_id UNIQUE (employee_id);
-- ALTER TABLE teachers ADD CONSTRAINT uk_teachers_email UNIQUE (email);
-- ALTER TABLE students ADD CONSTRAINT uk_students_admission_number UNIQUE (admission_number);

-- =====================================================
-- TESTING SCENARIOS
-- =====================================================

-- After running this migration, you should be able to:
-- 1. Create a teacher with employee_id 'EMP001'
-- 2. Soft delete that teacher (set is_deleted = TRUE)
-- 3. Create a new teacher with the same employee_id 'EMP001'
-- 4. The same applies to student admission numbers and emails

-- Test query example:
-- INSERT INTO teachers (employee_id, first_name, last_name, email, phone, position, joining_date, is_deleted) 
-- VALUES ('TEST001', 'John', 'Doe', 'john@test.com', '1234567890', 'Teacher', CURRENT_DATE, TRUE);
-- 
-- INSERT INTO teachers (employee_id, first_name, last_name, email, phone, position, joining_date) 
-- VALUES ('TEST001', 'Jane', 'Smith', 'jane@test.com', '0987654321', 'Teacher', CURRENT_DATE);
-- 
-- This should work without constraint violations after the migration.
