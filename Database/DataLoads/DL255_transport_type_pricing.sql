-- =====================================================
-- Data Load: transport_type_pricing
-- Description: Session-based pricing for transport types
-- Dependencies: T255_transport_type_pricing.sql, DL251_transport_types.sql
-- =====================================================

-- Insert pricing for recent sessions
-- E-Rickshaw pricing: 450 for 2025-26, 500 for 2026-27 (current session)
-- Van pricing: 700 for both sessions (unchanged)

INSERT INTO transport_type_pricing (transport_type_id, session_year_id, base_monthly_fee, is_active) VALUES
-- Session 2025-26 (session_year_id = 4) - Previous Session
(1, 4, 450.00, TRUE),  -- E-Rickshaw
(2, 4, 700.00, TRUE),  -- Van

-- Session 2026-27 (session_year_id = 5) - Current Session ⭐
(1, 5, 500.00, TRUE),  -- E-Rickshaw (INCREASED from 450 to 500)
(2, 5, 700.00, TRUE)   -- Van (unchanged)

ON CONFLICT (transport_type_id, session_year_id) DO UPDATE SET
    base_monthly_fee = EXCLUDED.base_monthly_fee,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Verify insertion
DO $$
DECLARE
    record_count INTEGER;
    e_rickshaw_2025_price DECIMAL(10,2);
    e_rickshaw_2026_price DECIMAL(10,2);
BEGIN
    SELECT COUNT(*) INTO record_count FROM transport_type_pricing;
    RAISE NOTICE 'Transport Type Pricing loaded: % records', record_count;

    -- Verify pricing
    SELECT base_monthly_fee INTO e_rickshaw_2025_price
    FROM transport_type_pricing
    WHERE transport_type_id = 1 AND session_year_id = 4;

    SELECT base_monthly_fee INTO e_rickshaw_2026_price
    FROM transport_type_pricing
    WHERE transport_type_id = 1 AND session_year_id = 5;

    -- Show pricing summary
    RAISE NOTICE '=== Pricing Summary ===';
    RAISE NOTICE 'E-Rickshaw 2025-26 (Previous): ₹%', e_rickshaw_2025_price;
    RAISE NOTICE 'E-Rickshaw 2026-27 (Current):  ₹% ⭐', e_rickshaw_2026_price;
    RAISE NOTICE 'Van (both sessions): ₹700.00';
    RAISE NOTICE '';

    IF e_rickshaw_2025_price = 450.00 AND e_rickshaw_2026_price = 500.00 THEN
        RAISE NOTICE '✓ Pricing configured correctly!';
    ELSE
        RAISE WARNING '⚠ Pricing mismatch detected!';
    END IF;
END $$;

