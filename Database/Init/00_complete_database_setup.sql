-- =====================================================
-- Complete Database Setup for Sunrise School Management System
-- =====================================================
-- This script creates the complete database structure with all essential tables
-- Run this script after creating the database and user
--
-- PREREQUISITES:
-- 1. PostgreSQL database 'sunrise_school_db' must exist
-- 2. User 'sunrise_user' must exist with proper permissions
-- 3. Schema 'sunrise' must be set as default search path
--
-- USAGE:
-- psql -U sunrise_user -d sunrise_school_db -f Database/Init/00_complete_database_setup.sql

-- Start transaction
BEGIN;

-- =====================================================
-- 1. Create Metadata Tables
-- =====================================================

-- User Types Metadata
CREATE TABLE IF NOT EXISTS user_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Session Years Metadata
CREATE TABLE IF NOT EXISTS session_years (
    id INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Genders Metadata
CREATE TABLE IF NOT EXISTS genders (
    id INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Classes Metadata
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Payment Types Metadata
CREATE TABLE IF NOT EXISTS payment_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Payment Statuses Metadata
CREATE TABLE IF NOT EXISTS payment_statuses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Payment Methods Metadata
CREATE TABLE IF NOT EXISTS payment_methods (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Leave Types Metadata
CREATE TABLE IF NOT EXISTS leave_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    max_days_per_year INTEGER,
    requires_medical_certificate BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Leave Statuses Metadata
CREATE TABLE IF NOT EXISTS leave_statuses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Expense Categories Metadata
CREATE TABLE IF NOT EXISTS expense_categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    budget_limit DECIMAL(15,2),
    requires_approval BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Expense Statuses Metadata
CREATE TABLE IF NOT EXISTS expense_statuses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- 2. Create Core Application Tables
-- =====================================================

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    user_type_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_type_id) REFERENCES user_types(id)
);

-- Students Table
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    admission_number VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    date_of_birth DATE,
    admission_date DATE NOT NULL,
    class_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    gender_id INTEGER,
    roll_number VARCHAR(20),
    section VARCHAR(10),
    blood_group VARCHAR(10),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    father_name VARCHAR(200),
    father_phone VARCHAR(20),
    father_email VARCHAR(255),
    father_occupation VARCHAR(100),
    mother_name VARCHAR(200),
    mother_phone VARCHAR(20),
    mother_email VARCHAR(255),
    mother_occupation VARCHAR(100),
    guardian_name VARCHAR(200),
    guardian_phone VARCHAR(20),
    guardian_email VARCHAR(255),
    guardian_relation VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    FOREIGN KEY (gender_id) REFERENCES genders(id)
);

-- Teachers Table
CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    date_of_birth DATE,
    hire_date DATE NOT NULL,
    gender_id INTEGER,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relation VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (gender_id) REFERENCES genders(id)
);

-- Fee Structures Table
CREATE TABLE IF NOT EXISTS fee_structures (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    fee_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    due_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id)
);

-- Fee Records Table
CREATE TABLE IF NOT EXISTS fee_records (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    paid_amount DECIMAL(10,2) DEFAULT 0.00,
    balance_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    payment_type_id INTEGER NOT NULL DEFAULT 1,
    payment_status_id INTEGER NOT NULL DEFAULT 1,
    due_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (payment_type_id) REFERENCES payment_types(id),
    FOREIGN KEY (payment_status_id) REFERENCES payment_statuses(id)
);

-- =====================================================
-- EXPENSES MANAGEMENT TABLES
-- =====================================================

