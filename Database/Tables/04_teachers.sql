-- =====================================================
-- Teacher Management Tables
-- =====================================================

-- Teachers table (Main teacher information) - Updated for metadata-driven architecture
CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender_id INTEGER REFERENCES genders(id),

    -- Contact Information
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'India',

    -- Emergency Contact
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relation VARCHAR(50),

    -- Professional Information
    position VARCHAR(100) NOT NULL, -- 'Principal', 'Vice Principal', 'Head Teacher', 'Teacher', 'Assistant Teacher'
    department VARCHAR(100), -- 'Mathematics', 'Science', 'English', 'Social Studies', etc.
    subjects TEXT, -- JSON array or comma-separated subjects they teach
    qualification_id INTEGER REFERENCES qualifications(id), -- Primary qualification
    experience_years INTEGER DEFAULT 0,

    -- Employment Details
    joining_date DATE NOT NULL,
    employment_status_id INTEGER DEFAULT 1 REFERENCES employment_statuses(id),
    salary DECIMAL(10,2),

    -- Class Assignments
    class_teacher_of_id INTEGER REFERENCES classes(id), -- Which class they are class teacher of
    classes_assigned TEXT, -- JSON array or comma-separated classes they teach
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    resignation_date DATE,
    
    -- Documents and Photos
    photo_url VARCHAR(500),
    resume_url VARCHAR(500),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Teacher Qualifications table (Detailed qualifications) - Updated for metadata-driven architecture
CREATE TABLE IF NOT EXISTS teacher_qualifications (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    qualification_id INTEGER NOT NULL REFERENCES qualifications(id),
    degree_name VARCHAR(200) NOT NULL,
    institution VARCHAR(200) NOT NULL,
    year_of_completion INTEGER,
    grade_percentage DECIMAL(5,2),
    specialization VARCHAR(200),
    document_url VARCHAR(500),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Teacher Experience table (Previous work experience)
CREATE TABLE IF NOT EXISTS teacher_experience (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    organization VARCHAR(200) NOT NULL,
    position VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    responsibilities TEXT,
    achievements TEXT,
    reason_for_leaving VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Teacher Subject Assignments table - Updated for metadata-driven architecture
CREATE TABLE IF NOT EXISTS teacher_subject_assignments (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    subject_name VARCHAR(100) NOT NULL,
    class_id INTEGER NOT NULL REFERENCES classes(id),
    section VARCHAR(10),
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    is_active BOOLEAN DEFAULT TRUE,
    assigned_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Teacher Documents table
CREATE TABLE IF NOT EXISTS teacher_documents (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL, -- 'Resume', 'Degree Certificate', 'Experience Letter', 'ID Proof', etc.
    document_name VARCHAR(200) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by INTEGER REFERENCES users(id),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by INTEGER REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE
);

-- Teacher Performance Reviews table (Optional)
CREATE TABLE IF NOT EXISTS teacher_performance_reviews (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    review_period_start DATE NOT NULL,
    review_period_end DATE NOT NULL,
    reviewer_id INTEGER NOT NULL REFERENCES users(id),
    overall_rating INTEGER CHECK (overall_rating BETWEEN 1 AND 5),
    teaching_effectiveness INTEGER CHECK (teaching_effectiveness BETWEEN 1 AND 5),
    student_engagement INTEGER CHECK (student_engagement BETWEEN 1 AND 5),
    professional_development INTEGER CHECK (professional_development BETWEEN 1 AND 5),
    teamwork INTEGER CHECK (teamwork BETWEEN 1 AND 5),
    strengths TEXT,
    areas_for_improvement TEXT,
    goals_next_period TEXT,
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Comments and Notes
COMMENT ON TABLE teachers IS 'Main teacher information and employment details';
COMMENT ON TABLE teacher_qualifications IS 'Teacher educational qualifications';
COMMENT ON TABLE teacher_experience IS 'Teacher previous work experience';
COMMENT ON TABLE teacher_subject_assignments IS 'Current subject and class assignments';
COMMENT ON TABLE teacher_documents IS 'Teacher document storage and verification';
COMMENT ON TABLE teacher_performance_reviews IS 'Teacher performance evaluation records';

COMMENT ON COLUMN teachers.employee_id IS 'Unique teacher employee ID';
COMMENT ON COLUMN teachers.position IS 'Job position/designation';
COMMENT ON COLUMN teachers.gender_id IS 'Foreign key reference to genders table';
COMMENT ON COLUMN teachers.qualification_id IS 'Foreign key reference to qualifications table (primary qualification)';
COMMENT ON COLUMN teachers.employment_status_id IS 'Foreign key reference to employment_statuses table';
COMMENT ON COLUMN teachers.class_teacher_of_id IS 'Foreign key reference to classes table for class teacher assignment';
COMMENT ON COLUMN teacher_qualifications.qualification_id IS 'Foreign key reference to qualifications table';
COMMENT ON COLUMN teacher_subject_assignments.class_id IS 'Foreign key reference to classes table';
COMMENT ON COLUMN teacher_subject_assignments.session_year_id IS 'Foreign key reference to session_years table';
