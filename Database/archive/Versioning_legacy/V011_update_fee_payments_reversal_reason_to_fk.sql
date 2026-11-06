-- =====================================================
-- Migration: Update fee_payments to use reversal_reason_id FK
-- Description: Replace reversal_reason VARCHAR with reversal_reason_id FK
-- =====================================================

-- Step 1: Add new reversal_reason_id column
ALTER TABLE fee_payments 
ADD COLUMN IF NOT EXISTS reversal_reason_id INTEGER;

-- Step 2: Add foreign key constraint (only if it doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_fee_payments_reversal_reason'
    ) THEN
        ALTER TABLE fee_payments
        ADD CONSTRAINT fk_fee_payments_reversal_reason
        FOREIGN KEY (reversal_reason_id) REFERENCES reversal_reasons(id)
        ON DELETE SET NULL;
    END IF;
END $$;

-- Step 3: Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_fee_payments_reversal_reason_id 
ON fee_payments(reversal_reason_id);

-- Step 4: Migrate existing data (if any)
-- Map old reversal_reason VARCHAR values to new reversal_reason_id
UPDATE fee_payments
SET reversal_reason_id = CASE
    WHEN reversal_reason = 'Incorrect Amount Entered' THEN 1
    WHEN reversal_reason = 'Duplicate Payment' THEN 2
    WHEN reversal_reason = 'Wrong Student Account' THEN 3
    WHEN reversal_reason = 'Wrong Payment Method' THEN 4
    WHEN reversal_reason = 'Payment Processing Error' THEN 5
    WHEN reversal_reason = 'Student Request/Refund' THEN 6
    WHEN reversal_reason = 'Administrative Correction' THEN 7
    WHEN reversal_reason = 'Other' THEN 8
    ELSE NULL
END
WHERE reversal_reason IS NOT NULL AND reversal_reason_id IS NULL;

-- Step 5: Drop old reversal_reason column
ALTER TABLE fee_payments
DROP COLUMN IF EXISTS reversal_reason;

-- Step 6: Add comment
COMMENT ON COLUMN fee_payments.reversal_reason_id IS 'Foreign key to reversal_reasons table';

