-- =====================================================
-- Table: students
-- Description: Stores student profile information
-- Dependencies: users, classes, session_years, genders
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS students CASCADE;

-- Create table
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE,
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
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    FOREIGN KEY (gender_id) REFERENCES genders(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_students_admission ON students(admission_number);
CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_id);
CREATE INDEX IF NOT EXISTS idx_students_session ON students(session_year_id);
CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id);
CREATE INDEX IF NOT EXISTS idx_students_not_deleted ON students(is_deleted) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_students_active_not_deleted ON students(is_active, is_deleted) WHERE is_active = TRUE AND is_deleted = FALSE;

-- Add comments
COMMENT ON TABLE students IS 'Student profile information';
COMMENT ON COLUMN students.user_id IS 'Foreign key to users table (nullable - students may not have login accounts)';
COMMENT ON COLUMN students.admission_number IS 'Unique admission number';
COMMENT ON COLUMN students.is_deleted IS 'Soft delete flag';
COMMENT ON COLUMN students.deleted_date IS 'Timestamp when record was soft deleted';

