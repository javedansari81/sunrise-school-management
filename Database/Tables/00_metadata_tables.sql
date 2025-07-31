-- =====================================================
-- Metadata Tables for Sunrise School Management System
-- =====================================================
-- These tables store reference data with non-auto-increment primary keys
-- Main tables will reference these instead of storing text values directly

-- =====================================================
-- User Types Metadata
-- =====================================================
CREATE TABLE IF NOT EXISTS user_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE user_types IS 'Reference table for user types (admin, teacher, student, etc.)';
COMMENT ON COLUMN user_types.id IS 'Non-auto-increment primary key for user type';

-- =====================================================
-- Session Years Metadata
-- =====================================================
CREATE TABLE IF NOT EXISTS session_years (
    id INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE session_years IS 'Reference table for academic session years';
COMMENT ON COLUMN session_years.id IS 'Non-auto-increment primary key for session year';
COMMENT ON COLUMN session_years.is_current IS 'Indicates if this is the current active session';

-- =====================================================
-- Genders Metadata
-- =====================================================
CREATE TABLE IF NOT EXISTS genders (
    id INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE genders IS 'Reference table for gender options';
COMMENT ON COLUMN genders.id IS 'Non-auto-increment primary key for gender';

-- =====================================================
-- Classes Metadata
-- =====================================================
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE,
    display_name VARCHAR(50),
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE classes IS 'Reference table for class/grade levels';
COMMENT ON COLUMN classes.id IS 'Non-auto-increment primary key for class';
COMMENT ON COLUMN classes.sort_order IS 'Order for displaying classes (PG=1, LKG=2, etc.)';

-- =====================================================
-- Payment Types Metadata
-- =====================================================
CREATE TABLE IF NOT EXISTS payment_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE payment_types IS 'Reference table for payment frequency types';
COMMENT ON COLUMN payment_types.id IS 'Non-auto-increment primary key for payment type';

-- =====================================================
-- Payment Statuses Metadata
-- =====================================================
CREATE TABLE IF NOT EXISTS payment_statuses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE,
    description TEXT,
    color_code VARCHAR(10), -- For UI display
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE payment_statuses IS 'Reference table for payment status options';
COMMENT ON COLUMN payment_statuses.id IS 'Non-auto-increment primary key for payment status';
COMMENT ON COLUMN payment_statuses.color_code IS 'Color code for UI display (e.g., #FF0000 for overdue)';

-- =====================================================
-- Payment Methods Metadata
-- =====================================================
CREATE TABLE IF NOT EXISTS payment_methods (
    id INTEGER PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE,
    description TEXT,
    requires_reference BOOLEAN DEFAULT FALSE, -- For cheque number, transaction ID, etc.
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE payment_methods IS 'Reference table for payment method options';
COMMENT ON COLUMN payment_methods.id IS 'Non-auto-increment primary key for payment method';
COMMENT ON COLUMN payment_methods.requires_reference IS 'Whether this method requires reference number';

-- =====================================================
-- Leave Types Metadata
-- =====================================================
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

COMMENT ON TABLE leave_types IS 'Reference table for leave type options';
COMMENT ON COLUMN leave_types.id IS 'Non-auto-increment primary key for leave type';
COMMENT ON COLUMN leave_types.max_days_per_year IS 'Maximum days allowed per year for this leave type';

-- =====================================================
-- Leave Statuses Metadata
-- =====================================================
CREATE TABLE IF NOT EXISTS leave_statuses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE,
    description TEXT,
    color_code VARCHAR(10), -- For UI display
    is_final BOOLEAN DEFAULT FALSE, -- Cannot be changed once set
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE leave_statuses IS 'Reference table for leave status options';
COMMENT ON COLUMN leave_statuses.id IS 'Non-auto-increment primary key for leave status';
COMMENT ON COLUMN leave_statuses.is_final IS 'Whether this status is final and cannot be changed';

-- =====================================================
-- Expense Categories Metadata
-- =====================================================
CREATE TABLE IF NOT EXISTS expense_categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    budget_limit DECIMAL(12,2),
    requires_approval BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE expense_categories IS 'Reference table for expense category options';
COMMENT ON COLUMN expense_categories.id IS 'Non-auto-increment primary key for expense category';
COMMENT ON COLUMN expense_categories.budget_limit IS 'Annual budget limit for this category';

-- =====================================================
-- Expense Statuses Metadata
-- =====================================================
CREATE TABLE IF NOT EXISTS expense_statuses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE,
    description TEXT,
    color_code VARCHAR(10), -- For UI display
    is_final BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE expense_statuses IS 'Reference table for expense status options';
COMMENT ON COLUMN expense_statuses.id IS 'Non-auto-increment primary key for expense status';

-- =====================================================
-- Employment Statuses Metadata
-- =====================================================
CREATE TABLE IF NOT EXISTS employment_statuses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE employment_statuses IS 'Reference table for employment status options';
COMMENT ON COLUMN employment_statuses.id IS 'Non-auto-increment primary key for employment status';

-- =====================================================
-- Qualifications Metadata
-- =====================================================
CREATE TABLE IF NOT EXISTS qualifications (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    level_order INTEGER, -- For sorting (1=Certificate, 2=Diploma, 3=Bachelor, etc.)
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE qualifications IS 'Reference table for qualification/education level options';
COMMENT ON COLUMN qualifications.id IS 'Non-auto-increment primary key for qualification';
COMMENT ON COLUMN qualifications.level_order IS 'Order for sorting qualifications by level';

-- =====================================================
-- Indexes for Performance
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_user_types_active ON user_types(is_active);
CREATE INDEX IF NOT EXISTS idx_session_years_current ON session_years(is_current);
CREATE INDEX IF NOT EXISTS idx_session_years_active ON session_years(is_active);
CREATE INDEX IF NOT EXISTS idx_genders_active ON genders(is_active);
CREATE INDEX IF NOT EXISTS idx_classes_active ON classes(is_active);
CREATE INDEX IF NOT EXISTS idx_classes_sort ON classes(sort_order);
CREATE INDEX IF NOT EXISTS idx_payment_types_active ON payment_types(is_active);
CREATE INDEX IF NOT EXISTS idx_payment_statuses_active ON payment_statuses(is_active);
CREATE INDEX IF NOT EXISTS idx_payment_methods_active ON payment_methods(is_active);
CREATE INDEX IF NOT EXISTS idx_leave_types_active ON leave_types(is_active);
CREATE INDEX IF NOT EXISTS idx_leave_statuses_active ON leave_statuses(is_active);
CREATE INDEX IF NOT EXISTS idx_expense_categories_active ON expense_categories(is_active);
CREATE INDEX IF NOT EXISTS idx_expense_statuses_active ON expense_statuses(is_active);
CREATE INDEX IF NOT EXISTS idx_employment_statuses_active ON employment_statuses(is_active);
CREATE INDEX IF NOT EXISTS idx_qualifications_active ON qualifications(is_active);
CREATE INDEX IF NOT EXISTS idx_qualifications_level ON qualifications(level_order);
