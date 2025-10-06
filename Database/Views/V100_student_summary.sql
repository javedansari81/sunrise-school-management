-- =====================================================
-- View: student_summary
-- Description: Student information summary with metadata relationships
-- Dependencies: students, classes, session_years, genders
-- =====================================================

-- Drop existing view
DROP VIEW IF EXISTS student_summary CASCADE;

-- Create view
CREATE OR REPLACE VIEW student_summary AS
SELECT
    s.id,
    s.admission_number,
    s.first_name || ' ' || s.last_name AS full_name,
    c.name AS class_name,
    s.section,
    sy.name AS session_year,
    g.name AS gender,
    s.father_name,
    s.father_phone,
    s.mother_name,
    s.mother_phone,
    s.is_active,
    EXTRACT(YEAR FROM AGE(s.date_of_birth)) AS age
FROM students s
LEFT JOIN classes c ON s.class_id = c.id
LEFT JOIN session_years sy ON s.session_year_id = sy.id
LEFT JOIN genders g ON s.gender_id = g.id
WHERE s.is_deleted = FALSE OR s.is_deleted IS NULL;

-- Add comment
COMMENT ON VIEW student_summary IS 'Student information summary with metadata relationships';

