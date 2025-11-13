-- =====================================================
-- Migration: V009 - Add Reversal Columns to monthly_payment_allocations
-- Description: Adds columns to support partial payment reversal functionality
-- Date: 2025-01-12
-- Dependencies: monthly_payment_allocations
-- =====================================================

-- Add new columns to monthly_payment_allocations table
ALTER TABLE monthly_payment_allocations 
ADD COLUMN IF NOT EXISTS is_reversal BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS reverses_allocation_id INTEGER;

-- Add foreign key constraint
ALTER TABLE monthly_payment_allocations 
ADD CONSTRAINT fk_monthly_allocations_reverses 
FOREIGN KEY (reverses_allocation_id) REFERENCES monthly_payment_allocations(id) ON DELETE SET NULL;

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_monthly_allocations_is_reversal ON monthly_payment_allocations(is_reversal);
CREATE INDEX IF NOT EXISTS idx_monthly_allocations_reverses_allocation_id ON monthly_payment_allocations(reverses_allocation_id);

-- Add comments
COMMENT ON COLUMN monthly_payment_allocations.is_reversal IS 'TRUE if this is a reversal allocation (negative amount)';
COMMENT ON COLUMN monthly_payment_allocations.reverses_allocation_id IS 'ID of the allocation being reversed (for reversal allocations)';

-- Add validation constraint: reversal allocations must have reverses_allocation_id
ALTER TABLE monthly_payment_allocations 
ADD CONSTRAINT chk_monthly_allocations_reversal_link 
CHECK (
    (is_reversal = FALSE) OR 
    (is_reversal = TRUE AND reverses_allocation_id IS NOT NULL)
);

-- Add validation constraint: non-reversal allocations should not have reverses_allocation_id
ALTER TABLE monthly_payment_allocations 
ADD CONSTRAINT chk_monthly_allocations_non_reversal_no_link 
CHECK (
    (is_reversal = TRUE) OR 
    (is_reversal = FALSE AND reverses_allocation_id IS NULL)
);

