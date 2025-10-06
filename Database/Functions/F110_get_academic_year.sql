-- =====================================================
-- Function: get_academic_year
-- Description: Returns academic year for a given date (April to March in India)
-- Parameters: input_date (DATE)
-- Returns: VARCHAR (academic year in format YYYY-YY)
-- Dependencies: None
-- =====================================================

-- Drop existing function
DROP FUNCTION IF EXISTS get_academic_year(DATE);

-- Create function
CREATE OR REPLACE FUNCTION get_academic_year(input_date DATE DEFAULT CURRENT_DATE)
RETURNS VARCHAR AS $$
DECLARE
    year_start INTEGER;
    year_end INTEGER;
BEGIN
    -- Academic year in India runs from April to March
    IF EXTRACT(MONTH FROM input_date) >= 4 THEN
        year_start := EXTRACT(YEAR FROM input_date);
        year_end := year_start + 1;
    ELSE
        year_end := EXTRACT(YEAR FROM input_date);
        year_start := year_end - 1;
    END IF;
    
    RETURN year_start || '-' || SUBSTRING(year_end::TEXT FROM 3 FOR 2);
END;
$$ LANGUAGE plpgsql;

-- Add comment
COMMENT ON FUNCTION get_academic_year(DATE) IS 'Returns academic year in format YYYY-YY (April to March)';

