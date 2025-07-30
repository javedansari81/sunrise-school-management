-- =====================================================
-- Load Initial Data - Complete Setup
-- =====================================================
-- This script loads all initial and sample data for the database

-- Start transaction
BEGIN;

-- =====================================================
-- 1. Load initial users and admin accounts
-- =====================================================

-- Note: In PostgreSQL, \i command requires absolute paths or relative to current directory
-- For manual execution, run each data load script individually:
-- psql -d your_database -f ../DataLoads/01_initial_users.sql
-- psql -d your_database -f ../DataLoads/02_sample_students.sql
-- etc.

-- Essential admin user (inline for immediate setup)
INSERT INTO users (
    email, hashed_password, first_name, last_name, phone, role, is_active, is_verified, created_at
) VALUES (
    'admin@sunriseschool.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsHjxstm6', -- password: admin123
    'Admin',
    'User',
    '9876543210',
    'admin',
    true,
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- =====================================================
-- 2. Load sample students (essential for testing)
-- =====================================================

-- Sample students for testing
INSERT INTO students (
    admission_number, first_name, last_name, date_of_birth, gender, class, section, roll_number,
    phone, email, address, city, state, postal_code, country,
    father_name, father_phone, father_email, father_occupation,
    mother_name, mother_phone, mother_email, mother_occupation,
    emergency_contact_name, emergency_contact_phone, emergency_contact_relation,
    admission_date, session_year, is_active, created_at
) VALUES 
-- Student 1: Aarav Sharma
(
    'SNS2024001', 'Aarav', 'Sharma', '2015-03-15', 'Male', 'Class 5', 'A', '001',
    '9876543301', 'aarav.sharma@student.sunriseschool.edu', 
    '123 MG Road, Koramangala', 'Bangalore', 'Karnataka', '560034', 'India',
    'Rajesh Sharma', '9876543220', 'rajesh.sharma@gmail.com', 'Software Engineer',
    'Priya Sharma', '9876543221', 'priya.sharma@gmail.com', 'Teacher',
    'Rajesh Sharma', '9876543220', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 2: Ananya Patel
(
    'SNS2024002', 'Ananya', 'Patel', '2016-07-22', 'Female', 'Class 4', 'B', '002',
    '9876543302', 'ananya.patel@student.sunriseschool.edu',
    '456 Brigade Road, Richmond Town', 'Bangalore', 'Karnataka', '560025', 'India',
    'Amit Patel', '9876543222', 'amit.patel@gmail.com', 'Business Owner',
    'Kavya Patel', '9876543223', 'kavya.patel@gmail.com', 'Doctor',
    'Amit Patel', '9876543222', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 3: Arjun Kumar
(
    'SNS2024003', 'Arjun', 'Kumar', '2014-11-08', 'Male', 'Class 6', 'A', '003',
    '9876543303', 'arjun.kumar@student.sunriseschool.edu',
    '789 Koramangala 5th Block', 'Bangalore', 'Karnataka', '560095', 'India',
    'Suresh Kumar', '9876543224', 'suresh.kumar@gmail.com', 'Manager',
    'Lakshmi Kumar', '9876543225', 'lakshmi.kumar@gmail.com', 'Homemaker',
    'Suresh Kumar', '9876543224', 'Father',
    '2024-04-01', '2024-25', true, NOW()
) ON CONFLICT (admission_number) DO NOTHING;

-- =====================================================
-- 3. Load fee structures
-- =====================================================

-- Fee Structures for 2024-25 session
INSERT INTO fee_structures (
    class_name, session_year, tuition_fee, admission_fee, development_fee, activity_fee,
    transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee, created_at
) VALUES 
('Class 5', '2024-25', 34000, 2500, 2000, 1500, 3500, 1000, 1000, 1000, 1000, 47500, NOW()),
('Class 4', '2024-25', 32000, 2500, 2000, 1500, 3500, 1000, 800, 1000, 1000, 45300, NOW()),
('Class 6', '2024-25', 36000, 3000, 2500, 2000, 4000, 1200, 1200, 1200, 1200, 52300, NOW())
ON CONFLICT (class_name, session_year) DO NOTHING;

-- =====================================================
-- 4. Load sample fee records
-- =====================================================

-- Fee Records for students
INSERT INTO fee_records (
    student_id, session_year, payment_type, total_amount, paid_amount, balance_amount,
    status, due_date, created_at
) VALUES 
-- Student 1: Aarav Sharma (Class 5) - Quarterly payments
(1, '2024-25', 'Quarterly', 11000.0, 0.0, 11000.0, 'Pending', '2024-07-15', NOW()),
-- Student 2: Ananya Patel (Class 4) - Quarterly payments  
(2, '2024-25', 'Quarterly', 10500.0, 5000.0, 5500.0, 'Pending', '2024-07-15', NOW()),
-- Student 3: Arjun Kumar (Class 6) - Half Yearly payments
(3, '2024-25', 'Half Yearly', 23150.0, 0.0, 23150.0, 'Pending', '2024-09-15', NOW())
ON CONFLICT DO NOTHING;

-- =====================================================
-- 5. Load essential configuration data
-- =====================================================

-- Attendance settings
INSERT INTO attendance_settings (setting_name, setting_value, setting_type, description) VALUES
('school_start_time', '08:00', 'time', 'School start time'),
('school_end_time', '15:30', 'time', 'School end time'),
('late_threshold_minutes', '15', 'integer', 'Minutes after which student is marked late'),
('attendance_required', 'true', 'boolean', 'Whether attendance is mandatory'),
('weekend_days', 'Saturday,Sunday', 'string', 'Weekend days when school is closed')
ON CONFLICT (setting_name) DO NOTHING;

-- Holiday calendar for current academic year
INSERT INTO holiday_calendar (holiday_date, holiday_name, holiday_type, academic_year, created_at) VALUES
('2024-08-15', 'Independence Day', 'National Holiday', '2024-25', NOW()),
('2024-10-02', 'Gandhi Jayanti', 'National Holiday', '2024-25', NOW()),
('2024-10-24', 'Dussehra', 'Festival', '2024-25', NOW()),
('2024-11-12', 'Diwali', 'Festival', '2024-25', NOW()),
('2024-12-25', 'Christmas', 'Festival', '2024-25', NOW()),
('2025-01-26', 'Republic Day', 'National Holiday', '2024-25', NOW())
ON CONFLICT (holiday_date) DO NOTHING;

-- =====================================================
-- 6. Update version tracking
-- =====================================================

INSERT INTO schema_versions (version, description) 
VALUES ('1.1', 'Initial data load completed with admin user, sample students, and configuration')
ON CONFLICT DO NOTHING;

-- =====================================================
-- 7. Verification queries
-- =====================================================

-- Verify data load
SELECT 'Users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'Students' as table_name, COUNT(*) as record_count FROM students
UNION ALL
SELECT 'Fee Structures' as table_name, COUNT(*) as record_count FROM fee_structures
UNION ALL
SELECT 'Fee Records' as table_name, COUNT(*) as record_count FROM fee_records
UNION ALL
SELECT 'Attendance Settings' as table_name, COUNT(*) as record_count FROM attendance_settings
UNION ALL
SELECT 'Holiday Calendar' as table_name, COUNT(*) as record_count FROM holiday_calendar;

-- Display admin user
SELECT 
    email,
    first_name,
    last_name,
    role,
    is_active
FROM users 
WHERE role = 'admin';

-- Display sample students
SELECT 
    admission_number,
    first_name || ' ' || last_name as student_name,
    class,
    session_year
FROM students 
ORDER BY admission_number;

-- Commit the transaction
COMMIT;

-- =====================================================
-- Success Messages
-- =====================================================

SELECT 'Initial data load completed successfully!' AS result;
SELECT 'Admin user, sample students, fee structures, and configuration data loaded' AS details;
SELECT 'System is ready for use. Login with admin@sunriseschool.edu / admin123' AS login_info;
