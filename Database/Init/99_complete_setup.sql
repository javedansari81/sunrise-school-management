-- =====================================================
-- Complete Database Setup - One-Click Installation
-- =====================================================
-- This script performs a complete database setup from scratch
-- It combines all the individual scripts for a one-click installation

-- Start transaction
BEGIN;

-- =====================================================
-- STEP 1: Clean existing database (optional - uncomment if needed)
-- =====================================================

-- WARNING: Uncomment the following line only if you want to drop all existing data
-- \i '00_drop_all.sql'

-- =====================================================
-- STEP 2: Create complete database schema
-- =====================================================

-- Create version tracking table first
CREATE TABLE IF NOT EXISTS schema_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(10) NOT NULL,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_by VARCHAR(100) DEFAULT current_user
);

-- Users and Authentication Tables
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'teacher', 'student', 'parent')),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Students table (Essential for fee management)
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    admission_number VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'India',
    class VARCHAR(20) NOT NULL,
    section VARCHAR(10),
    roll_number VARCHAR(20),
    admission_date DATE NOT NULL,
    session_year VARCHAR(10) NOT NULL CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27')),
    father_name VARCHAR(200),
    father_phone VARCHAR(20),
    father_email VARCHAR(255),
    father_occupation VARCHAR(100),
    mother_name VARCHAR(200),
    mother_phone VARCHAR(20),
    mother_email VARCHAR(255),
    mother_occupation VARCHAR(100),
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relation VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Fee Structures table
CREATE TABLE IF NOT EXISTS fee_structures (
    id SERIAL PRIMARY KEY,
    class_name VARCHAR(20) NOT NULL,
    session_year VARCHAR(10) NOT NULL CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27')),
    tuition_fee DECIMAL(10,2) DEFAULT 0.0,
    admission_fee DECIMAL(10,2) DEFAULT 0.0,
    development_fee DECIMAL(10,2) DEFAULT 0.0,
    activity_fee DECIMAL(10,2) DEFAULT 0.0,
    transport_fee DECIMAL(10,2) DEFAULT 0.0,
    library_fee DECIMAL(10,2) DEFAULT 0.0,
    lab_fee DECIMAL(10,2) DEFAULT 0.0,
    exam_fee DECIMAL(10,2) DEFAULT 0.0,
    other_fee DECIMAL(10,2) DEFAULT 0.0,
    total_annual_fee DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(class_name, session_year)
);

