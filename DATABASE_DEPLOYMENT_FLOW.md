# Database Deployment Flow

A local database is redeployed with `redeploy_database.py` at the repository root. It talks to PostgreSQL directly; the backend server does not need to be running. The old `POST /api/v1/database/deploy` endpoint has been removed: it dropped the whole schema without authentication, which is unsafe once several schools share one database.

## Redeploy a local database

```bash
# From the repository root. Uses DATABASE_URL from sunrise-backend-fastapi/.env
python redeploy_database.py

# Another local database, without the confirmation prompt
python redeploy_database.py --database-url postgresql://user:pass@localhost:5432/sunrise_school_db --yes
```

The script asks you to type the database name before it does anything. It refuses any host other than `localhost`, `127.0.0.1` or `::1` unless you pass `--allow-remote`.

## What it does

1. Reads the list of SQL files from `Database/deploy_database.sql` (its `\ir` lines, in order). This is the same list `psql -f Database/deploy_database.sql` uses, so there is one source of truth.
2. Opens one transaction.
3. Drops the `sunrise` schema.
4. Runs every listed file in order, skipping psql-only lines (`\echo`, `\ir`) and each file's own `BEGIN;` / `COMMIT;`.
5. Commits. If any file fails, it prints which one and rolls back, so the database is left exactly as it was.
6. Prints table and row counts.

## Deployment order (`Database/deploy_database.sql`)

| Step | Contents |
| --- | --- |
| 1 | `Schema/00_create_schema.sql` |
| 2 to 7 | Every `Tables/T*.sql` in number order: lookups (T100 to T297), core (T300 to T320), fee and transport (T400 to T470), expense and leave (T500 to T600), gallery and inventory (T700 to T750), attendance and alerts (T800 to T810) |
| 8 | Every `Functions/F*.sql` |
| 9 | Every `Views/V*.sql` |
| 10 | `Init/01_load_metadata.sql` and every `DataLoads/*.sql` |
| 11 | Admin users and initial data (`Init/02`, `Init/03`, `Init/07`) |
| 12 | Migrations not yet folded into the table scripts (V033, V034) |
| 13 | `Versioning/V036_add_schools_and_tenant_columns.sql` (multi-tenancy) |

A fresh deployment produces the same tables, columns, functions and views as a database that was migrated step by step.

## Keeping it complete

- New table, function, view or data script: add an `\ir` line for it in `deploy_database.sql`.
- New migration in `Database/Versioning/`: apply it to existing databases as usual. If the `Tables/` scripts do not already include the change, also add the migration to step 12 so fresh deployments match.

## Admin login after a fresh deployment

See `Database/Init/02_create_admin_user.sql` for the credentials.
