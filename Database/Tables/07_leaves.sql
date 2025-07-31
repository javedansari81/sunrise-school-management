-- =====================================================
-- Leave Management Tables
-- =====================================================

-- Leave Requests table (Student and Teacher leave applications) - Updated for metadata-driven architecture
CREATE TABLE IF NOT EXISTS leave_requests (
    id SERIAL PRIMARY KEY,
    applicant_id INTEGER NOT NULL, -- Can be student_id or teacher_id
    applicant_type VARCHAR(10) NOT NULL CHECK (applicant_type IN ('student', 'teacher')),

    -- Leave Details
    leave_type_id INTEGER NOT NULL REFERENCES leave_types(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INTEGER NOT NULL,
    reason TEXT NOT NULL,

    -- Supporting Documents
    medical_certificate_url VARCHAR(500),
    supporting_document_url VARCHAR(500),

    -- Application Status
    leave_status_id INTEGER DEFAULT 1 REFERENCES leave_statuses(id),
    
    -- Approval Workflow
    applied_to INTEGER REFERENCES users(id), -- Teacher/Principal who should approve
    reviewed_by INTEGER REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_comments TEXT,
    
    -- For Teachers - Substitute Arrangement
    substitute_teacher_id INTEGER REFERENCES teachers(id),
    substitute_arranged BOOLEAN DEFAULT FALSE,
    
    -- For Students - Parent Consent
    parent_consent BOOLEAN DEFAULT FALSE,
    parent_signature_url VARCHAR(500),
    
    -- Emergency Contact (for students)
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    
    -- Additional Information
    is_half_day BOOLEAN DEFAULT FALSE,
    half_day_session VARCHAR(10) CHECK (half_day_session IN ('morning', 'afternoon')),
    
    -- Timestamps
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Leave Balance table (Available leave balance for teachers) - Updated for metadata-driven architecture
CREATE TABLE IF NOT EXISTS leave_balance (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER UNIQUE NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    
    -- Leave Entitlements
    casual_leave_total INTEGER DEFAULT 12,
    casual_leave_used INTEGER DEFAULT 0,
    casual_leave_balance INTEGER DEFAULT 12,
    
    sick_leave_total INTEGER DEFAULT 12,
    sick_leave_used INTEGER DEFAULT 0,
    sick_leave_balance INTEGER DEFAULT 12,
    
    earned_leave_total INTEGER DEFAULT 20,
    earned_leave_used INTEGER DEFAULT 0,
    earned_leave_balance INTEGER DEFAULT 20,
    
    maternity_leave_total INTEGER DEFAULT 180,
    maternity_leave_used INTEGER DEFAULT 0,
    maternity_leave_balance INTEGER DEFAULT 180,
    
    paternity_leave_total INTEGER DEFAULT 15,
    paternity_leave_used INTEGER DEFAULT 0,
    paternity_leave_balance INTEGER DEFAULT 15,
    
    -- Carry Forward
    carry_forward_from_previous INTEGER DEFAULT 0,
    
    -- Timestamps
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint
    UNIQUE(teacher_id, session_year_id)
);

-- Leave Policies table (Leave policy configuration) - Updated for metadata-driven architecture
CREATE TABLE IF NOT EXISTS leave_policies (
    id SERIAL PRIMARY KEY,
    policy_name VARCHAR(100) UNIQUE NOT NULL,
    applicant_type VARCHAR(10) NOT NULL CHECK (applicant_type IN ('student', 'teacher', 'both')),
    leave_type_id INTEGER NOT NULL REFERENCES leave_types(id),
    
    -- Policy Rules
    max_days_per_application INTEGER,
    max_days_per_year INTEGER,
    min_notice_days INTEGER DEFAULT 1,
    requires_medical_certificate BOOLEAN DEFAULT FALSE,
    requires_approval BOOLEAN DEFAULT TRUE,
    
    -- Approval Hierarchy
    approval_levels JSONB, -- JSON array of approval levels
    
    -- Validity
    effective_from DATE NOT NULL,
    effective_to DATE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Additional Rules
    can_be_carried_forward BOOLEAN DEFAULT FALSE,
    carry_forward_limit INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER REFERENCES users(id)
);

-- Leave Approvers table (Who can approve different types of leaves) - Updated for metadata-driven architecture
CREATE TABLE IF NOT EXISTS leave_approvers (
    id SERIAL PRIMARY KEY,
    approver_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    leave_type_id INTEGER NOT NULL REFERENCES leave_types(id),
    applicant_type VARCHAR(10) NOT NULL CHECK (applicant_type IN ('student', 'teacher')),
    
    -- Approval Limits
    max_days_can_approve INTEGER,
    
    -- Scope
    can_approve_all BOOLEAN DEFAULT FALSE,
    specific_classes TEXT, -- JSON array of classes they can approve for students
    specific_departments TEXT, -- JSON array of departments they can approve for teachers
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by INTEGER REFERENCES users(id)
);

-- Leave Calendar table (Leave calendar view) - Updated for metadata-driven architecture
CREATE TABLE IF NOT EXISTS leave_calendar (
    id SERIAL PRIMARY KEY,
    leave_request_id INTEGER NOT NULL REFERENCES leave_requests(id) ON DELETE CASCADE,
    leave_date DATE NOT NULL,
    applicant_id INTEGER NOT NULL,
    applicant_type VARCHAR(10) NOT NULL CHECK (applicant_type IN ('student', 'teacher')),
    leave_type_id INTEGER NOT NULL REFERENCES leave_types(id),
    is_half_day BOOLEAN DEFAULT FALSE,
    half_day_session VARCHAR(10) CHECK (half_day_session IN ('morning', 'afternoon')),
    
    -- For quick queries
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL, -- 1=Monday, 7=Sunday
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Leave Notifications table (Leave-related notifications)
CREATE TABLE IF NOT EXISTS leave_notifications (
    id SERIAL PRIMARY KEY,
    leave_request_id INTEGER NOT NULL REFERENCES leave_requests(id) ON DELETE CASCADE,
    recipient_id INTEGER NOT NULL REFERENCES users(id),
    notification_type VARCHAR(20) NOT NULL CHECK (notification_type IN ('Email', 'SMS', 'Push', 'In-App')),
    
    -- Message Details
    subject VARCHAR(200),
    message_content TEXT NOT NULL,
    
    -- Status
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Sent', 'Delivered', 'Read', 'Failed')),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Leave Reports table (Generated leave reports)
CREATE TABLE IF NOT EXISTS leave_reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL, -- 'Monthly Leave Summary', 'Leave Balance Report', 'Pending Applications', etc.
    report_name VARCHAR(200) NOT NULL,
    parameters JSONB, -- Report parameters
    file_url VARCHAR(500),
    file_format VARCHAR(10), -- 'PDF', 'Excel', 'CSV'
    
    -- Generation Details
    generated_by INTEGER NOT NULL REFERENCES users(id),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    generation_time_ms INTEGER,
    
    -- Access Control
    is_public BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Comments and Notes
COMMENT ON TABLE leave_requests IS 'Leave applications from students and teachers';
COMMENT ON TABLE leave_balance IS 'Leave balance tracking for teachers';
COMMENT ON TABLE leave_policies IS 'Leave policy configuration and rules';
COMMENT ON TABLE leave_approvers IS 'Users authorized to approve leave requests';
COMMENT ON TABLE leave_calendar IS 'Calendar view of approved leaves';
COMMENT ON TABLE leave_notifications IS 'Leave-related notifications and communications';
COMMENT ON TABLE leave_reports IS 'Generated leave management reports';

COMMENT ON COLUMN leave_requests.applicant_type IS 'Type of applicant: student or teacher';
COMMENT ON COLUMN leave_requests.leave_type_id IS 'Foreign key reference to leave_types table';
COMMENT ON COLUMN leave_requests.leave_status_id IS 'Foreign key reference to leave_statuses table';
COMMENT ON COLUMN leave_balance.session_year_id IS 'Foreign key reference to session_years table';
COMMENT ON COLUMN leave_policies.leave_type_id IS 'Foreign key reference to leave_types table';
COMMENT ON COLUMN leave_approvers.leave_type_id IS 'Foreign key reference to leave_types table';
COMMENT ON COLUMN leave_calendar.leave_type_id IS 'Foreign key reference to leave_types table';
