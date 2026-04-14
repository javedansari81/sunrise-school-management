-- =====================================================
-- Migration: V035_add_transport_type_pricing_table
-- Description: Add session-based pricing for transport types
--              Enables different pricing per academic session
--              (E.g., E-Rickshaw 450 in 2025-26, 500 in 2026-27)
-- =====================================================

-- Create transport_type_pricing table
CREATE TABLE IF NOT EXISTS transport_type_pricing (
    id SERIAL PRIMARY KEY,
    transport_type_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    base_monthly_fee DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Foreign Key Constraints
    FOREIGN KEY (transport_type_id) REFERENCES transport_types(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    
    -- Unique constraint: one pricing per transport type per session
    UNIQUE (transport_type_id, session_year_id)
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_transport_type_pricing_type ON transport_type_pricing(transport_type_id);
CREATE INDEX IF NOT EXISTS idx_transport_type_pricing_session ON transport_type_pricing(session_year_id);
CREATE INDEX IF NOT EXISTS idx_transport_type_pricing_active ON transport_type_pricing(is_active);

-- Add comments
COMMENT ON TABLE transport_type_pricing IS 'Session-based pricing for transport types (enables different rates per academic year)';
COMMENT ON COLUMN transport_type_pricing.transport_type_id IS 'Foreign key to transport_types table';
COMMENT ON COLUMN transport_type_pricing.session_year_id IS 'Foreign key to session_years table';
COMMENT ON COLUMN transport_type_pricing.base_monthly_fee IS 'Base monthly fee for this transport type in this session';

-- Migrate existing pricing data from transport_types to transport_type_pricing
-- For existing installations, add pricing for the two current sessions: 2025-26 and 2026-27
INSERT INTO transport_type_pricing (transport_type_id, session_year_id, base_monthly_fee, is_active)
VALUES
-- Session 2025-26 (session_year_id = 4) - Previous Session
(1, 4, 450.00, TRUE),  -- E-Rickshaw
(2, 4, 700.00, TRUE),  -- Van
-- Session 2026-27 (session_year_id = 5) - Current Session
(1, 5, 500.00, TRUE),  -- E-Rickshaw (NEW PRICE)
(2, 5, 700.00, TRUE)   -- Van
ON CONFLICT (transport_type_id, session_year_id) DO UPDATE SET
    base_monthly_fee = EXCLUDED.base_monthly_fee,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Verification
DO $$
DECLARE
    record_count INTEGER;
    e_rickshaw_2025_price DECIMAL(10,2);
    e_rickshaw_2026_price DECIMAL(10,2);
BEGIN
    SELECT COUNT(*) INTO record_count FROM transport_type_pricing;
    RAISE NOTICE 'Transport Type Pricing records: %', record_count;

    -- Verify E-Rickshaw pricing for both sessions
    SELECT base_monthly_fee INTO e_rickshaw_2025_price
    FROM transport_type_pricing
    WHERE transport_type_id = 1 AND session_year_id = 4;

    SELECT base_monthly_fee INTO e_rickshaw_2026_price
    FROM transport_type_pricing
    WHERE transport_type_id = 1 AND session_year_id = 5;

    RAISE NOTICE '';
    RAISE NOTICE '=== Verification Results ===';
    RAISE NOTICE 'E-Rickshaw 2025-26: ₹%', e_rickshaw_2025_price;
    RAISE NOTICE 'E-Rickshaw 2026-27: ₹%', e_rickshaw_2026_price;
    RAISE NOTICE '';

    IF e_rickshaw_2025_price = 450.00 AND e_rickshaw_2026_price = 500.00 THEN
        RAISE NOTICE '✓ Migration successful!';
        RAISE NOTICE '  - 2025-26 (Previous): ₹450';
        RAISE NOTICE '  - 2026-27 (Current):  ₹500 ⭐';
    ELSE
        RAISE WARNING '⚠ Pricing mismatch. Please verify manually.';
    END IF;
END $$;

