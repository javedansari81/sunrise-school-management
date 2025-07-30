-- =====================================================
-- Student Management Tables
-- =====================================================

-- Students table (Main student information)
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    admission_number VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    blood_group VARCHAR(5),
    
    -- Contact Information
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'India',
    
    -- Academic Information
    class VARCHAR(20) NOT NULL,
    section VARCHAR(10),
    roll_number VARCHAR(20),
    admission_date DATE NOT NULL,
    session_year VARCHAR(10) NOT NULL CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27')),
    
    -- Parent/Guardian Information
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
    
    -- Emergency Contact
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relation VARCHAR(50),
    
    -- Medical Information
    medical_conditions TEXT,
    allergies TEXT,
    medications TEXT,
    
    -- Academic Status
    is_active BOOLEAN DEFAULT TRUE,
    graduation_date DATE,
    
    -- Documents and Photos
    photo_url VARCHAR(500),
    birth_certificate_url VARCHAR(500),
    address_proof_url VARCHAR(500),
    
    -- Additional Information
    transport_required BOOLEAN DEFAULT FALSE,
    transport_route VARCHAR(100),
    hostel_required BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Student Academic History table
CREATE TABLE IF NOT EXISTS student_academic_history (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year VARCHAR(10) NOT NULL CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27')),
    class VARCHAR(20) NOT NULL,
    section VARCHAR(10),
    roll_number VARCHAR(20),
    promoted BOOLEAN DEFAULT FALSE,
    promotion_date DATE,
    remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Student Documents table
CREATE TABLE IF NOT EXISTS student_documents (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
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

-- Student Notes table (for administrative notes)
CREATE TABLE IF NOT EXISTS student_notes (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    note_type VARCHAR(50) NOT NULL, -- 'academic', 'behavioral', 'medical', 'general'
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_confidential BOOLEAN DEFAULT FALSE,
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Comments and Notes
COMMENT ON TABLE students IS 'Main student information and enrollment details';
COMMENT ON TABLE student_academic_history IS 'Historical record of student class promotions';
COMMENT ON TABLE student_documents IS 'Student document storage and verification';
COMMENT ON TABLE student_notes IS 'Administrative notes about students';

COMMENT ON COLUMN students.admission_number IS 'Unique student admission number';
COMMENT ON COLUMN students.session_year IS 'Current academic session year';
COMMENT ON COLUMN students.is_active IS 'Whether the student is currently enrolled';
COMMENT ON COLUMN student_notes.note_type IS 'Type of note: academic, behavioral, medical, general';
COMMENT ON COLUMN student_notes.is_confidential IS 'Whether the note is confidential';
