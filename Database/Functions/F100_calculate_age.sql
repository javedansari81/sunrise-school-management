-- =====================================================
-- Function: calculate_age
-- Description: Calculates age from date of birth
-- Parameters: birth_date (DATE)
-- Returns: INTEGER (age in years)
-- Dependencies: None
-- =====================================================

-- Drop existing function
DROP FUNCTION IF EXISTS calculate_age(DATE);

-- Create function
CREATE OR REPLACE FUNCTION calculate_age(birth_date DATE)
RETURNS INTEGER AS $$
BEGIN
    RETURN EXTRACT(YEAR FROM AGE(birth_date));
END;
$$ LANGUAGE plpgsql;

-- Add comment
COMMENT ON FUNCTION calculate_age(DATE) IS 'Calculates age in years from date of birth';

