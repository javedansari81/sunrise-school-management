-- Sunrise School Management System Database Schema
-- PostgreSQL Database Schema with all required tables

-- Drop existing tables if they exist (in correct order to handle foreign keys)
DROP TABLE IF EXISTS fee_payments CASCADE;
DROP TABLE IF EXISTS fee_records CASCADE;
DROP TABLE IF EXISTS fee_structures CASCADE;
DROP TABLE IF EXISTS leave_requests CASCADE;
DROP TABLE IF EXISTS expenses CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS teachers CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create ENUM types
CREATE TYPE user_type_enum AS ENUM ('admin', 'teacher', 'student', 'staff', 'parent');
CREATE TYPE gender_enum AS ENUM ('Male', 'Female', 'Other');
CREATE TYPE class_enum AS ENUM ('PG', 'LKG', 'UKG', 'Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5', 'Class 6', 'Class 7', 'Class 8');
CREATE TYPE qualification_enum AS ENUM ('Bachelor''s Degree', 'Master''s Degree', 'PhD', 'Diploma', 'Certificate', 'Other');
CREATE TYPE employment_status_enum AS ENUM ('Full Time', 'Part Time', 'Contract', 'Substitute');
CREATE TYPE session_year_enum AS ENUM ('2023-24', '2024-25', '2025-26', '2026-27');
CREATE TYPE payment_type_enum AS ENUM ('Monthly', 'Quarterly', 'Half Yearly', 'Yearly');
CREATE TYPE payment_status_enum AS ENUM ('Pending', 'Partial', 'Paid', 'Overdue');
CREATE TYPE payment_method_enum AS ENUM ('Cash', 'Cheque', 'Online', 'UPI', 'Card');
CREATE TYPE leave_type_enum AS ENUM ('Sick Leave', 'Casual Leave', 'Emergency Leave', 'Family Function', 'Medical Leave', 'Other');
CREATE TYPE leave_status_enum AS ENUM ('Pending', 'Approved', 'Rejected', 'Cancelled');
CREATE TYPE expense_category_enum AS ENUM ('Office Supplies', 'Maintenance', 'Utilities', 'Transport', 'Food & Catering', 'Equipment', 'Marketing', 'Staff Welfare', 'Academic Materials', 'Infrastructure', 'Other');
CREATE TYPE expense_status_enum AS ENUM ('Pending', 'Approved', 'Rejected', 'Paid');

-- Users table (for authentication and authorization)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    mobile VARCHAR(20) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_type user_type_enum NOT NULL DEFAULT 'admin',
    student_id INTEGER,
    teacher_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Students table
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    admission_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender gender_enum NOT NULL,
    current_class class_enum NOT NULL,
    section VARCHAR(10),
    roll_number VARCHAR(20),
    email VARCHAR(255),
    phone VARCHAR(15),
    address TEXT,
    father_name VARCHAR(100) NOT NULL,
    father_phone VARCHAR(15),
    father_email VARCHAR(255),
    father_occupation VARCHAR(100),
    mother_name VARCHAR(100) NOT NULL,
    mother_phone VARCHAR(15),
    mother_email VARCHAR(255),
    mother_occupation VARCHAR(100),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(15),
    emergency_contact_relation VARCHAR(50),
    admission_date DATE NOT NULL,
    previous_school VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Teachers table
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender gender_enum NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    address TEXT,
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(15),
    emergency_contact_relation VARCHAR(50),
    position VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    subjects TEXT, -- JSON array of subjects
    qualification qualification_enum NOT NULL,
    experience_years INTEGER DEFAULT 0,
    joining_date DATE NOT NULL,
    employment_status employment_status_enum DEFAULT 'Full Time',
    salary DECIMAL(10,2),
    bio TEXT,
    specializations TEXT, -- JSON array of specializations
    certifications TEXT, -- JSON array of certifications
    img TEXT, -- Base64 encoded image or URL
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Fee structures table
CREATE TABLE fee_structures (
    id SERIAL PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    session_year session_year_enum NOT NULL,
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

-- Fee records table
CREATE TABLE fee_records (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year session_year_enum NOT NULL,
    payment_type payment_type_enum NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    paid_amount DECIMAL(10,2) DEFAULT 0.0,
    balance_amount DECIMAL(10,2) NOT NULL,
    status payment_status_enum DEFAULT 'Pending',
    payment_method payment_method_enum,
    transaction_id VARCHAR(100),
    payment_date DATE,
    due_date DATE NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Fee payments table (for tracking individual payments)
CREATE TABLE fee_payments (
    id SERIAL PRIMARY KEY,
    fee_record_id INTEGER NOT NULL REFERENCES fee_records(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    payment_method payment_method_enum NOT NULL,
    transaction_id VARCHAR(100),
    payment_date DATE NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Leave requests table
CREATE TABLE leave_requests (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    leave_type leave_type_enum NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INTEGER NOT NULL,
    reason TEXT NOT NULL,
    description TEXT,
    emergency_contact VARCHAR(15),
    attachment_url TEXT,
    status leave_status_enum DEFAULT 'Pending',
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Expenses table
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category expense_category_enum NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0.0,
    total_amount DECIMAL(10,2) NOT NULL,
    vendor_name VARCHAR(200),
    vendor_contact VARCHAR(15),
    vendor_address TEXT,
    payment_mode payment_method_enum,
    payment_date DATE,
    transaction_id VARCHAR(100),
    cheque_number VARCHAR(50),
    invoice_number VARCHAR(100),
    invoice_date DATE,
    bill_attachment_url TEXT,
    status expense_status_enum DEFAULT 'Pending',
    requested_by INTEGER NOT NULL REFERENCES users(id),
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    remarks TEXT,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_frequency VARCHAR(50),
    expense_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add foreign key constraints for users table
ALTER TABLE users ADD CONSTRAINT fk_users_student FOREIGN KEY (student_id) REFERENCES students(id);
ALTER TABLE users ADD CONSTRAINT fk_users_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id);

-- Create indexes for better performance
CREATE INDEX idx_students_admission_number ON students(admission_number);
CREATE INDEX idx_students_class ON students(current_class);
CREATE INDEX idx_students_active ON students(is_active);
CREATE INDEX idx_teachers_employee_id ON teachers(employee_id);
CREATE INDEX idx_teachers_department ON teachers(department);
CREATE INDEX idx_teachers_active ON teachers(is_active);
CREATE INDEX idx_fee_records_student ON fee_records(student_id);
CREATE INDEX idx_fee_records_session ON fee_records(session_year);
CREATE INDEX idx_fee_records_status ON fee_records(status);
CREATE INDEX idx_leave_requests_student ON leave_requests(student_id);
CREATE INDEX idx_leave_requests_status ON leave_requests(status);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_status ON expenses(status);
CREATE INDEX idx_expenses_requested_by ON expenses(requested_by);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_type ON users(user_type);

-- Add triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_teachers_updated_at BEFORE UPDATE ON teachers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_fee_structures_updated_at BEFORE UPDATE ON fee_structures FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_fee_records_updated_at BEFORE UPDATE ON fee_records FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_fee_payments_updated_at BEFORE UPDATE ON fee_payments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_leave_requests_updated_at BEFORE UPDATE ON leave_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_expenses_updated_at BEFORE UPDATE ON expenses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
