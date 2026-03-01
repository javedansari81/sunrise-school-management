-- =====================================================
-- Migration: V030_add_session_year_id_to_alerts
-- Description: Add session_year_id column to alerts table
--              to enable filtering alerts by academic session
-- =====================================================

-- Add session_year_id column
ALTER TABLE alerts
ADD COLUMN IF NOT EXISTS session_year_id INTEGER;

-- Add foreign key constraint
ALTER TABLE alerts
ADD CONSTRAINT fk_alerts_session_year 
    FOREIGN KEY (session_year_id) REFERENCES session_years(id);

-- Backfill existing records with session_year_id = 4 (current session)
UPDATE alerts
SET session_year_id = 4
WHERE session_year_id IS NULL;

-- Create index for query optimization
CREATE INDEX IF NOT EXISTS idx_alerts_session_year 
    ON alerts(session_year_id);

-- Add comment
COMMENT ON COLUMN alerts.session_year_id IS 'Academic session year for the alert';

-- Verification
DO $$
DECLARE
    column_exists BOOLEAN;
    records_updated INTEGER;
BEGIN
    -- Check if column exists
    SELECT EXISTS(
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'sunrise' 
        AND table_name = 'alerts' 
        AND column_name = 'session_year_id'
    ) INTO column_exists;

    IF column_exists THEN
        RAISE NOTICE '✅ session_year_id column added to alerts table';
        
        -- Count records with session_year_id set
        SELECT COUNT(*) INTO records_updated FROM alerts WHERE session_year_id IS NOT NULL;
        RAISE NOTICE '✅ % records have session_year_id set', records_updated;
    ELSE
        RAISE WARNING '❌ session_year_id column not found in alerts table';
    END IF;
END $$;