-- Expenses Table
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,

    -- Basic Information
    expense_date DATE NOT NULL,
    expense_category_id INTEGER NOT NULL,
    subcategory VARCHAR(100),
    description TEXT NOT NULL,

    -- Financial Details
    amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
    tax_amount DECIMAL(10,2) DEFAULT 0.0 CHECK (tax_amount >= 0),
    total_amount DECIMAL(12,2) NOT NULL CHECK (total_amount > 0),
    currency VARCHAR(3) DEFAULT 'INR',

    -- Vendor Information
    vendor_name VARCHAR(200),
    vendor_contact VARCHAR(20),
    vendor_email VARCHAR(255),
    vendor_address TEXT,
    vendor_gst_number VARCHAR(20),

    -- Payment Details
    payment_method_id INTEGER NOT NULL,
    payment_status_id INTEGER DEFAULT 1,
    payment_date DATE,
    payment_reference VARCHAR(100),

    -- Bank/Cheque Details
    bank_name VARCHAR(100),
    cheque_number VARCHAR(50),
    cheque_date DATE,

    -- Approval Workflow
    expense_status_id INTEGER DEFAULT 1,
    requested_by INTEGER NOT NULL,
    approved_by INTEGER,
    approved_at TIMESTAMP WITH TIME ZONE,
    approval_comments TEXT,

    -- Budget Information
    budget_category VARCHAR(100),
    session_year_id INTEGER,
    is_budgeted BOOLEAN DEFAULT FALSE,

    -- Documents
    invoice_url VARCHAR(500),
    receipt_url VARCHAR(500),
    supporting_documents JSONB,

    -- Additional Information
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_frequency VARCHAR(20) CHECK (recurring_frequency IN ('Monthly', 'Quarterly', 'Half Yearly', 'Yearly')),
    next_due_date DATE,

    -- Priority and Urgency
    priority VARCHAR(10) DEFAULT 'Medium' CHECK (priority IN ('Low', 'Medium', 'High', 'Urgent')),
    is_emergency BOOLEAN DEFAULT FALSE,

    -- Soft Delete Support
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_date TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    FOREIGN KEY (expense_category_id) REFERENCES expense_categories(id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id),
    FOREIGN KEY (payment_status_id) REFERENCES payment_statuses(id),
    FOREIGN KEY (expense_status_id) REFERENCES expense_statuses(id),
    FOREIGN KEY (requested_by) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id)
);

-- Vendors Table
CREATE TABLE IF NOT EXISTS vendors (
    id SERIAL PRIMARY KEY,
    vendor_name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    country VARCHAR(100) DEFAULT 'India',

    -- Business Information
    gst_number VARCHAR(20),
    pan_number VARCHAR(15),
    vendor_categories JSONB,

    -- Banking Information
    bank_name VARCHAR(100),
    account_number VARCHAR(50),
    ifsc_code VARCHAR(15),
    account_holder_name VARCHAR(200),

    -- Contract Information
    contract_start_date DATE,
    contract_end_date DATE,
    payment_terms VARCHAR(100),
    credit_limit DECIMAL(12,2) DEFAULT 0.0,

    -- Performance Metrics
    rating DECIMAL(3,2) CHECK (rating BETWEEN 0 AND 5),
    total_orders INTEGER DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0.0,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER,

    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- =====================================================
-- LEAVE MANAGEMENT TABLES
-- =====================================================

-- Leave Requests Table
CREATE TABLE IF NOT EXISTS leave_requests (
    id SERIAL PRIMARY KEY,

    -- Basic Information
    user_id INTEGER NOT NULL,
    leave_type_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INTEGER NOT NULL,
    reason TEXT NOT NULL,

    -- Status and Approval
    leave_status_id INTEGER DEFAULT 1,
    applied_by INTEGER NOT NULL,
    approved_by INTEGER,
    approved_at TIMESTAMP WITH TIME ZONE,
    approval_comments TEXT,

    -- Additional Information
    is_half_day BOOLEAN DEFAULT FALSE,
    half_day_period VARCHAR(10) CHECK (half_day_period IN ('Morning', 'Afternoon')),
    emergency_contact VARCHAR(20),
    medical_certificate_url VARCHAR(500),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (leave_type_id) REFERENCES leave_types(id),
    FOREIGN KEY (leave_status_id) REFERENCES leave_statuses(id),
    FOREIGN KEY (applied_by) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- =====================================================
-- MONTHLY FEE TRACKING TABLES
-- =====================================================

-- Monthly Fee Tracking Table
CREATE TABLE IF NOT EXISTS monthly_fee_tracking (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    year INTEGER NOT NULL,
    monthly_fee_amount DECIMAL(10,2) NOT NULL,
    paid_amount DECIMAL(10,2) DEFAULT 0.00,
    balance_amount DECIMAL(10,2) NOT NULL,
    payment_status_id INTEGER DEFAULT 1,
    due_date DATE,
    paid_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    FOREIGN KEY (payment_status_id) REFERENCES payment_statuses(id),
    UNIQUE(student_id, session_year_id, month, year)
);

-- Monthly Payment Allocations Table
CREATE TABLE IF NOT EXISTS monthly_payment_allocations (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER NOT NULL,
    monthly_tracking_id INTEGER NOT NULL,
    allocated_amount DECIMAL(10,2) NOT NULL,
    allocation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    FOREIGN KEY (monthly_tracking_id) REFERENCES monthly_fee_tracking(id)
);

-- =====================================================
-- PERFORMANCE INDEXES
-- =====================================================

-- User indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type_id);

-- Student indexes
CREATE INDEX IF NOT EXISTS idx_students_admission ON students(admission_number);
CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_id);
CREATE INDEX IF NOT EXISTS idx_students_session ON students(session_year_id);

