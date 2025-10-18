-- =====================================================
-- Data Load: DL400_fee_structures_data.sql
-- Description: Populate fee_structures table with metadata for all classes
-- Dependencies: classes, session_years tables must be populated
-- Date: 2025-10-10
-- =====================================================
-- This script populates the fee_structures table with detailed fee components
-- for all classes (PRE_NURSERY through CLASS_12) for session years 2025-26 and 2026-27
--
-- Fee Structure:
-- - Only tuition_fee is set (monthly amount)
-- - All other fee components are set to 0
-- - total_annual_fee = tuition_fee * 12 months
--
-- USAGE:
-- psql -U sunrise_user -d sunrise_school_db -f Database/DataLoads/DL400_fee_structures_data.sql

-- Set search path
SET search_path TO sunrise, public;

-- Start transaction
BEGIN;

-- =====================================================
-- Fee Structures for Session Year 2025-26
-- =====================================================

-- PRE_NURSERY (Monthly: 640, Annual: 7680)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee, 
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'PRE_NURSERY' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    640.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 7680.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- LKG (Monthly: 680, Annual: 8160)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee, 
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'LKG' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    680.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 8160.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- UKG (Monthly: 720, Annual: 8640)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee, 
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'UKG' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    720.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 8640.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_1 (Monthly: 800, Annual: 9600)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee, 
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_1' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    800.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 9600.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_2 (Monthly: 840, Annual: 10080)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee, 
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_2' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    840.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 10080.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_3 (Monthly: 880, Annual: 10560)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee, 
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_3' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    880.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 10560.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_4 (Monthly: 920, Annual: 11040)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_4' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    920.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 11040.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_5 (Monthly: 960, Annual: 11520)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_5' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    960.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 11520.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_6 (Monthly: 1000, Annual: 12000)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_6' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    1000.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 12000.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_7 (Monthly: 1040, Annual: 12480)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_7' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    1040.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 12480.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_8 (Monthly: 1080, Annual: 12960)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_8' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    1080.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 12960.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- =====================================================
-- Fee Structures for Session Year 2026-27
-- =====================================================
-- NURSERY (Monthly: 640, Annual: 7680)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'PRE_NURSERY' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2026-27' LIMIT 1),
    640.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 7680.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- LKG (Monthly: 680, Annual: 8160)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'LKG' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2026-27' LIMIT 1),
    680.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 8160.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- UKG (Monthly: 720, Annual: 8640)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'UKG' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2026-27' LIMIT 1),
    720.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 8640.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_1 (Monthly: 800, Annual: 9600)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_1' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2026-27' LIMIT 1),
    800.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 9600.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_2 (Monthly: 840, Annual: 10080)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_2' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2026-27' LIMIT 1),
    840.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 10080.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_3 (Monthly: 880, Annual: 10560)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_3' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2026-27' LIMIT 1),
    880.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 10560.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_4 (Monthly: 920, Annual: 11040)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_4' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2026-27' LIMIT 1),
    920.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 11040.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_5 (Monthly: 960, Annual: 11520)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_5' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2026-27' LIMIT 1),
    960.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 11520.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_6 (Monthly: 1000, Annual: 12000)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_6' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2026-27' LIMIT 1),
    1000.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 12000.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_7 (Monthly: 1040, Annual: 12480)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_7' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2026-27' LIMIT 1),
    1040.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 12480.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();

-- CLASS_8 (Monthly: 1080, Annual: 12960)
INSERT INTO fee_structures (
    class_id, session_year_id, tuition_fee, admission_fee, development_fee,
    activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee
) VALUES (
    (SELECT id FROM classes WHERE name = 'CLASS_8' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2026-27' LIMIT 1),
    1080.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 12960.00
) ON CONFLICT (class_id, session_year_id) DO UPDATE SET
    tuition_fee = EXCLUDED.tuition_fee, total_annual_fee = EXCLUDED.total_annual_fee, updated_at = NOW();
-- =====================================================
-- Commit transaction and display summary
-- =====================================================

COMMIT;

-- Display summary of inserted records
SELECT
    'Fee structures populated successfully!' as message,
    COUNT(*) as total_records,
    COUNT(DISTINCT class_id) as total_classes,
    COUNT(DISTINCT session_year_id) as total_session_years
FROM fee_structures;

-- Display fee structures by session year
SELECT
    sy.name as session_year,
    c.name as class_name,
    c.description as class_description,
    fs.tuition_fee as monthly_fee,
    fs.total_annual_fee as annual_fee
FROM fee_structures fs
JOIN classes c ON fs.class_id = c.id
JOIN session_years sy ON fs.session_year_id = sy.id
ORDER BY sy.name, c.sort_order, c.name;
