-- =====================================================
-- View: teacher_summary
-- Description: Teacher information summary with metadata relationships
-- Dependencies: teachers, classes, employment_statuses, qualifications, genders
-- =====================================================

-- Drop existing view
DROP VIEW IF EXISTS teacher_summary CASCADE;

-- Create view
CREATE OR REPLACE VIEW teacher_summary AS
SELECT
    t.id,
    t.employee_id,
    t.first_name || ' ' || t.last_name AS full_name,
    t.position,
    t.department,
    c.name AS class_teacher_of,
    es.name AS employment_status,
    q.name AS qualification,
    g.name AS gender,
    t.experience_years,
    t.is_active,
    EXTRACT(YEAR FROM AGE(t.date_of_birth)) AS age
FROM teachers t
LEFT JOIN classes c ON t.class_teacher_of_id = c.id
LEFT JOIN employment_statuses es ON t.employment_status_id = es.id
LEFT JOIN qualifications q ON t.qualification_id = q.id
LEFT JOIN genders g ON t.gender_id = g.id
WHERE t.is_deleted = FALSE OR t.is_deleted IS NULL;

-- Add comment
COMMENT ON VIEW teacher_summary IS 'Teacher information summary with metadata relationships';

