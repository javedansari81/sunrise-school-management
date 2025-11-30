-- =====================================================
-- Table: attendance_statuses
-- Description: Stores attendance status definitions (Present, Absent, Late, etc.)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS attendance_statuses CASCADE;

-- Create table
CREATE TABLE attendance_statuses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color_code VARCHAR(10),
    affects_attendance_percentage BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create index
CREATE INDEX IF NOT EXISTS idx_attendance_statuses_active ON attendance_statuses(is_active) WHERE is_active = TRUE;

-- Add comments
COMMENT ON TABLE attendance_statuses IS 'Attendance status definitions with color codes for UI display';
COMMENT ON COLUMN attendance_statuses.name IS 'Database identifier (e.g., PRESENT, ABSENT)';
COMMENT ON COLUMN attendance_statuses.description IS 'Human-readable text for UI display';
COMMENT ON COLUMN attendance_statuses.color_code IS 'Hex color code for UI display';
COMMENT ON COLUMN attendance_statuses.affects_attendance_percentage IS 'Whether this status counts towards attendance percentage calculation';

