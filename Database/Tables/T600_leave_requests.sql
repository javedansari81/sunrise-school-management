-- =====================================================
-- Table: leave_requests
-- Description: Stores leave request records with approval workflow
-- Dependencies: users, leave_types, leave_statuses
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS leave_requests CASCADE;

-- Create table
CREATE TABLE leave_requests (
    id SERIAL PRIMARY KEY,

    -- Basic Information
    user_id INTEGER NOT NULL,
    leave_type_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INTEGER NOT NULL,
    reason TEXT NOT NULL,

    -- Applicant Information
    applicant_type VARCHAR(10) CHECK (applicant_type IN ('student', 'teacher')),
    applicant_id INTEGER,

    -- Session Year
    session_year_id INTEGER,

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
    FOREIGN KEY (approved_by) REFERENCES users(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_leave_requests_user ON leave_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_status ON leave_requests(leave_status_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_dates ON leave_requests(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_leave_requests_applicant_id ON leave_requests(applicant_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_applicant_id_type ON leave_requests(applicant_id, applicant_type);
CREATE INDEX IF NOT EXISTS idx_leave_requests_applicant_type ON leave_requests(applicant_type);
CREATE INDEX IF NOT EXISTS idx_leave_requests_user_applicant_type ON leave_requests(user_id, applicant_type);
CREATE INDEX IF NOT EXISTS idx_leave_requests_session_year ON leave_requests(session_year_id);

-- Add comments
COMMENT ON TABLE leave_requests IS 'Leave request records with approval workflow';
COMMENT ON COLUMN leave_requests.applicant_type IS 'Type of applicant: student or teacher (derived from users.user_type_id)';
COMMENT ON COLUMN leave_requests.applicant_id IS 'ID of the applicant (student.id or teacher.id) - used for business logic';
COMMENT ON COLUMN leave_requests.user_id IS 'User ID for authentication/authorization';

