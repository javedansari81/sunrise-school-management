-- =====================================================
-- Load Initial Data - Clean SQL Version (Metadata-Driven)
-- =====================================================
-- This script loads essential initial data using pure SQL
-- Run this AFTER metadata tables are created and populated

-- Start transaction
BEGIN;

-- =====================================================
-- 1. Verify tables exist
-- =====================================================

-- Check if required tables exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        RAISE EXCEPTION 'Users table does not exist. Create tables first!';
    END IF;
    RAISE NOTICE 'Table verification passed - proceeding with data load';
END $$;

-- =====================================================
-- 2. Create admin user (aligned with current API structure)
-- =====================================================

INSERT INTO users (
    first_name, last_name, mobile, email, password, user_type, is_active, created_at
) VALUES (
    'Admin',
    'User',
    '9876543210',
    'admin@sunriseschool.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsHjxstm6', -- password: admin123
    'ADMIN',
    true,
    NOW()
) ON CONFLICT (email) DO UPDATE SET
    user_type = EXCLUDED.user_type,
    updated_at = NOW();

-- =====================================================
-- 3. Create sample teacher user (aligned with current API structure)
-- =====================================================

INSERT INTO users (
    first_name, last_name, mobile, email, password, user_type, is_active, created_at
) VALUES (
    'Sample',
    'Teacher',
    '9876543211',
    'teacher@sunriseschool.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsHjxstm6', -- password: admin123
    'TEACHER',
    true,
    NOW()
) ON CONFLICT (email) DO UPDATE SET
    user_type = EXCLUDED.user_type,
    updated_at = NOW();

-- =====================================================
-- 4. Create sample student user (aligned with current API structure)
-- =====================================================

INSERT INTO users (
    first_name, last_name, mobile, email, password, user_type, is_active, created_at
) VALUES (
    'Sample',
    'Student',
    '9876543212',
    'student@sunriseschool.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsHjxstm6', -- password: admin123
    'STUDENT',
    true,
    NOW()
) ON CONFLICT (email) DO UPDATE SET
    user_type = EXCLUDED.user_type,
    updated_at = NOW();

-- =====================================================
-- 5. Create sample teacher record (aligned with current API structure)
-- =====================================================

INSERT INTO teachers (
    employee_id, first_name, last_name, date_of_birth, gender,
    email, phone, address, emergency_contact_name, emergency_contact_phone, emergency_contact_relation,
    position, department, subjects, qualification, experience_years,
    joining_date, employment_status, salary, bio, is_active, created_at
) VALUES (
    'EMP001',
    'Sample',
    'Teacher',
    '1985-05-15',
    'Female',
    'teacher@sunriseschool.edu',
    '9876543211',
    '123 Teacher Street, Bangalore, Karnataka, 560001',
    'Emergency Contact',
    '9876543299',
    'Spouse',
    'Senior Teacher',
    'Mathematics',
    '["Mathematics", "Physics"]',
    'MASTER',
    5,
    '2020-06-01',
    'FULL_TIME',
    45000.00,
    'Experienced mathematics teacher',
    true,
    NOW()
) ON CONFLICT (employee_id) DO NOTHING;

-- =====================================================
-- 6. Create sample student record (aligned with current API structure)
-- =====================================================

INSERT INTO students (
    admission_number, first_name, last_name, date_of_birth, gender,
    current_class, section, roll_number, email, phone, address,
    father_name, father_phone, father_email, father_occupation,
    mother_name, mother_phone, mother_email, mother_occupation,
    emergency_contact_name, emergency_contact_phone, emergency_contact_relation,
    admission_date, is_active, created_at
) VALUES (
    'SNS2024001',
    'Sample',
    'Student',
    '2015-03-15',
    'Male',
    'Class 5',
    'A',
    '001',
    'student@sunriseschool.edu',
    '9876543212',
    '123 Student Street, Bangalore, Karnataka, 560001',
    'Father Name',
    '9876543220',
    'father@example.com',
    'Software Engineer',
    'Mother Name',
    '9876543221',
    'mother@example.com',
    'Teacher',
    'Father Name',
    '9876543220',
    'Father',
    '2024-04-01',
    true,
    NOW()
) ON CONFLICT (admission_number) DO NOTHING;

-- =====================================================
-- 7. Create sample fee structure (if fee tables exist)
-- =====================================================

-- Note: Fee tables may not exist yet, so we'll skip them for now
-- You can create fee records later when fee management is implemented

-- Example fee structure (commented out until tables are created)
-- INSERT INTO fee_structures (
--     class_name, session_year, tuition_fee, admission_fee, development_fee, activity_fee,
--     transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee, created_at
-- ) VALUES (
--     'Class 5', '2024-25', 34000, 2500, 2000, 1500, 3500, 1000, 1000, 1000, 1000, 47500, NOW()
-- ) ON CONFLICT (class_name, session_year) DO NOTHING;

-- =====================================================
-- 9. Create schema_versions table and update version
-- =====================================================

CREATE TABLE IF NOT EXISTS schema_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(10) NOT NULL,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_by VARCHAR(100) DEFAULT current_user
);

INSERT INTO schema_versions (version, description)
VALUES ('1.1', 'Initial data load completed with current API structure')
ON CONFLICT DO NOTHING;

-- =====================================================
-- 10. Verification queries
-- =====================================================

-- Show what was created
SELECT 'VERIFICATION RESULTS:' as status;

SELECT 'Users created' as table_name, COUNT(*) as count FROM users;
SELECT 'Teachers created' as table_name, COUNT(*) as count FROM teachers;
SELECT 'Students created' as table_name, COUNT(*) as count FROM students;

-- Show sample data (current API structure)
SELECT
    'SAMPLE STUDENT DATA:' as info,
    s.admission_number,
    s.first_name || ' ' || s.last_name as name,
    s.current_class as class,
    s.gender,
    s.father_name,
    s.mother_name
FROM students s
WHERE s.admission_number = 'SNS2024001';

-- Show sample teacher
SELECT
    'SAMPLE TEACHER DATA:' as info,
    t.employee_id,
    t.first_name || ' ' || t.last_name as name,
    t.position,
    t.department,
    t.qualification,
    t.employment_status
FROM teachers t
WHERE t.employee_id = 'EMP001';

-- Show admin user
SELECT
    'ADMIN USER:' as info,
    u.email,
    u.first_name || ' ' || u.last_name as name,
    u.user_type
FROM users u
WHERE u.email = 'admin@sunriseschool.edu';

-- Commit the transaction
COMMIT;

-- Final success message
SELECT 'SUCCESS: Initial data load completed!' as result;
SELECT 'You can now test the API endpoints with the sample data' as next_step;
