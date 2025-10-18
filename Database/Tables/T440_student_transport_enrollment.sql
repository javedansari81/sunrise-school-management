-- =====================================================
-- Table: student_transport_enrollment
-- Description: Tracks student enrollment in transport services
-- Dependencies: students, session_years, transport_types
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS student_transport_enrollment CASCADE;

-- Create table
CREATE TABLE student_transport_enrollment (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    transport_type_id INTEGER NOT NULL,
    
    -- Enrollment Details
    enrollment_date DATE NOT NULL,
    discontinue_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Distance and Pricing
    distance_km DECIMAL(5,2),
    monthly_fee DECIMAL(10,2) NOT NULL,
    
    -- Additional Information
    pickup_location TEXT,
    drop_location TEXT,
    remarks TEXT,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Foreign Key Constraints
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    FOREIGN KEY (transport_type_id) REFERENCES transport_types(id)
);

-- Add indexes
CREATE INDEX idx_transport_enrollment_student ON student_transport_enrollment(student_id);
CREATE INDEX idx_transport_enrollment_session ON student_transport_enrollment(session_year_id);
CREATE INDEX idx_transport_enrollment_type ON student_transport_enrollment(transport_type_id);
CREATE INDEX idx_transport_enrollment_active ON student_transport_enrollment(is_active);

-- Add unique constraint for active enrollments
CREATE UNIQUE INDEX idx_transport_enrollment_unique_active 
ON student_transport_enrollment(student_id, session_year_id) 
WHERE is_active = TRUE AND discontinue_date IS NULL;

-- Add comments
COMMENT ON TABLE student_transport_enrollment IS 'Student enrollment in transport services with pricing and distance tracking';
COMMENT ON COLUMN student_transport_enrollment.student_id IS 'Foreign key to students table';
COMMENT ON COLUMN student_transport_enrollment.session_year_id IS 'Foreign key to session_years table';
COMMENT ON COLUMN student_transport_enrollment.transport_type_id IS 'Foreign key to transport_types table';
COMMENT ON COLUMN student_transport_enrollment.enrollment_date IS 'Date when student opted for transport service';
COMMENT ON COLUMN student_transport_enrollment.discontinue_date IS 'Date when student discontinued service (NULL = active)';
COMMENT ON COLUMN student_transport_enrollment.is_active IS 'Current enrollment status';
COMMENT ON COLUMN student_transport_enrollment.distance_km IS 'Distance from school in kilometers';
COMMENT ON COLUMN student_transport_enrollment.monthly_fee IS 'Monthly transport fee for this student';
COMMENT ON COLUMN student_transport_enrollment.pickup_location IS 'Student pickup location/address';
COMMENT ON COLUMN student_transport_enrollment.drop_location IS 'Student drop location/address';

