-- =====================================================
-- Function: calculate_fee_balance
-- Description: Trigger function to automatically calculate balance_amount in fee_records
-- Parameters: None (trigger function)
-- Returns: TRIGGER
-- Dependencies: None
-- =====================================================

-- Drop existing function
DROP FUNCTION IF EXISTS calculate_fee_balance() CASCADE;

-- Create function
CREATE OR REPLACE FUNCTION calculate_fee_balance()
RETURNS TRIGGER AS $$
BEGIN
    NEW.balance_amount := NEW.total_amount - COALESCE(NEW.paid_amount, 0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add comment
COMMENT ON FUNCTION calculate_fee_balance() IS 'Trigger function to calculate balance_amount as total_amount - paid_amount';

-- Create trigger on fee_records table
DROP TRIGGER IF EXISTS trg_calculate_fee_balance ON fee_records;
CREATE TRIGGER trg_calculate_fee_balance
    BEFORE INSERT OR UPDATE ON fee_records
    FOR EACH ROW
    EXECUTE FUNCTION calculate_fee_balance();

COMMENT ON TRIGGER trg_calculate_fee_balance ON fee_records IS 'Automatically calculates balance_amount before insert or update';

