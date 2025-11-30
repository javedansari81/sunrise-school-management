-- =====================================================
-- Table: attendance_periods
-- Description: Stores attendance period definitions (Full Day, Morning, Afternoon)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS attendance_periods CASCADE;

-- Create table
CREATE TABLE attendance_periods (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    start_time TIME,
    end_time TIME,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create index
CREATE INDEX IF NOT EXISTS idx_attendance_periods_active ON attendance_periods(is_active) WHERE is_active = TRUE;

-- Add comments
COMMENT ON TABLE attendance_periods IS 'Attendance period definitions for schools with multiple attendance sessions';
COMMENT ON COLUMN attendance_periods.name IS 'Database identifier (e.g., FULL_DAY, MORNING)';
COMMENT ON COLUMN attendance_periods.description IS 'Human-readable text for UI display';
COMMENT ON COLUMN attendance_periods.start_time IS 'Period start time';
COMMENT ON COLUMN attendance_periods.end_time IS 'Period end time';

