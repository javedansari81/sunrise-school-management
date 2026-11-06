# Database Deployment Flow

The application lives in one schema (`DB_SCHEMA`, default `school`) of a shared database (`warsi_db`, which also holds `mart`). It is deployed with `redeploy_database.py` at the repository root, which talks to PostgreSQL directly; the backend server does not need to be running. The old `POST /api/v1/database/deploy` endpoint has been removed: it dropped the whole schema without authentication.

## Redeploy

```bash
# From the repository root. Uses DATABASE_URL and DB_SCHEMA from sunrise-backend-fastapi/.env
python redeploy_database.py

# Explicit target, without the confirmation prompt
python redeploy_database.py --database-url postgresql://warsi_user:PASSWORD@localhost:5432/warsi_db --schema school --yes
```

The script asks you to type the schema name before it does anything. It refuses any host other than `localhost`, `127.0.0.1` or `::1` unless you pass `--allow-remote`, and it never accepts `public` as the schema.

## What it does

1. Reads the list of SQL files from `Database/deploy_database.sql` (its `\ir` lines, in order). psql uses the same list, so there is one source of truth.
2. Opens one transaction.
3. Drops and recreates only the `DB_SCHEMA` schema. Other schemas (`mart`, `public`) are not touched.
4. Sets `search_path` to that schema for this session only. The database-wide setting is never changed.
5. Runs every listed file in order, skipping psql-only lines and each file's own `BEGIN;` / `COMMIT;`.
6. Commits. If any file fails, it prints which one and rolls back, so the database is left exactly as it was.
7. Records every migration already in `Database/Versioning/` as included in the baseline, so `migrate_database.py` never runs them on this schema.
8. Prints table and row counts.

## Deployment order (`Database/deploy_database.sql`)

| Step | Contents |
| --- | --- |
| 1 | `Schema/00_create_schema.sql` (schema_migrations, baseline 3.0) |
| 2 | Tenants: `T010_schools`, `T020_school_settings` |
| 3 to 8 | Every other `Tables/T*.sql` in number order |
| 9 | Every `Functions/F*.sql` |
| 10 | Default school: `Init/00` creates Sunrise (school 1), then reference data (`Init/01`, `DataLoads/*`), admin users, fee structures and initial stock rows, then `Init/99` closes the seed |

A fresh deployment produces the same tables, columns, constraints, indexes and seed data as the legacy database after all of its migrations. The differences are intended: `school_id` has no default, and unused objects are gone (the `pgcrypto` extension, the five reporting views, and the `calculate_age` and `get_academic_year` functions).

## First deployment to DigitalOcean

1. Back up `warsi_db` on DigitalOcean.
2. Run with the DigitalOcean URL (keep `?sslmode=require`):
   ```bash
   python redeploy_database.py --database-url "postgresql://warsi_user:PASSWORD@HOST:25060/warsi_db?sslmode=require" --schema school --allow-remote
   ```
3. Set `DATABASE_URL` and `DB_SCHEMA=school` on the backend's hosting environment.
4. Log in with the seeded admin and change its password.

Later schema changes to a database with data are made with migrations in `Database/Versioning/`, applied with `python migrate_database.py`, never by redeploying. Each migration runs once; `schema_migrations` records it.

## Keeping it complete

- New table, function, view or data script: add an `\ir` line for it in `deploy_database.sql`.
- Change to an existing table: edit its `Tables/` script AND add a migration to `Database/Versioning/`.
