-- =====================================================
-- Migration: ENUM to VARCHAR Conversion
-- =====================================================
-- This script converts PostgreSQL ENUM columns to VARCHAR with CHECK constraints
-- for better compatibility with SQLAlchemy ORM

-- Start transaction
BEGIN;

-- =====================================================
-- 1. Drop existing ENUM types if they exist
-- =====================================================
DROP TYPE IF EXISTS user_type_enum CASCADE;
DROP TYPE IF EXISTS gender_enum CASCADE;
DROP TYPE IF EXISTS class_enum CASCADE;
DROP TYPE IF EXISTS qualification_enum CASCADE;
DROP TYPE IF EXISTS employment_status_enum CASCADE;
DROP TYPE IF EXISTS session_year_enum CASCADE;
DROP TYPE IF EXISTS payment_type_enum CASCADE;
DROP TYPE IF EXISTS payment_status_enum CASCADE;
DROP TYPE IF EXISTS payment_method_enum CASCADE;
DROP TYPE IF EXISTS leave_type_enum CASCADE;
DROP TYPE IF EXISTS leave_status_enum CASCADE;
DROP TYPE IF EXISTS expense_category_enum CASCADE;
DROP TYPE IF EXISTS expense_status_enum CASCADE;

-- =====================================================
-- 2. Alter existing tables to use VARCHAR with CHECK constraints
-- =====================================================

-- Users table
ALTER TABLE users 
ALTER COLUMN role TYPE VARCHAR(20),
ADD CONSTRAINT chk_users_role CHECK (role IN ('admin', 'teacher', 'student', 'parent'));

-- Students table
ALTER TABLE students 
ALTER COLUMN gender TYPE VARCHAR(10),
ADD CONSTRAINT chk_students_gender CHECK (gender IN ('Male', 'Female', 'Other')),
ALTER COLUMN session_year TYPE VARCHAR(10),
ADD CONSTRAINT chk_students_session_year CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27'));

-- Teachers table
ALTER TABLE teachers 
ALTER COLUMN gender TYPE VARCHAR(10),
ADD CONSTRAINT chk_teachers_gender CHECK (gender IN ('Male', 'Female', 'Other')),
ALTER COLUMN employment_type TYPE VARCHAR(20),
ADD CONSTRAINT chk_teachers_employment_type CHECK (employment_type IN ('Full Time', 'Part Time', 'Contract', 'Substitute'));

-- Fee Structures table
ALTER TABLE fee_structures 
ALTER COLUMN session_year TYPE VARCHAR(10),
ADD CONSTRAINT chk_fee_structures_session_year CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27'));

-- Fee Records table
ALTER TABLE fee_records 
ALTER COLUMN session_year TYPE VARCHAR(10),
ADD CONSTRAINT chk_fee_records_session_year CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27')),
ALTER COLUMN payment_type TYPE VARCHAR(20),
ADD CONSTRAINT chk_fee_records_payment_type CHECK (payment_type IN ('Monthly', 'Quarterly', 'Half Yearly', 'Yearly')),
ALTER COLUMN status TYPE VARCHAR(20),
ADD CONSTRAINT chk_fee_records_status CHECK (status IN ('Pending', 'Partial', 'Paid', 'Overdue')),
ALTER COLUMN payment_method TYPE VARCHAR(20),
ADD CONSTRAINT chk_fee_records_payment_method CHECK (payment_method IN ('Cash', 'Cheque', 'Online', 'UPI', 'Card'));

-- Fee Payments table
ALTER TABLE fee_payments 
ALTER COLUMN payment_method TYPE VARCHAR(20),
ADD CONSTRAINT chk_fee_payments_payment_method CHECK (payment_method IN ('Cash', 'Cheque', 'Online', 'UPI', 'Card'));

-- Student Attendance table
ALTER TABLE student_attendance 
ALTER COLUMN status TYPE VARCHAR(10),
ADD CONSTRAINT chk_student_attendance_status CHECK (status IN ('Present', 'Absent', 'Late', 'Half Day'));

