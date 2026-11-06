-- =====================================================
-- Migration: V029_add_session_year_id_to_leave_requests
-- Description: Add session_year_id column to leave_requests table
--              to enable filtering leave records by academic session
-- =====================================================

-- Add session_year_id column
ALTER TABLE leave_requests
ADD COLUMN IF NOT EXISTS session_year_id INTEGER;

-- Add foreign key constraint
ALTER TABLE leave_requests
ADD CONSTRAINT fk_leave_requests_session_year 
    FOREIGN KEY (session_year_id) REFERENCES session_years(id);

-- Backfill existing records with session_year_id = 4 (current session)
UPDATE leave_requests
SET session_year_id = 4
WHERE session_year_id IS NULL;

-- Create index for query optimization
CREATE INDEX IF NOT EXISTS idx_leave_requests_session_year 
    ON leave_requests(session_year_id);

-- Add comment
COMMENT ON COLUMN leave_requests.session_year_id IS 'Academic session year for the leave request';

