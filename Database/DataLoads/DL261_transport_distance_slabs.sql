-- =====================================================
-- Data Load: transport_distance_slabs
-- Description: Distance-based pricing slabs for Van transport
-- Dependencies: T260_transport_distance_slabs.sql, DL250_transport_types.sql
-- =====================================================

-- Clear existing data
TRUNCATE TABLE transport_distance_slabs RESTART IDENTITY CASCADE;

-- Insert distance slabs for Van (transport_type_id = 2)
-- E-Rickshaw has fixed pricing (450), so no slabs needed
INSERT INTO transport_distance_slabs (transport_type_id, distance_from_km, distance_to_km, monthly_fee, description, is_active) VALUES
(2, 0.00, 8.00, 700.00, 'Up to 8 KM', TRUE),
(2, 8.01, 10.00, 800.00, 'Up to 10 KM', TRUE),
(2, 10.01, 12.00, 900.00, 'Up to 12 KM', TRUE),
(2, 12.01, 999.99, 900.00, 'Above 12 KM', TRUE);

-- Verify insertion
DO $$
DECLARE
    record_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO record_count FROM transport_distance_slabs;
    RAISE NOTICE 'Transport Distance Slabs loaded: % records', record_count;
END $$;

