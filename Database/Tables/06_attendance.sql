-- =====================================================
-- Attendance Management Tables
-- =====================================================

-- Student Attendance table (Daily attendance records)
CREATE TABLE IF NOT EXISTS student_attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    attendance_date DATE NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('Present', 'Absent', 'Late', 'Half Day')),
    
    -- Time Details
    check_in_time TIME,
    check_out_time TIME,
    late_minutes INTEGER DEFAULT 0,
    
    -- Subject-wise Attendance (for higher classes)
    subject VARCHAR(100),
    period_number INTEGER,
    
    -- Reason for Absence
    absence_reason VARCHAR(200),
    is_excused BOOLEAN DEFAULT FALSE,
    
    -- Recorded By
    marked_by INTEGER NOT NULL REFERENCES users(id),
    marked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Additional Info
    remarks TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Unique constraint to prevent duplicate entries
    UNIQUE(student_id, attendance_date, subject, period_number)
);

-- Teacher Attendance table (Staff attendance records)
CREATE TABLE IF NOT EXISTS teacher_attendance (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    attendance_date DATE NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('Present', 'Absent', 'Late', 'Half Day', 'On Leave')),
    
    -- Time Details
    check_in_time TIME,
    check_out_time TIME,
    total_hours DECIMAL(4,2),
    late_minutes INTEGER DEFAULT 0,
    
    -- Leave Details (if on leave)
    leave_type VARCHAR(30) CHECK (leave_type IN ('Sick Leave', 'Casual Leave', 'Emergency Leave', 'Medical Leave')),
    leave_reason VARCHAR(500),
    
    -- Substitute Teacher
    substitute_teacher_id INTEGER REFERENCES teachers(id),
    
    -- Recorded By
    marked_by INTEGER NOT NULL REFERENCES users(id),
    marked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Additional Info
    remarks TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Unique constraint
    UNIQUE(teacher_id, attendance_date)
);

-- Attendance Summary table (Monthly/Weekly summaries)
CREATE TABLE IF NOT EXISTS attendance_summary (
    id SERIAL PRIMARY KEY,
    person_id INTEGER NOT NULL, -- Can be student_id or teacher_id
    person_type VARCHAR(10) NOT NULL CHECK (person_type IN ('student', 'teacher')),
    summary_period VARCHAR(10) NOT NULL CHECK (summary_period IN ('weekly', 'monthly', 'yearly')),
    
    -- Period Details
    year INTEGER NOT NULL,
    month INTEGER CHECK (month BETWEEN 1 AND 12),
    week_number INTEGER CHECK (week_number BETWEEN 1 AND 53),
    
    -- Attendance Statistics
    total_days INTEGER NOT NULL,
    present_days INTEGER DEFAULT 0,
    absent_days INTEGER DEFAULT 0,
    late_days INTEGER DEFAULT 0,
    half_days INTEGER DEFAULT 0,
    leave_days INTEGER DEFAULT 0,
    
    -- Calculated Percentages
    attendance_percentage DECIMAL(5,2) DEFAULT 0.0,
    
    -- Timestamps
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint
    UNIQUE(person_id, person_type, summary_period, year, month, week_number)
);

-- Attendance Settings table (School attendance configuration)
CREATE TABLE IF NOT EXISTS attendance_settings (
    id SERIAL PRIMARY KEY,
    setting_name VARCHAR(100) UNIQUE NOT NULL,
    setting_value VARCHAR(500) NOT NULL,
    setting_type VARCHAR(20) NOT NULL CHECK (setting_type IN ('string', 'integer', 'decimal', 'boolean', 'time')),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    updated_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Attendance Notifications table (Absence notifications to parents)
CREATE TABLE IF NOT EXISTS attendance_notifications (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    attendance_date DATE NOT NULL,
    notification_type VARCHAR(20) NOT NULL CHECK (notification_type IN ('Email', 'SMS', 'Push')),
    recipient_contact VARCHAR(255) NOT NULL,
    message_content TEXT NOT NULL,
    
    -- Status
    sent_at TIMESTAMP WITH TIME ZONE,
    delivery_status VARCHAR(20) DEFAULT 'Pending' CHECK (delivery_status IN ('Pending', 'Sent', 'Delivered', 'Failed')),
    delivery_response TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Attendance Reports table (Generated attendance reports)
CREATE TABLE IF NOT EXISTS attendance_reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL, -- 'Daily Attendance', 'Monthly Summary', 'Low Attendance Alert', etc.
    report_name VARCHAR(200) NOT NULL,
    parameters JSONB, -- Report parameters like date range, class, etc.
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

-- Holiday Calendar table (School holidays and working days)
CREATE TABLE IF NOT EXISTS holiday_calendar (
    id SERIAL PRIMARY KEY,
    holiday_date DATE UNIQUE NOT NULL,
    holiday_name VARCHAR(200) NOT NULL,
    holiday_type VARCHAR(50) NOT NULL, -- 'National Holiday', 'School Holiday', 'Festival', 'Exam Day', etc.
    is_working_day BOOLEAN DEFAULT FALSE, -- Some holidays might be working days
    description TEXT,
    
    -- Academic Year
    academic_year VARCHAR(10) NOT NULL CHECK (academic_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27')),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id)
);

-- Comments and Notes
COMMENT ON TABLE student_attendance IS 'Daily attendance records for students';
COMMENT ON TABLE teacher_attendance IS 'Daily attendance records for teachers';
COMMENT ON TABLE attendance_summary IS 'Periodic attendance summaries and statistics';
COMMENT ON TABLE attendance_settings IS 'School attendance system configuration';
COMMENT ON TABLE attendance_notifications IS 'Absence notifications sent to parents';
COMMENT ON TABLE attendance_reports IS 'Generated attendance reports';
COMMENT ON TABLE holiday_calendar IS 'School holiday calendar and working days';

COMMENT ON COLUMN student_attendance.status IS 'Attendance status: Present, Absent, Late, Half Day';
COMMENT ON COLUMN teacher_attendance.status IS 'Attendance status: Present, Absent, Late, Half Day, On Leave';
COMMENT ON COLUMN attendance_summary.person_type IS 'Type of person: student or teacher';
