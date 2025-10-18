-- =====================================================
-- Data Load: transport_types
-- Description: Initial data for transport types
-- Dependencies: T250_transport_types.sql
-- =====================================================

-- Insert transport types
INSERT INTO transport_types (id, name, description, base_monthly_fee, capacity, is_active) VALUES
(1, 'E_RICKSHAW', 'E-Rickshaw Service', 450.00, 6, TRUE),
(2, 'VAN', 'Van Service', 700.00, 12, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    base_monthly_fee = EXCLUDED.base_monthly_fee,
    capacity = EXCLUDED.capacity,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Verify insertion
DO $$
DECLARE
    record_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO record_count FROM transport_types;
    RAISE NOTICE 'Transport Types loaded: % records', record_count;
END $$;

