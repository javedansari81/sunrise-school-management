-- =====================================================
-- Default school: Sunrise (school 1)
-- =====================================================
-- Creates the first school and opens the seed window for it:
-- school-owned rows inserted by the scripts that follow (classes, session
-- years, departments, inventory lists, admin users, ...) belong to school 1.
--
-- The window is closed by Init/99_finish_default_school.sql, which removes
-- the temporary DEFAULT again. After deployment, school_id has no default:
-- the application always sets it, and a missing school_id is an error.
-- =====================================================

INSERT INTO schools (id, code, name, short_name)
VALUES (1, 'sunrise', 'Sunrise School', 'Sunrise');

DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN
        SELECT c.table_name
        FROM information_schema.columns c
        JOIN information_schema.tables tb
          ON tb.table_schema = c.table_schema AND tb.table_name = c.table_name AND tb.table_type = 'BASE TABLE'
        WHERE c.table_schema = current_schema() AND c.column_name = 'school_id'
    LOOP
        EXECUTE format('ALTER TABLE %I ALTER COLUMN school_id SET DEFAULT 1', t);
    END LOOP;
END $$;
