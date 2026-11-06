-- =====================================================
-- Migration: Add Sibling Fee Waiver Columns
-- Description: Add columns to support sibling-based fee waivers
-- Dependencies: fee_records, monthly_fee_tracking tables
-- =====================================================

-- Add columns to fee_records table
ALTER TABLE fee_records 
ADD COLUMN IF NOT EXISTS has_sibling_waiver BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS sibling_waiver_percentage DECIMAL(5,2) DEFAULT 0.00 CHECK (sibling_waiver_percentage >= 0 AND sibling_waiver_percentage <= 100),
ADD COLUMN IF NOT EXISTS original_total_amount DECIMAL(10,2);

-- Add comments for fee_records columns
COMMENT ON COLUMN fee_records.has_sibling_waiver IS 'Whether this fee record has a sibling-based waiver applied';
COMMENT ON COLUMN fee_records.sibling_waiver_percentage IS 'Percentage of fee waived due to sibling discount (0-100)';
COMMENT ON COLUMN fee_records.original_total_amount IS 'Original total amount before sibling waiver applied';

-- Add columns to monthly_fee_tracking table
ALTER TABLE monthly_fee_tracking 
ADD COLUMN IF NOT EXISTS original_monthly_amount DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS fee_waiver_percentage DECIMAL(5,2) DEFAULT 0.00 CHECK (fee_waiver_percentage >= 0 AND fee_waiver_percentage <= 100),
ADD COLUMN IF NOT EXISTS waiver_reason TEXT;

-- Add comments for monthly_fee_tracking columns
COMMENT ON COLUMN monthly_fee_tracking.original_monthly_amount IS 'Original monthly amount before any waiver applied';
COMMENT ON COLUMN monthly_fee_tracking.fee_waiver_percentage IS 'Percentage of fee waived (0-100)';
COMMENT ON COLUMN monthly_fee_tracking.waiver_reason IS 'Reason for fee waiver (e.g., "Sibling discount - youngest of 3")';

-- Create index for querying students with waivers
CREATE INDEX IF NOT EXISTS idx_fee_records_sibling_waiver ON fee_records(has_sibling_waiver) WHERE has_sibling_waiver = TRUE;
CREATE INDEX IF NOT EXISTS idx_monthly_fee_tracking_waiver ON monthly_fee_tracking(fee_waiver_percentage) WHERE fee_waiver_percentage > 0;

-- Update existing records to set original amounts (for records without waivers)
UPDATE fee_records 
SET original_total_amount = total_amount 
WHERE original_total_amount IS NULL AND has_sibling_waiver = FALSE;

UPDATE monthly_fee_tracking 
SET original_monthly_amount = monthly_amount 
WHERE original_monthly_amount IS NULL AND fee_waiver_percentage = 0;

