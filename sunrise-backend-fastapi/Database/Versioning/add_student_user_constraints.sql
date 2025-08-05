-- Add constraints to prevent orphaned student records
-- This migration adds database-level constraints to ensure data integrity

-- 1. Add a check constraint to ensure students with email/phone have user_id
-- Note: This is a conditional constraint that only applies when email or phone is provided

DO $$
BEGIN
    -- Check if the constraint already exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'chk_student_user_link' 
        AND table_name = 'students'
    ) THEN
        -- Add constraint: if student has email or phone, they must have user_id
        ALTER TABLE students 
        ADD CONSTRAINT chk_student_user_link 
        CHECK (
            (email IS NULL AND phone IS NULL) OR 
            (user_id IS NOT NULL)
        );
        
        RAISE NOTICE 'Added constraint: chk_student_user_link';
    ELSE
        RAISE NOTICE 'Constraint chk_student_user_link already exists';
    END IF;
END $$;

-- 2. Add index on user_id for better performance
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_students_user_id'
    ) THEN
        CREATE INDEX idx_students_user_id ON students(user_id);
        RAISE NOTICE 'Added index: idx_students_user_id';
    ELSE
        RAISE NOTICE 'Index idx_students_user_id already exists';
    END IF;
END $$;

-- 3. Add index on email for faster lookups during user linking
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_students_email'
    ) THEN
        CREATE INDEX idx_students_email ON students(email) WHERE email IS NOT NULL;
        RAISE NOTICE 'Added index: idx_students_email';
    ELSE
        RAISE NOTICE 'Index idx_students_email already exists';
    END IF;
END $$;

-- 4. Add a function to validate student-user linking
CREATE OR REPLACE FUNCTION validate_student_user_link()
RETURNS TRIGGER AS $$
BEGIN
    -- If student has email or phone, ensure they have a user_id
    IF (NEW.email IS NOT NULL OR NEW.phone IS NOT NULL) AND NEW.user_id IS NULL THEN
        RAISE EXCEPTION 'Students with email or phone must have a linked user account (user_id cannot be NULL)';
    END IF;
    
    -- If user_id is provided, ensure the user exists and is a STUDENT type
    IF NEW.user_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1 FROM users u 
            JOIN user_types ut ON u.user_type_id = ut.id 
            WHERE u.id = NEW.user_id AND ut.name = 'STUDENT'
        ) THEN
            RAISE EXCEPTION 'user_id % must reference a valid STUDENT user', NEW.user_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5. Create trigger to enforce validation
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'trg_validate_student_user_link'
    ) THEN
        CREATE TRIGGER trg_validate_student_user_link
            BEFORE INSERT OR UPDATE ON students
            FOR EACH ROW
            EXECUTE FUNCTION validate_student_user_link();
        
        RAISE NOTICE 'Added trigger: trg_validate_student_user_link';
    ELSE
        RAISE NOTICE 'Trigger trg_validate_student_user_link already exists';
    END IF;
END $$;

-- 6. Create a view to easily identify orphaned students
CREATE OR REPLACE VIEW orphaned_students AS
SELECT 
    s.id,
    s.admission_number,
    s.first_name,
    s.last_name,
    s.email,
    s.phone,
    s.user_id,
    s.created_at,
    s.updated_at
FROM students s
WHERE 
    s.user_id IS NULL 
    AND (s.email IS NOT NULL OR s.phone IS NOT NULL)
    AND s.is_active = true
    AND (s.is_deleted IS NULL OR s.is_deleted = false);

COMMENT ON VIEW orphaned_students IS 'Students who should have user accounts but are missing user_id links';

-- 7. Create a function to get orphaned student count
CREATE OR REPLACE FUNCTION get_orphaned_student_count()
RETURNS INTEGER AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM orphaned_students);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_orphaned_student_count() IS 'Returns the count of students missing user account links';

-- Display summary
DO $$
DECLARE
    orphaned_count INTEGER;
BEGIN
    SELECT get_orphaned_student_count() INTO orphaned_count;
    
    RAISE NOTICE '';
    RAISE NOTICE '=== STUDENT-USER LINKING CONSTRAINTS APPLIED ===';
    RAISE NOTICE 'Constraints added to prevent orphaned student records';
    RAISE NOTICE 'Current orphaned students: %', orphaned_count;
    
    IF orphaned_count > 0 THEN
        RAISE NOTICE 'WARNING: % orphaned student(s) found!', orphaned_count;
        RAISE NOTICE 'Run the fix_orphaned_students.py script to resolve them';
        RAISE NOTICE 'Query: SELECT * FROM orphaned_students;';
    ELSE
        RAISE NOTICE 'No orphaned students found - database is clean!';
    END IF;
    
    RAISE NOTICE '================================================';
END $$;
