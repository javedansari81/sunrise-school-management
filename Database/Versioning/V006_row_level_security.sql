-- =====================================================
-- V006: Row-level security on school_id (Phase 7, decision 12)
-- =====================================================
-- Last layer of school isolation. Every table with a school_id column only
-- shows and accepts rows of the school in the setting app.school_id, or every
-- row when app.bypass_rls is 'on'. The backend sets both per transaction
-- (app/core/tenant.py); migrate_database.py and redeploy_database.py set the
-- bypass for their own connection.
--
-- After this migration, a direct psql session sees no school-owned rows until it runs:
--   SET app.bypass_rls = on;            -- every school
--   SET app.school_id = 1;              -- or one school
--
-- Same function as Functions/F900_tenant_row_level_security.sql, called as in
-- Schema/90_enable_row_level_security.sql.
-- =====================================================

DROP FUNCTION IF EXISTS enable_tenant_row_level_security();

CREATE FUNCTION enable_tenant_row_level_security() RETURNS INTEGER
LANGUAGE plpgsql AS $$
DECLARE
    t RECORD;
    covered INTEGER := 0;
BEGIN
    FOR t IN
        SELECT c.relname
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_attribute a ON a.attrelid = c.oid AND a.attname = 'school_id' AND NOT a.attisdropped
        WHERE n.nspname = current_schema() AND c.relkind IN ('r', 'p')
        ORDER BY c.relname
    LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t.relname);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', t.relname);
        EXECUTE format('DROP POLICY IF EXISTS tenant_isolation ON %I', t.relname);
        EXECUTE format(
            'CREATE POLICY tenant_isolation ON %I '
            'USING (current_setting(''app.bypass_rls'', true) = ''on'' '
            '       OR school_id = NULLIF(current_setting(''app.school_id'', true), '''')::integer) '
            'WITH CHECK (current_setting(''app.bypass_rls'', true) = ''on'' '
            '       OR school_id = NULLIF(current_setting(''app.school_id'', true), '''')::integer)',
            t.relname
        );
        covered := covered + 1;
    END LOOP;
    RETURN covered;
END;
$$;

COMMENT ON FUNCTION enable_tenant_row_level_security() IS
    'Enables and forces row-level security (policy tenant_isolation) on every table with school_id';

SELECT enable_tenant_row_level_security();
