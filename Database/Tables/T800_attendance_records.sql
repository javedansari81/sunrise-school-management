-- =====================================================
-- Table: attendance_records
-- Description: Stores daily attendance records for students
-- Dependencies: students, classes, session_years, attendance_statuses, attendance_periods, users, leave_requests
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS attendance_records CASCADE;

-- Create table
CREATE TABLE attendance_records (
    id SERIAL PRIMARY KEY,
    
    -- Student Information
    student_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    
    -- Attendance Details
    attendance_date DATE NOT NULL,
    attendance_status_id INTEGER NOT NULL,
    attendance_period_id INTEGER DEFAULT 1,
    
    -- Time Tracking
    check_in_time TIME,
    check_out_time TIME,
    
    -- Additional Information
    remarks TEXT,
    marked_by INTEGER NOT NULL,
    
    -- Leave Integration (Optional)
    leave_request_id INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Foreign Key Constraints
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    FOREIGN KEY (attendance_status_id) REFERENCES attendance_statuses(id),
    FOREIGN KEY (attendance_period_id) REFERENCES attendance_periods(id),
    FOREIGN KEY (marked_by) REFERENCES users(id),
    FOREIGN KEY (leave_request_id) REFERENCES leave_requests(id),
    
    -- Unique constraint: One attendance record per student per date per period
    UNIQUE(student_id, attendance_date, attendance_period_id)
);

-- Performance Indexes (following existing patterns)
CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance_records(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance_records(attendance_date);
CREATE INDEX IF NOT EXISTS idx_attendance_class ON attendance_records(class_id);
CREATE INDEX IF NOT EXISTS idx_attendance_session ON attendance_records(session_year_id);
CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance_records(attendance_status_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date_class ON attendance_records(attendance_date, class_id);
CREATE INDEX IF NOT EXISTS idx_attendance_student_date_range ON attendance_records(student_id, attendance_date);
CREATE INDEX IF NOT EXISTS idx_attendance_marked_by ON attendance_records(marked_by);
CREATE INDEX IF NOT EXISTS idx_attendance_period ON attendance_records(attendance_period_id);
CREATE INDEX IF NOT EXISTS idx_attendance_leave_request ON attendance_records(leave_request_id) WHERE leave_request_id IS NOT NULL;

-- Add comments
COMMENT ON TABLE attendance_records IS 'Daily attendance records for students with full audit trail';
COMMENT ON COLUMN attendance_records.student_id IS 'Foreign key to students table';
COMMENT ON COLUMN attendance_records.class_id IS 'Foreign key to classes table';
COMMENT ON COLUMN attendance_records.session_year_id IS 'Foreign key to session_years table';
COMMENT ON COLUMN attendance_records.attendance_date IS 'Date of attendance record';
COMMENT ON COLUMN attendance_records.attendance_status_id IS 'Foreign key to attendance_statuses (Present, Absent, Late, etc.)';
COMMENT ON COLUMN attendance_records.attendance_period_id IS 'Foreign key to attendance_periods (Full Day, Morning, Afternoon)';
COMMENT ON COLUMN attendance_records.check_in_time IS 'Time when student checked in (optional)';
COMMENT ON COLUMN attendance_records.check_out_time IS 'Time when student checked out (optional)';
COMMENT ON COLUMN attendance_records.remarks IS 'Additional notes or comments';
COMMENT ON COLUMN attendance_records.marked_by IS 'User ID of teacher/admin who marked attendance';
COMMENT ON COLUMN attendance_records.leave_request_id IS 'Links to approved leave request if applicable';