-- Teacher indexes
CREATE INDEX IF NOT EXISTS idx_teachers_employee ON teachers(employee_id);

-- Fee indexes
CREATE INDEX IF NOT EXISTS idx_fee_records_student ON fee_records(student_id);
CREATE INDEX IF NOT EXISTS idx_fee_records_session ON fee_records(session_year_id);
CREATE INDEX IF NOT EXISTS idx_monthly_fee_student ON monthly_fee_tracking(student_id);
CREATE INDEX IF NOT EXISTS idx_monthly_fee_session ON monthly_fee_tracking(session_year_id);

-- Expense indexes
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(expense_category_id);
CREATE INDEX IF NOT EXISTS idx_expenses_status ON expenses(expense_status_id);
CREATE INDEX IF NOT EXISTS idx_expenses_requested_by ON expenses(requested_by);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date);
CREATE INDEX IF NOT EXISTS idx_expenses_not_deleted ON expenses(is_deleted) WHERE is_deleted = FALSE;

-- Leave indexes
CREATE INDEX IF NOT EXISTS idx_leave_requests_user ON leave_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_status ON leave_requests(leave_status_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_dates ON leave_requests(start_date, end_date);

-- Vendor indexes
CREATE INDEX IF NOT EXISTS idx_vendors_name ON vendors(vendor_name);
CREATE INDEX IF NOT EXISTS idx_vendors_active ON vendors(is_active) WHERE is_active = TRUE;

-- Commit transaction
COMMIT;

-- =====================================================
-- Success Message
-- =====================================================
\echo '=========================================='
\echo 'DATABASE STRUCTURE CREATED SUCCESSFULLY!'
\echo '=========================================='
\echo 'Tables created:'
\echo '- 11 Metadata tables (user_types, session_years, genders, classes, etc.)'
\echo '- 3 Core user tables (users, students, teachers)'
\echo '- 2 Fee management tables (fee_structures, fee_records)'
\echo '- 2 Expense management tables (expenses, vendors)'
\echo '- 1 Leave management table (leave_requests)'
\echo '- 2 Monthly fee tracking tables (monthly_fee_tracking, monthly_payment_allocations)'
\echo 'Total: 21 tables'
\echo ''
\echo 'Performance indexes: 15 indexes created for optimal query performance'
\echo ''
\echo 'Next steps:'
\echo '1. Run Database/Init/01_load_metadata.sql to load reference data'
\echo '2. Run Database/Init/02_create_admin_user.sql to create admin user'
\echo '=========================================='
