-- =====================================================
-- Function: enable_tenant_row_level_security
-- Description: Row-level security on every school-owned table (Phase 7, decision 12)
-- =====================================================
-- Every table in the current schema with a school_id column gets the policy
-- tenant_isolation. A row is visible, and may be written, only when
--
--   * its school_id equals the setting app.school_id, or
--   * the setting app.bypass_rls is 'on' (platform work, migrations, deployment).
--
-- Without either setting a school-owned table shows no rows and accepts no writes.
-- The backend sets both settings per transaction from its session
-- (app/core/tenant.py). Platform admins (users.school_id IS NULL) are only
-- visible with the bypass.
--
-- FORCE is needed because the application connects as the owner of the tables,
-- and owners skip row-level security otherwise. A superuser or a role with
-- BYPASSRLS skips it always, so the application must not connect as one.
--
-- Safe to run again: it replaces the policy on every table. A migration that
-- adds a school-owned table ends with:  SELECT enable_tenant_row_level_security();
-- Returns the number of tables covered.
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
