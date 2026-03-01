-- =====================================================
-- Migration: V031_add_session_year_id_to_stock_procurements.sql
-- Description: Add session_year_id to inventory_stock_procurements table
-- Author: System
-- Date: 2024
-- =====================================================

-- Add session_year_id column to inventory_stock_procurements
ALTER TABLE inventory_stock_procurements
ADD COLUMN IF NOT EXISTS session_year_id INTEGER;

-- Add foreign key constraint
ALTER TABLE inventory_stock_procurements
ADD CONSTRAINT fk_stock_procurements_session_year
FOREIGN KEY (session_year_id) REFERENCES session_years(id);

-- Backfill existing records with session_year_id = 4 (current session)
UPDATE inventory_stock_procurements
SET session_year_id = 4
WHERE session_year_id IS NULL;

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_stock_procurements_session_year
ON inventory_stock_procurements(session_year_id);

-- Add comment
COMMENT ON COLUMN inventory_stock_procurements.session_year_id IS 'Reference to session year for budgeting and reporting';

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
        AND table_name = 'inventory_stock_procurements'
        AND column_name = 'session_year_id'
    ) INTO column_exists;

    IF column_exists THEN
        RAISE NOTICE '✅ session_year_id column added to inventory_stock_procurements table';

        -- Count records with session_year_id set
        SELECT COUNT(*) INTO records_updated FROM inventory_stock_procurements WHERE session_year_id IS NOT NULL;
        RAISE NOTICE '✅ % records have session_year_id set', records_updated;
    ELSE
        RAISE WARNING '❌ session_year_id column not found in inventory_stock_procurements table';
    END IF;
END $$;

-- =====================================================
-- Rollback Script (if needed):
-- ALTER TABLE inventory_stock_procurements DROP CONSTRAINT IF EXISTS fk_stock_procurements_session_year;
-- DROP INDEX IF EXISTS idx_stock_procurements_session_year;
-- ALTER TABLE inventory_stock_procurements DROP COLUMN IF EXISTS session_year_id;
-- =====================================================

