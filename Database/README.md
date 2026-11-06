# School Management System: Database

The application lives in one PostgreSQL schema, `school` by default, inside a database that can be shared with other applications. Locally and on DigitalOcean that database is `warsi_db`, which also holds the `mart` schema. The scripts here only ever create, change or drop objects in the application's schema.

**Version:** 3.0, multi-tenant baseline (Nov 2026). Every legacy migration (V001 to V036) is folded into the table scripts.

## Deploy or redeploy

```bash
# From the repository root. Reads DATABASE_URL and DB_SCHEMA from sunrise-backend-fastapi/.env
python redeploy_database.py
```

- It drops and recreates only the `DB_SCHEMA` schema, then runs every script in one transaction. If a script fails, nothing changes.
- It asks you to type the schema name first (`--yes` skips the prompt).
- It refuses non-local databases unless you pass `--allow-remote`, for example for the first DigitalOcean deployment.
- It refuses `public`.

With psql instead:

```bash
psql "postgresql://warsi_user@localhost:5432/warsi_db" -v schema=school -f Database/deploy_database.sql
```

The database user needs permission to create a schema in the database. `warsi_user` owns `warsi_db`, so it has it.

## Rules every script follows

- **No manual schema setup.** `redeploy_database.py` creates the schema. The database user only needs permission to create a schema in the database (`warsi_user` owns `warsi_db`).
- **Unqualified names.** The runner sets `search_path` to the schema, and every object is created there. No script names a schema or database.
- **The database-wide `search_path` is never changed.** The app sets it per connection, because other applications share the database.
- **Every school-owned row has `school_id`.** It is `NOT NULL` with no default, and references `schools(id)`. The app's session layer stamps it on every insert.

## Folder structure

| Folder | Contents |
| --- | --- |
| `Schema/` | `00_create_schema.sql`: the `schema_migrations` table and the baseline row |
| `Tables/` | One file per table. `T010` `schools`, `T020` `school_settings`, then lookups (T100 to T297), core (T300 to T320), fee and transport (T400 to T470), expense and leave (T500 to T600), gallery and inventory (T700 to T750), attendance and alerts (T800 to T810) |
| `Functions/` | One file per function. All four are used by the legacy fee, sibling and transport code (F120 is the trigger that keeps `fee_records.balance_amount` current) |
| `Init/` | Default school seed: `00` creates Sunrise (school 1), `01` reference lists, `02`/`03` admin users, `03_fee_structures_data`, `07` initial stock rows, `99` closes the seed |
| `DataLoads/` | More reference data (alert types, reversal reasons, transport, inventory, attendance, gallery categories) |
| `Versioning/` | Migrations for existing databases, starting after the 3.0 baseline. Applied once each by `migrate_database.py`. See its README |
| `archive/` | Legacy migrations V001 to V036 and old scripts. Already included in the baseline. Kept for history only |
| `deploy_database.sql` | The single, ordered list of scripts. Used by `redeploy_database.py` and psql |

## Which tables are per school

| Kind | Tables | Rule |
| --- | --- | --- |
| School-owned data | users, students, teachers, attendance_records, leave_requests, expenses, vendors, inventory (pricing, purchases, stock, procurements and their items), gallery_images, alerts, student_siblings, student_session_history, school_settings | `school_id NOT NULL`. Admission numbers, employee IDs and emails are unique per school |
| School-configurable lists | classes, session_years, departments, positions, expense_categories, gallery_categories, inventory_item_category, inventory_item_types, inventory_size_types, leave_types | `school_id NOT NULL`, `name` unique per school, auto-increment ids |
| Shared system lists | user_types, genders, payment_types, payment_statuses, payment_methods, leave_statuses, expense_statuses, employment_statuses, qualifications, reversal_reasons, attendance_statuses, attendance_periods, progression_actions, alert_types, alert_statuses | No `school_id`. Same for every school |
| Legacy fee and transport | fee_structures, fee_records, fee_payments, monthly_fee_tracking, transport tables | No `school_id` yet. Being replaced by the unified fee module (redesign plan Phases 2 to 4) |

## How the default school is seeded

`Init/00_create_default_school.sql` inserts Sunrise as school 1 and gives `school_id` a temporary `DEFAULT 1`. Every seed script that follows then writes Sunrise's rows without naming the school. `Init/99_finish_default_school.sql` removes that default and moves every id sequence past the seeded ids.

Admin logins after a fresh deployment: see `Init/02_create_admin_user.sql` and `Init/03_create_super_admin_user.sql`. Change these passwords after the first login.

## Changing the schema later

- **Never run a single `Tables/*.sql` file against a database with data.** Each one starts with `DROP TABLE ... CASCADE`.
- Edit the table script so fresh deployments get the change, AND add a migration to `Versioning/` for existing databases. Apply it with `python migrate_database.py` (see `Versioning/README.md`).
- New table, function, view or data script: add it to `deploy_database.sql`.
- There are no views. The five old reporting views and two helper functions (`calculate_age`, `get_academic_year`) were removed because nothing used them.

## Check a deployment

```sql
SELECT version, kind, applied_at FROM school.schema_migrations ORDER BY id;
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'school' AND table_type = 'BASE TABLE';  -- 58
SELECT id, code, name, status FROM school.schools;
```
