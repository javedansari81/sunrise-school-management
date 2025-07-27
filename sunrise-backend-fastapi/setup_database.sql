-- =====================================================
-- Sunrise School Management System - Database Setup
-- =====================================================

-- Create database (run this first if database doesn't exist)
-- CREATE DATABASE sunrise_db;

-- Connect to sunrise_db database before running the rest

-- =====================================================
-- 1. CREATE TABLES
-- =====================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    mobile VARCHAR(20) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_type VARCHAR(50) NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    admission_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    current_class VARCHAR(20) NOT NULL CHECK (current_class IN ('PG', 'Nursery', 'LKG', 'UKG', 'Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5', 'Class 6', 'Class 7', 'Class 8')),
    section VARCHAR(10),
    roll_number VARCHAR(20),
    
    -- Contact Information
    email VARCHAR(100),
    phone VARCHAR(15),
    address TEXT,
    
    -- Parent Information
    father_name VARCHAR(100) NOT NULL,
    father_phone VARCHAR(15),
    father_email VARCHAR(100),
    father_occupation VARCHAR(100),
    
    mother_name VARCHAR(100) NOT NULL,
    mother_phone VARCHAR(15),
    mother_email VARCHAR(100),
    mother_occupation VARCHAR(100),
    
    -- Emergency Contact
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(15),
    emergency_contact_relation VARCHAR(50),
    
    -- Academic Information
    admission_date DATE NOT NULL,
    previous_school VARCHAR(200),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Leave Requests table
CREATE TABLE IF NOT EXISTS leave_requests (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) NOT NULL,
    
    -- Leave Details
    leave_type VARCHAR(50) NOT NULL CHECK (leave_type IN ('Sick Leave', 'Casual Leave', 'Emergency Leave', 'Family Function', 'Medical Leave', 'Other')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INTEGER NOT NULL,
    
    -- Reason and Description
    reason VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Status and Approval
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Rejected', 'Cancelled')),
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    
    -- Contact Information during leave
    emergency_contact VARCHAR(15),
    
    -- Attachments (if any)
    attachment_url VARCHAR(500),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    
    -- Basic Information
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL CHECK (category IN ('Infrastructure', 'Maintenance', 'Utilities', 'Supplies', 'Equipment', 'Transportation', 'Events', 'Marketing', 'Staff Welfare', 'Academic', 'Sports', 'Library', 'Laboratory', 'Security', 'Cleaning', 'Other')),
    
    -- Amount Details
    amount DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0.0,
    total_amount DECIMAL(10,2) NOT NULL,
    
    -- Vendor/Supplier Information
    vendor_name VARCHAR(200),
    vendor_contact VARCHAR(15),
    vendor_address TEXT,
    
    -- Payment Information
    payment_mode VARCHAR(20) CHECK (payment_mode IN ('Cash', 'Cheque', 'Online Transfer', 'UPI', 'Card')),
    payment_date DATE,
    transaction_id VARCHAR(100),
    cheque_number VARCHAR(50),
    
    -- Invoice/Bill Information
    invoice_number VARCHAR(100),
    invoice_date DATE,
    bill_attachment_url VARCHAR(500),
    
    -- Approval Workflow
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Paid', 'Rejected')),
    requested_by INTEGER REFERENCES users(id) NOT NULL,
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    
    -- Additional Information
    remarks TEXT,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_frequency VARCHAR(50),
    
    -- Timestamps
    expense_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Fee Structures table
CREATE TABLE IF NOT EXISTS fee_structures (
    id SERIAL PRIMARY KEY,
    class_name VARCHAR(20) NOT NULL,
    session_year VARCHAR(10) NOT NULL CHECK (session_year IN ('2023-24', '2024-25', '2025-26', '2026-27')),
    
    -- Fee Components
    tuition_fee DECIMAL(10,2) DEFAULT 0.0,
    admission_fee DECIMAL(10,2) DEFAULT 0.0,
    development_fee DECIMAL(10,2) DEFAULT 0.0,
    activity_fee DECIMAL(10,2) DEFAULT 0.0,
    transport_fee DECIMAL(10,2) DEFAULT 0.0,
    library_fee DECIMAL(10,2) DEFAULT 0.0,
    lab_fee DECIMAL(10,2) DEFAULT 0.0,
    exam_fee DECIMAL(10,2) DEFAULT 0.0,
    other_fee DECIMAL(10,2) DEFAULT 0.0,
    
    -- Total
    total_annual_fee DECIMAL(10,2) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Fee Records table
CREATE TABLE IF NOT EXISTS fee_records (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) NOT NULL,
    session_year VARCHAR(10) NOT NULL CHECK (session_year IN ('2023-24', '2024-25', '2025-26', '2026-27')),
    payment_type VARCHAR(20) NOT NULL CHECK (payment_type IN ('Monthly', 'Quarterly', 'Half Yearly', 'Yearly')),
    
    -- Fee Details
    total_amount DECIMAL(10,2) NOT NULL,
    paid_amount DECIMAL(10,2) DEFAULT 0.0,
    balance_amount DECIMAL(10,2) NOT NULL,
    
    -- Payment Status
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Partial', 'Paid', 'Overdue')),
    
    -- Due Date
    due_date DATE NOT NULL,
    
    -- Payment Details
    payment_method VARCHAR(20) CHECK (payment_method IN ('Cash', 'Cheque', 'Online', 'UPI', 'Card')),
    transaction_id VARCHAR(100),
    payment_date DATE,
    
    -- Additional Info
    remarks TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Fee Payments table
CREATE TABLE IF NOT EXISTS fee_payments (
    id SERIAL PRIMARY KEY,
    fee_record_id INTEGER REFERENCES fee_records(id) NOT NULL,
    
    -- Payment Details
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('Cash', 'Cheque', 'Online', 'UPI', 'Card')),
    payment_date DATE NOT NULL,
    transaction_id VARCHAR(100),
    
    -- Additional Info
    remarks TEXT,
    receipt_number VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_students_admission_number ON students(admission_number);
CREATE INDEX IF NOT EXISTS idx_students_class ON students(current_class);
CREATE INDEX IF NOT EXISTS idx_leave_requests_student_id ON leave_requests(student_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_status ON leave_requests(status);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);
CREATE INDEX IF NOT EXISTS idx_expenses_status ON expenses(status);
CREATE INDEX IF NOT EXISTS idx_fee_records_student_id ON fee_records(student_id);
CREATE INDEX IF NOT EXISTS idx_fee_records_status ON fee_records(status);
