-- =====================================================
-- Schema bookkeeping for the School Management System
-- =====================================================
-- The schema itself (default name: school) is created by the deployment
-- runner, which also sets search_path to it before running any script:
--   * redeploy_database.py   (reads DB_SCHEMA from sunrise-backend-fastapi/.env)
--   * psql -v schema=school -f Database/deploy_database.sql
--
-- Every script in Database/ uses unqualified names, so all objects land in
-- that schema. No script changes the database-wide search_path: the database
-- (warsi_db) is shared with other applications.
--
-- schema_migrations records what has been applied to this schema:
--   BASELINE              the full deployment from deploy_database.sql
--   INCLUDED_IN_BASELINE  a Versioning/ migration whose change the baseline already
--                         contains (recorded by redeploy_database.py, never run)
--   MIGRATION             a Versioning/ migration applied by migrate_database.py
-- migrate_database.py skips every version already recorded here, and refuses to
-- continue if an applied file was edited afterwards (checksum mismatch).
-- =====================================================

CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    filename VARCHAR(255),
    description TEXT,
    checksum CHAR(64),
    kind VARCHAR(25) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_by VARCHAR(100) DEFAULT current_user,
    execution_ms INTEGER,

    CONSTRAINT schema_migrations_version_unique UNIQUE (version),
    CONSTRAINT schema_migrations_kind_valid CHECK (kind IN ('BASELINE', 'INCLUDED_IN_BASELINE', 'MIGRATION'))
);

COMMENT ON TABLE schema_migrations IS 'Baseline and migrations applied to this schema. Maintained by redeploy_database.py and migrate_database.py';
COMMENT ON COLUMN schema_migrations.checksum IS 'SHA-256 of the migration file when it was applied';

INSERT INTO schema_migrations (version, description, kind)
VALUES ('3.0', 'Multi-tenant baseline: all legacy migrations folded into the table scripts', 'BASELINE');
