-- =====================================================
-- Transport operations module: default transport types, rates and settings
-- =====================================================
-- Runs for every school, so the same script serves a fresh deployment
-- (school 1) and migration V003 (every existing school). Each step skips a
-- school that already has the rows. New schools created later get theirs from
-- app/modules/transport/provisioning.py.
--
-- 1. Transport types E-Rickshaw, Van and Bus for every school without types.
-- 2. Rates carried over from the pre-redesign price list
--    (transport_type_pricing and transport_distance_slabs, which only Sunrise
--    has) for schools without rates. Price lists are configuration, not student
--    data, so they are kept (decision 1 drops only old enrollments and
--    payments). Old slabs ran 0-8, 8.01-10, ...; new slabs cover
--    (from, to], so 8.01 becomes 8.00.
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

CREATE TEMP TABLE _legacy_transport_type_map AS
SELECT lt.id AS legacy_id,
       CASE lt.name
           WHEN 'E_RICKSHAW' THEN 'E-Rickshaw'
           WHEN 'VAN' THEN 'Van'
           WHEN 'BUS' THEN 'Bus'
           ELSE initcap(replace(lt.name, '_', ' '))
       END AS name
FROM legacy_transport_types lt;

INSERT INTO transport_rates (school_id, session_year_id, basis, transport_type_id, monthly_amount, description)
SELECT sy.school_id, p.session_year_id, 'FLAT', t.id, p.base_monthly_fee, 'Carried over from the old price list'
FROM transport_type_pricing p
JOIN session_years sy ON sy.id = p.session_year_id
JOIN _legacy_transport_type_map m ON m.legacy_id = p.transport_type_id
JOIN transport_types t ON t.school_id = sy.school_id AND t.name = m.name
WHERE p.is_active
  AND NOT EXISTS (SELECT 1 FROM transport_rates r WHERE r.school_id = sy.school_id AND r.basis = 'FLAT');

INSERT INTO transport_rates (school_id, session_year_id, basis, transport_type_id,
                             distance_from_km, distance_to_km, monthly_amount, description)
SELECT sy.school_id, p.session_year_id, 'DISTANCE_SLAB', t.id,
       CASE WHEN ds.distance_from_km = 0 THEN 0 ELSE ds.distance_from_km - 0.01 END,
       ds.distance_to_km, ds.monthly_fee, ds.description
FROM transport_distance_slabs ds
JOIN transport_type_pricing p ON p.transport_type_id = ds.transport_type_id AND p.is_active
JOIN session_years sy ON sy.id = p.session_year_id
JOIN _legacy_transport_type_map m ON m.legacy_id = ds.transport_type_id
JOIN transport_types t ON t.school_id = sy.school_id AND t.name = m.name
WHERE ds.is_active
  AND NOT EXISTS (SELECT 1 FROM transport_rates r WHERE r.school_id = sy.school_id AND r.basis = 'DISTANCE_SLAB');

DROP TABLE _legacy_transport_type_map;

INSERT INTO school_settings (school_id, key, value, description)
SELECT id, 'fee.transport.due_day', '10', 'Day of the month transport dues fall due (1-28)'
FROM schools
ON CONFLICT (school_id, key) DO NOTHING;
