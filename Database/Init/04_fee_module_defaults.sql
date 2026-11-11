-- =====================================================
-- Unified fee module: default fee heads, sibling rule and settings
-- =====================================================
-- Runs for every school that has no fee heads yet, so the same script serves a
-- fresh deployment (school 1) and migration V002 (every existing school).
-- New schools created later get theirs from app/modules/fees/provisioning.py.
--
-- Fee heads mirror the columns of the pre-redesign fee structure. TRANSPORT and
-- LATE_FEE are system heads used by the transport handoff and late fee job.
--
-- Sibling rule: Sunrise's existing rule (calculate_sibling_fee_waiver), tuition
-- only. Siblings are ordered eldest first by date of birth; positions below are
-- counted from the youngest.
--   3 siblings: youngest 100%
--   4 siblings: 2nd youngest 50%, youngest 100%
--   5 or more:  2 youngest 100%
--
-- Receipt branding comes from the schools row and school_settings (no longer
-- hard-coded). Sunrise's details, as printed on its receipts until now, are
-- filled in where still empty, and its black-and-white logo is set.
-- =====================================================

UPDATE schools SET
    name = 'Sunrise National Public School',
    address = 'Sena road, Farsauliyana, Rath, Hamirpur, UP - 210431',
    email = 'sunrise.nps008@gmail.com',
    website = 'https://sunrisenps.com'
WHERE code = 'sunrise' AND name = 'Sunrise School' AND address IS NULL;

INSERT INTO school_settings (school_id, key, value, description)
SELECT id, 'receipt.logo', 'static:images/school_logo_bw.jpeg',
       'Logo on receipts: static:<path under app/static> or an https URL'
FROM schools WHERE code = 'sunrise'
ON CONFLICT (school_id, key) DO NOTHING;

DO $$
DECLARE
    s RECORD;
    tuition_id INTEGER;
BEGIN
    FOR s IN
        SELECT sc.id, sc.code FROM schools sc
        WHERE NOT EXISTS (SELECT 1 FROM fee_heads h WHERE h.school_id = sc.id)
        ORDER BY sc.id
    LOOP
        INSERT INTO fee_heads (school_id, code, name, category, default_frequency, is_system, sort_order) VALUES
            (s.id, 'TUITION',     'Tuition Fee',     'ACADEMIC',  'MONTHLY',  FALSE, 10),
            (s.id, 'ADMISSION',   'Admission Fee',   'ONE_TIME',  'ONE_TIME', FALSE, 20),
            (s.id, 'DEVELOPMENT', 'Development Fee', 'ACADEMIC',  'ANNUAL',   FALSE, 30),
            (s.id, 'ACTIVITY',    'Activity Fee',    'ACADEMIC',  'ANNUAL',   FALSE, 40),
            (s.id, 'LIBRARY',     'Library Fee',     'ACADEMIC',  'ANNUAL',   FALSE, 50),
            (s.id, 'LAB',         'Lab Fee',         'ACADEMIC',  'ANNUAL',   FALSE, 60),
            (s.id, 'EXAM',        'Exam Fee',        'ACADEMIC',  'ANNUAL',   FALSE, 70),
            (s.id, 'TRANSPORT',   'Transport Fee',   'TRANSPORT', 'MONTHLY',  TRUE,  80),
            (s.id, 'LATE_FEE',    'Late Fee',        'PENALTY',   'ONE_TIME', TRUE,  90),
            (s.id, 'OTHER',       'Other Charges',   'OTHER',     'ONE_TIME', FALSE, 100);

        SELECT id INTO tuition_id FROM fee_heads WHERE school_id = s.id AND code = 'TUITION';

        INSERT INTO concession_rules (school_id, name, description, concession_type, value_type, value, fee_head_ids, tiers)
        VALUES (
            s.id, 'Sibling concession',
            'Younger siblings in large families. Siblings ordered eldest first by date of birth.',
            'SIBLING', 'PERCENT', 0, ARRAY[tuition_id],
            '[
              {"min_siblings": 3, "max_siblings": 3,    "position_basis": "YOUNGEST", "position_from": 1, "position_to": 1, "percent": 100},
              {"min_siblings": 4, "max_siblings": 4,    "position_basis": "YOUNGEST", "position_from": 1, "position_to": 1, "percent": 100},
              {"min_siblings": 4, "max_siblings": 4,    "position_basis": "YOUNGEST", "position_from": 2, "position_to": 2, "percent": 50},
              {"min_siblings": 5, "max_siblings": null, "position_basis": "YOUNGEST", "position_from": 1, "position_to": 2, "percent": 100}
            ]'::jsonb
        );

        INSERT INTO school_settings (school_id, key, value, description) VALUES
            (s.id, 'fee.receipt_prefix', UPPER(LEFT(s.code, 3)), 'Receipt number prefix, e.g. SUN in SUN/2026-27/000123'),
            (s.id, 'fee.late_fee.enabled', 'false', 'Add a Late fee due automatically after the grace days'),
            (s.id, 'fee.late_fee.mode', 'FIXED', 'FIXED amount or PERCENT of the overdue amount'),
            (s.id, 'fee.late_fee.value', '0', 'Late fee amount or percent per overdue month'),
            (s.id, 'fee.late_fee.grace_days', '7', 'Days after the due date before a late fee is added'),
            (s.id, 'fee.transport.cutoff_day', '15', 'Transport started after this day of the month is billed from the next month')
        ON CONFLICT (school_id, key) DO NOTHING;
    END LOOP;
END $$;
