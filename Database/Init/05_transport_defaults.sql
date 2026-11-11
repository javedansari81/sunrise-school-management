-- =====================================================
-- Transport operations module: default transport types, rates and settings
-- =====================================================
-- Fresh deployments only. Existing databases got the same rows from
-- migration V003. New schools created later get theirs from
-- app/modules/transport/provisioning.py.
--
-- 1. Transport types E-Rickshaw, Van and Bus for every school without types.
-- 2. Sunrise's price list (school 1), the same rates V003 carried over from
--    the pre-redesign tables: flat monthly fees per type for 2025-26 and
--    2026-27, and Van distance slabs covering (from, to] km.
-- 3. The fee.transport.due_day setting.
-- =====================================================

INSERT INTO transport_types (school_id, name, description, capacity, sort_order)
SELECT s.id, d.name, d.description, d.capacity, d.sort_order
FROM schools s
CROSS JOIN (VALUES
    ('E-Rickshaw', 'E-Rickshaw service', 6, 10),
    ('Van', 'Van service', 12, 20),
    ('Bus', 'Bus service', 40, 30)
) AS d (name, description, capacity, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM transport_types t WHERE t.school_id = s.id);

INSERT INTO transport_rates (school_id, session_year_id, basis, transport_type_id, monthly_amount, description)
SELECT sy.school_id, sy.id, 'FLAT', t.id, r.monthly_amount, 'Carried over from the old price list'
FROM (VALUES
    ('2025-26', 'E-Rickshaw', 450.00),
    ('2025-26', 'Van', 700.00),
    ('2026-27', 'E-Rickshaw', 500.00),
    ('2026-27', 'Van', 700.00)
) AS r (session_name, type_name, monthly_amount)
JOIN session_years sy ON sy.school_id = 1 AND sy.name = r.session_name
JOIN transport_types t ON t.school_id = 1 AND t.name = r.type_name
WHERE NOT EXISTS (SELECT 1 FROM transport_rates x WHERE x.school_id = 1 AND x.basis = 'FLAT');

INSERT INTO transport_rates (school_id, session_year_id, basis, transport_type_id,
                             distance_from_km, distance_to_km, monthly_amount, description)
SELECT sy.school_id, sy.id, 'DISTANCE_SLAB', t.id, s.distance_from_km, s.distance_to_km, s.monthly_amount, s.description
FROM (VALUES
    (0.00, 8.00, 700.00, 'Up to 8 KM'),
    (8.00, 10.00, 800.00, 'Up to 10 KM'),
    (10.00, 12.00, 900.00, 'Up to 12 KM'),
    (12.00, 999.99, 900.00, 'Above 12 KM')
) AS s (distance_from_km, distance_to_km, monthly_amount, description)
CROSS JOIN (VALUES ('2025-26'), ('2026-27')) AS sessions (session_name)
JOIN session_years sy ON sy.school_id = 1 AND sy.name = sessions.session_name
JOIN transport_types t ON t.school_id = 1 AND t.name = 'Van'
WHERE NOT EXISTS (SELECT 1 FROM transport_rates x WHERE x.school_id = 1 AND x.basis = 'DISTANCE_SLAB');

INSERT INTO school_settings (school_id, key, value, description)
SELECT id, 'fee.transport.due_day', '10', 'Day of the month transport dues fall due (1-28)'
FROM schools
ON CONFLICT (school_id, key) DO NOTHING;
