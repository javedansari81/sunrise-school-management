-- =====================================================
-- Table: student_session_history
-- Description: Tracks student progression history across session years
-- Dependencies: students, session_years, classes, progression_actions, users
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS student_session_history CASCADE;

-- Create table
CREATE TABLE student_session_history (
    id SERIAL PRIMARY KEY,

    -- Student and Session Reference
    student_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,

    -- Session-Specific Academic Info
    section VARCHAR(10),
    roll_number VARCHAR(20),

    -- Progression Details (references metadata table)
    progression_action_id INTEGER NOT NULL,
    from_session_year_id INTEGER,
    from_class_id INTEGER,

    -- Batch Tracking (for bulk operations and rollback)
    progression_batch_id VARCHAR(50),

    -- Audit Fields
    progressed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    progressed_by INTEGER NOT NULL,
    remarks TEXT,

    -- Optional: Snapshot of student data at time of progression (JSONB)
    snapshot_data JSONB,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    -- Foreign Keys
    CONSTRAINT fk_session_history_student 
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    CONSTRAINT fk_session_history_session_year 
        FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    CONSTRAINT fk_session_history_class 
        FOREIGN KEY (class_id) REFERENCES classes(id),
    CONSTRAINT fk_session_history_progression_action 
        FOREIGN KEY (progression_action_id) REFERENCES progression_actions(id),
    CONSTRAINT fk_session_history_from_session_year 
        FOREIGN KEY (from_session_year_id) REFERENCES session_years(id),
    CONSTRAINT fk_session_history_from_class 
        FOREIGN KEY (from_class_id) REFERENCES classes(id),
    CONSTRAINT fk_session_history_progressed_by 
        FOREIGN KEY (progressed_by) REFERENCES users(id),

    -- Constraints: One record per student per session year
    CONSTRAINT uq_student_session_year UNIQUE(student_id, session_year_id)
);

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_session_history_student ON student_session_history(student_id);
CREATE INDEX IF NOT EXISTS idx_session_history_session ON student_session_history(session_year_id);
CREATE INDEX IF NOT EXISTS idx_session_history_class ON student_session_history(class_id);
CREATE INDEX IF NOT EXISTS idx_session_history_action ON student_session_history(progression_action_id);
CREATE INDEX IF NOT EXISTS idx_session_history_batch ON student_session_history(progression_batch_id);
CREATE INDEX IF NOT EXISTS idx_session_history_progressed_at ON student_session_history(progressed_at);

-- Composite index for common query: students in a class for a session
CREATE INDEX IF NOT EXISTS idx_session_history_session_class 
    ON student_session_history(session_year_id, class_id);

-- Add comments
COMMENT ON TABLE student_session_history IS 'Tracks student progression history across academic session years';
COMMENT ON COLUMN student_session_history.student_id IS 'Reference to the student';
COMMENT ON COLUMN student_session_history.session_year_id IS 'The session year this record is for';
COMMENT ON COLUMN student_session_history.class_id IS 'The class the student was in for this session';
COMMENT ON COLUMN student_session_history.section IS 'Section within the class (A, B, C, etc.)';
COMMENT ON COLUMN student_session_history.roll_number IS 'Roll number for this session';
COMMENT ON COLUMN student_session_history.progression_action_id IS 'How the student got to this session (PROMOTED, RETAINED, etc.)';
COMMENT ON COLUMN student_session_history.from_session_year_id IS 'Previous session year (NULL for NEW_ADMISSION)';
COMMENT ON COLUMN student_session_history.from_class_id IS 'Previous class (NULL for NEW_ADMISSION)';
COMMENT ON COLUMN student_session_history.progression_batch_id IS 'Batch ID for bulk operations and rollback support';
COMMENT ON COLUMN student_session_history.progressed_by IS 'User who performed the progression';
COMMENT ON COLUMN student_session_history.remarks IS 'Optional notes about the progression';
COMMENT ON COLUMN student_session_history.snapshot_data IS 'Optional JSONB snapshot of student data at progression time';

