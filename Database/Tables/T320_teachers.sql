-- =====================================================
-- Table: teachers
-- Description: Stores teacher profile information
-- Dependencies: users, genders, qualifications, employment_statuses, classes, departments, positions
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS teachers CASCADE;

-- Create table
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE,
    employee_id VARCHAR(50) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    father_name VARCHAR(200),
    date_of_birth DATE,
    gender_id INTEGER,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    aadhar_no VARCHAR(12),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'India',
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relation VARCHAR(50),
    position_id INTEGER NOT NULL,
    department_id INTEGER,
    subjects TEXT,
    qualification_id INTEGER,
    employment_status_id INTEGER DEFAULT 1,
    experience_years INTEGER DEFAULT 0,
    joining_date DATE NOT NULL,
    class_teacher_of_id INTEGER,
    classes_assigned TEXT,
    salary DECIMAL(10,2),
    profile_picture_url TEXT,
    profile_picture_cloudinary_id TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (gender_id) REFERENCES genders(id),
    FOREIGN KEY (qualification_id) REFERENCES qualifications(id),
    FOREIGN KEY (employment_status_id) REFERENCES employment_statuses(id),
    FOREIGN KEY (class_teacher_of_id) REFERENCES classes(id),
    FOREIGN KEY (position_id) REFERENCES positions(id),
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Create indexes
-- Note: Using partial unique indexes instead of UNIQUE constraints to support soft delete
CREATE UNIQUE INDEX IF NOT EXISTS teachers_employee_id_active_unique
ON teachers (employee_id)
WHERE (is_deleted = FALSE OR is_deleted IS NULL);

CREATE UNIQUE INDEX IF NOT EXISTS teachers_email_active_unique
ON teachers (email)
WHERE (is_deleted = FALSE OR is_deleted IS NULL);

CREATE INDEX IF NOT EXISTS idx_teachers_employee ON teachers(employee_id);
CREATE INDEX IF NOT EXISTS idx_teachers_user_id ON teachers(user_id);
CREATE INDEX IF NOT EXISTS idx_teachers_qualification ON teachers(qualification_id);
CREATE INDEX IF NOT EXISTS idx_teachers_employment_status ON teachers(employment_status_id);
CREATE INDEX IF NOT EXISTS idx_teachers_class_teacher_of ON teachers(class_teacher_of_id);
CREATE INDEX IF NOT EXISTS idx_teachers_department ON teachers(department_id);
CREATE INDEX IF NOT EXISTS idx_teachers_position ON teachers(position_id);
CREATE INDEX IF NOT EXISTS idx_teachers_not_deleted ON teachers(is_deleted) WHERE is_deleted = FALSE;

-- Add comments
COMMENT ON TABLE teachers IS 'Teacher profile information';
COMMENT ON COLUMN teachers.user_id IS 'Foreign key to users table';
COMMENT ON COLUMN teachers.employee_id IS 'Unique employee ID (unique only for non-deleted teachers)';
COMMENT ON COLUMN teachers.father_name IS 'Father name of the teacher';
COMMENT ON COLUMN teachers.email IS 'Teacher email address (unique only for non-deleted teachers)';
COMMENT ON COLUMN teachers.profile_picture_url IS 'Cloudinary URL for teacher profile picture';
COMMENT ON COLUMN teachers.profile_picture_cloudinary_id IS 'Cloudinary public ID for profile picture management (deletion/replacement)';
COMMENT ON COLUMN teachers.is_deleted IS 'Soft delete flag';
COMMENT ON COLUMN teachers.deleted_date IS 'Timestamp when record was soft deleted';

