-- =====================================================
-- Function: calculate_sibling_fee_waiver
-- Description: Calculate fee waiver percentage based on sibling count and birth order
-- Parameters:
--   p_total_siblings: Total number of siblings including current student
--   p_birth_order: Birth order of the student (1=eldest, 2=second, etc.)
-- Returns: Fee waiver percentage (0-100)
-- Business Rules:
--   - 3 siblings: Youngest gets 100% waiver
--   - 4 siblings: 2nd youngest gets 50%, youngest gets 100%
--   - 5+ siblings: 2nd youngest gets 100%, youngest gets 100%
-- =====================================================

DROP FUNCTION IF EXISTS calculate_sibling_fee_waiver(INTEGER, INTEGER);

CREATE OR REPLACE FUNCTION calculate_sibling_fee_waiver(
    p_total_siblings INTEGER,
    p_birth_order INTEGER
) RETURNS DECIMAL(5,2) AS $$
DECLARE
    v_waiver_percentage DECIMAL(5,2) := 0.00;
BEGIN
    -- Validate inputs
    IF p_total_siblings IS NULL OR p_birth_order IS NULL THEN
        RETURN 0.00;
    END IF;
    
    IF p_birth_order > p_total_siblings THEN
        RETURN 0.00;
    END IF;
    
    -- Calculate waiver based on business rules
    IF p_total_siblings = 3 THEN
        -- 3 siblings: Only youngest (birth_order = 3) gets 100% waiver
        IF p_birth_order = 3 THEN
            v_waiver_percentage := 100.00;
        END IF;
        
    ELSIF p_total_siblings = 4 THEN
        -- 4 siblings: 2nd youngest (birth_order = 3) gets 50%, youngest (birth_order = 4) gets 100%
        IF p_birth_order = 3 THEN
            v_waiver_percentage := 50.00;
        ELSIF p_birth_order = 4 THEN
            v_waiver_percentage := 100.00;
        END IF;
        
    ELSIF p_total_siblings >= 5 THEN
        -- 5+ siblings: 2nd youngest and youngest both get 100%
        IF p_birth_order = p_total_siblings - 1 THEN
            -- 2nd youngest
            v_waiver_percentage := 100.00;
        ELSIF p_birth_order = p_total_siblings THEN
            -- Youngest
            v_waiver_percentage := 100.00;
        END IF;
    END IF;
    
    RETURN v_waiver_percentage;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Add comment
COMMENT ON FUNCTION calculate_sibling_fee_waiver(INTEGER, INTEGER) IS 
'Calculate fee waiver percentage based on total siblings and birth order. 
Rules: 3 siblings (youngest=100%), 4 siblings (2nd youngest=50%, youngest=100%), 5+ siblings (2nd youngest=100%, youngest=100%)';


-- =====================================================
-- Function: get_waiver_reason_text
-- Description: Generate human-readable waiver reason text
-- Parameters:
--   p_total_siblings: Total number of siblings
--   p_birth_order: Birth order of the student
--   p_waiver_percentage: Calculated waiver percentage
-- Returns: Text description of the waiver
-- =====================================================

DROP FUNCTION IF EXISTS get_waiver_reason_text(INTEGER, INTEGER, DECIMAL);

CREATE OR REPLACE FUNCTION get_waiver_reason_text(
    p_total_siblings INTEGER,
    p_birth_order INTEGER,
    p_waiver_percentage DECIMAL
) RETURNS TEXT AS $$
DECLARE
    v_position_text TEXT;
    v_reason TEXT;
BEGIN
    IF p_waiver_percentage = 0 THEN
        RETURN NULL;
    END IF;
    
    -- Determine position text
    IF p_birth_order = p_total_siblings THEN
        v_position_text := 'youngest';
    ELSIF p_birth_order = p_total_siblings - 1 THEN
        v_position_text := '2nd youngest';
    ELSE
        v_position_text := 'sibling ' || p_birth_order::TEXT;
    END IF;
    
    -- Build reason text
    v_reason := 'Sibling discount - ' || v_position_text || ' of ' || p_total_siblings::TEXT || ' siblings (' || p_waiver_percentage::TEXT || '% waiver)';
    
    RETURN v_reason;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Add comment
COMMENT ON FUNCTION get_waiver_reason_text(INTEGER, INTEGER, DECIMAL) IS 
'Generate human-readable text describing the sibling fee waiver reason';