-- Fee Records table (Main fee tracking)
CREATE TABLE IF NOT EXISTS fee_records (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year VARCHAR(10) NOT NULL CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27')),
    payment_type VARCHAR(20) NOT NULL CHECK (payment_type IN ('Monthly', 'Quarterly', 'Half Yearly', 'Yearly')),
    total_amount DECIMAL(10,2) NOT NULL,
    paid_amount DECIMAL(10,2) DEFAULT 0.0,
    balance_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Partial', 'Paid', 'Overdue')),
    due_date DATE NOT NULL,
    payment_method VARCHAR(20) CHECK (payment_method IN ('Cash', 'Cheque', 'Online', 'UPI', 'Card')),
    transaction_id VARCHAR(100),
    payment_date DATE,
    remarks TEXT,
    late_fee DECIMAL(10,2) DEFAULT 0.0,
    discount_amount DECIMAL(10,2) DEFAULT 0.0,
    discount_reason VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- STEP 3: Create essential indexes
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_students_admission_number ON students(admission_number);
CREATE INDEX IF NOT EXISTS idx_students_class ON students(class);
CREATE INDEX IF NOT EXISTS idx_students_session_year ON students(session_year);
CREATE INDEX IF NOT EXISTS idx_fee_records_student_id ON fee_records(student_id);
CREATE INDEX IF NOT EXISTS idx_fee_records_session_year ON fee_records(session_year);
CREATE INDEX IF NOT EXISTS idx_fee_records_status ON fee_records(status);

-- =====================================================
-- STEP 4: Load initial data
-- =====================================================

-- Insert admin user
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

-- Insert sample students
INSERT INTO students (
    admission_number, first_name, last_name, date_of_birth, gender, class, section, roll_number,
    phone, email, address, city, state, postal_code, country,
    father_name, father_phone, father_email, father_occupation,
    mother_name, mother_phone, mother_email, mother_occupation,
    emergency_contact_name, emergency_contact_phone, emergency_contact_relation,
    admission_date, session_year, is_active, created_at
) VALUES 
('SNS2024001', 'Aarav', 'Sharma', '2015-03-15', 'Male', 'Class 5', 'A', '001',
 '9876543301', 'aarav.sharma@student.sunriseschool.edu', 
 '123 MG Road, Koramangala', 'Bangalore', 'Karnataka', '560034', 'India',
 'Rajesh Sharma', '9876543220', 'rajesh.sharma@gmail.com', 'Software Engineer',
 'Priya Sharma', '9876543221', 'priya.sharma@gmail.com', 'Teacher',
 'Rajesh Sharma', '9876543220', 'Father',
 '2024-04-01', '2024-25', true, NOW()),
('SNS2024002', 'Ananya', 'Patel', '2016-07-22', 'Female', 'Class 4', 'B', '002',
 '9876543302', 'ananya.patel@student.sunriseschool.edu',
 '456 Brigade Road, Richmond Town', 'Bangalore', 'Karnataka', '560025', 'India',
 'Amit Patel', '9876543222', 'amit.patel@gmail.com', 'Business Owner',
 'Kavya Patel', '9876543223', 'kavya.patel@gmail.com', 'Doctor',
 'Amit Patel', '9876543222', 'Father',
 '2024-04-01', '2024-25', true, NOW()),
('SNS2024003', 'Arjun', 'Kumar', '2014-11-08', 'Male', 'Class 6', 'A', '003',
 '9876543303', 'arjun.kumar@student.sunriseschool.edu',
 '789 Koramangala 5th Block', 'Bangalore', 'Karnataka', '560095', 'India',
 'Suresh Kumar', '9876543224', 'suresh.kumar@gmail.com', 'Manager',
 'Lakshmi Kumar', '9876543225', 'lakshmi.kumar@gmail.com', 'Homemaker',
 'Suresh Kumar', '9876543224', 'Father',
 '2024-04-01', '2024-25', true, NOW())
ON CONFLICT (admission_number) DO NOTHING;

-- Insert fee structures
INSERT INTO fee_structures (
    class_name, session_year, tuition_fee, admission_fee, development_fee, activity_fee,
    transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee, created_at
) VALUES 
('Class 5', '2024-25', 34000, 2500, 2000, 1500, 3500, 1000, 1000, 1000, 1000, 47500, NOW()),
('Class 4', '2024-25', 32000, 2500, 2000, 1500, 3500, 1000, 800, 1000, 1000, 45300, NOW()),
('Class 6', '2024-25', 36000, 3000, 2500, 2000, 4000, 1200, 1200, 1200, 1200, 52300, NOW())
ON CONFLICT (class_name, session_year) DO NOTHING;

-- Insert sample fee records
INSERT INTO fee_records (
    student_id, session_year, payment_type, total_amount, paid_amount, balance_amount,
    status, due_date, created_at
) VALUES 
(1, '2024-25', 'Quarterly', 11000.0, 0.0, 11000.0, 'Pending', '2024-07-15', NOW()),
(2, '2024-25', 'Quarterly', 10500.0, 5000.0, 5500.0, 'Pending', '2024-07-15', NOW()),
(3, '2024-25', 'Half Yearly', 23150.0, 0.0, 23150.0, 'Pending', '2024-09-15', NOW())
ON CONFLICT DO NOTHING;

-- =====================================================
-- STEP 5: Record installation
-- =====================================================

INSERT INTO schema_versions (version, description) 
VALUES ('1.0', 'Complete database setup with essential tables and initial data')
ON CONFLICT DO NOTHING;

-- =====================================================
-- STEP 6: Verification and summary
-- =====================================================

-- Verify installation
SELECT 'Installation Summary' as info;

SELECT 'Tables Created' as item, COUNT(*) as count
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'

UNION ALL

SELECT 'Users Created' as item, COUNT(*) as count FROM users

UNION ALL

SELECT 'Students Created' as item, COUNT(*) as count FROM students

UNION ALL

SELECT 'Fee Structures Created' as item, COUNT(*) as count FROM fee_structures

UNION ALL

SELECT 'Fee Records Created' as item, COUNT(*) as count FROM fee_records;

-- Display login information
SELECT 
    'Login Information' as info,
    'Email: admin@sunriseschool.edu' as email,
    'Password: admin123' as password;

-- Commit the transaction
COMMIT;

-- =====================================================
-- Success Messages
-- =====================================================

SELECT 'Complete database setup finished successfully!' AS result;
SELECT 'System is ready for use' AS status;
SELECT 'Login with: admin@sunriseschool.edu / admin123' AS login_info;
