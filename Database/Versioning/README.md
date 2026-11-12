# Migrations

Migrations change an existing database that already has data. Each one runs once. `migrate_database.py` records every migration it applies in `school.schema_migrations`, with a checksum of the file, and skips it on every later run.

A fresh deployment (`redeploy_database.py`) does not run migrations. It builds the latest schema straight from `Tables/`, `Functions/` and `Init/`, and records every file in this folder as `INCLUDED_IN_BASELINE`, so they never run on that schema either.

The current baseline is 3.0, the multi-tenant baseline. The legacy migrations V001 to V036 are already folded into it and kept in `../archive/Versioning_legacy/` for history.

## Run migrations

```bash
# From the repository root. DATABASE_URL and DB_SCHEMA come from sunrise-backend-fastapi/.env
python migrate_database.py --status   # what is applied, what is pending; changes nothing
python migrate_database.py            # apply pending migrations (asks first)
python migrate_database.py --yes      # apply without asking
python migrate_database.py --database-url "<DigitalOcean URL>" --allow-remote   # production
```

- Migrations run in version order, each in its own transaction. If one fails, it is rolled back, it is not recorded, and the run stops before later migrations.
- If an applied migration file is changed afterwards, the runner stops with `EDITED`. Never edit an applied migration. Restore it and put the fix in a new one.
- Two runs at the same time cannot overlap: the runner takes a database lock.

## Write a migration

1. Name it `V001_short_description.sql`, then `V002_...` and so on. The runner rejects other names.
2. Use unqualified names. The runner sets `search_path` to the schema. Never name the schema, and never use `ALTER DATABASE ... SET search_path`, because the database is shared.
3. Do not add `BEGIN;` or `COMMIT;`. The runner wraps each migration in a transaction.
4. Make the same change in the matching `Tables/` script (or `Init/`, `Functions/`), so fresh deployments get it too. `redeploy_database.py` relies on this when it records the migration as already included.
5. School-owned tables need `school_id INTEGER NOT NULL REFERENCES schools(id)` and an index on it. Unique keys on them include `school_id`. End the migration with `SELECT enable_tenant_row_level_security();` so the new table gets row-level security (`tests/tenant/test_row_level_security.py` fails otherwise).
6. The runner works across schools (`app.bypass_rls = on`), so a migration sees and writes every school's rows.

Example, `V001_add_school_motto.sql`:

```sql
ALTER TABLE schools ADD COLUMN IF NOT EXISTS motto TEXT;
COMMENT ON COLUMN schools.motto IS 'Shown on receipts and the website';
```

The same column is also added to `Tables/T010_schools.sql`.