-- Teacher Attendance table
ALTER TABLE teacher_attendance 
ALTER COLUMN status TYPE VARCHAR(10),
ADD CONSTRAINT chk_teacher_attendance_status CHECK (status IN ('Present', 'Absent', 'Late', 'Half Day', 'On Leave')),
ALTER COLUMN leave_type TYPE VARCHAR(30),
ADD CONSTRAINT chk_teacher_attendance_leave_type CHECK (leave_type IN ('Sick Leave', 'Casual Leave', 'Emergency Leave', 'Medical Leave'));

-- Leave Requests table
ALTER TABLE leave_requests 
ALTER COLUMN leave_type TYPE VARCHAR(30),
ADD CONSTRAINT chk_leave_requests_leave_type CHECK (leave_type IN ('Sick Leave', 'Casual Leave', 'Emergency Leave', 'Medical Leave', 'Family Function', 'Other')),
ALTER COLUMN status TYPE VARCHAR(20),
ADD CONSTRAINT chk_leave_requests_status CHECK (status IN ('Pending', 'Approved', 'Rejected', 'Cancelled'));

-- Expenses table
ALTER TABLE expenses 
ALTER COLUMN category TYPE VARCHAR(50),
ADD CONSTRAINT chk_expenses_category CHECK (category IN (
    'Infrastructure', 'Maintenance', 'Utilities', 'Supplies', 'Equipment',
    'Transportation', 'Events', 'Marketing', 'Staff Welfare', 'Academic',
    'Sports', 'Library', 'Laboratory', 'Security', 'Cleaning', 'Other'
)),
ALTER COLUMN payment_method TYPE VARCHAR(20),
ADD CONSTRAINT chk_expenses_payment_method CHECK (payment_method IN ('Cash', 'Cheque', 'Online Transfer', 'UPI', 'Card')),
ALTER COLUMN payment_status TYPE VARCHAR(20),
ADD CONSTRAINT chk_expenses_payment_status CHECK (payment_status IN ('Pending', 'Paid', 'Partially Paid', 'Overdue')),
ALTER COLUMN status TYPE VARCHAR(20),
ADD CONSTRAINT chk_expenses_status CHECK (status IN ('Pending', 'Approved', 'Rejected', 'Paid'));

-- =====================================================
-- 3. Update any existing data to ensure consistency
-- =====================================================

-- Update any inconsistent data (if needed)
-- This section would contain specific data updates based on your current data

-- =====================================================
-- 4. Create indexes on new VARCHAR columns for performance
-- =====================================================

-- Recreate indexes that might have been dropped
CREATE INDEX IF NOT EXISTS idx_users_role_varchar ON users(role);
CREATE INDEX IF NOT EXISTS idx_students_gender_varchar ON students(gender);
CREATE INDEX IF NOT EXISTS idx_students_session_year_varchar ON students(session_year);
CREATE INDEX IF NOT EXISTS idx_teachers_employment_type_varchar ON teachers(employment_type);
CREATE INDEX IF NOT EXISTS idx_fee_records_session_year_varchar ON fee_records(session_year);
CREATE INDEX IF NOT EXISTS idx_fee_records_payment_type_varchar ON fee_records(payment_type);
CREATE INDEX IF NOT EXISTS idx_fee_records_status_varchar ON fee_records(status);
CREATE INDEX IF NOT EXISTS idx_expenses_category_varchar ON expenses(category);
CREATE INDEX IF NOT EXISTS idx_expenses_status_varchar ON expenses(status);

-- =====================================================
-- 5. Verification queries
-- =====================================================

-- Verify the migration
SELECT 
    table_name,
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND column_name IN ('role', 'gender', 'session_year', 'payment_type', 'status', 'category', 'employment_type')
ORDER BY table_name, column_name;

-- Check constraints
SELECT 
    tc.table_name,
    tc.constraint_name,
    cc.check_clause
FROM information_schema.table_constraints tc
JOIN information_schema.check_constraints cc ON tc.constraint_name = cc.constraint_name
WHERE tc.table_schema = 'public' 
AND tc.constraint_type = 'CHECK'
AND tc.constraint_name LIKE 'chk_%'
ORDER BY tc.table_name, tc.constraint_name;

-- Commit the transaction
COMMIT;

-- Success message
SELECT 'ENUM to VARCHAR migration completed successfully!' as result;
SELECT 'All ENUM types have been converted to VARCHAR with CHECK constraints' as details;
