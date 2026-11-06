-- =====================================================
-- Migration: V036_add_schools_and_tenant_columns
-- Description: Multi-tenancy foundation (Phase 1).
--   1. Creates the schools and school_settings tables.
--   2. Inserts the existing school (Sunrise) as school 1.
--   3. Adds school_id to every school-owned and school-configurable table,
--      backfilled with 1.
--   4. Makes unique keys per school (names, admission numbers, employee IDs, emails).
--
-- Notes:
--   * school_id keeps a transitional DEFAULT 1 so that raw SQL writes that are
--     not yet tenant-aware keep working while only one school exists. The
--     default is removed in Phase 5, once every write path stamps school_id.
--   * The old fee and transport tables are intentionally NOT changed. They are
--     replaced by the unified fee module (Phases 2 to 4).
--   * Idempotent: safe to run more than once.
--   * Contains no psql meta-commands, so it can also be executed by a driver.
-- =====================================================

BEGIN;

SET search_path TO sunrise, public;

-- -----------------------------------------------------
-- 1. schools
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS schools (
    id SERIAL PRIMARY KEY,
    code VARCHAR(63) NOT NULL,
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    logo_url TEXT,
    timezone VARCHAR(64) NOT NULL DEFAULT 'Asia/Kolkata',
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    academic_year_start_month INTEGER NOT NULL DEFAULT 4,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT schools_code_unique UNIQUE (code),
    -- code is used as the subdomain label: lowercase letters, digits and hyphens
    CONSTRAINT schools_code_format CHECK (code ~ '^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$'),
    CONSTRAINT schools_status_valid CHECK (status IN ('ACTIVE', 'SUSPENDED')),
    CONSTRAINT schools_start_month_valid CHECK (academic_year_start_month BETWEEN 1 AND 12)
);

COMMENT ON TABLE schools IS 'Tenants. One row per school served by the platform';
COMMENT ON COLUMN schools.code IS 'Subdomain label, for example sunrise in sunrise.<base domain>';

INSERT INTO schools (id, code, name, short_name)
VALUES (1, 'sunrise', 'Sunrise School', 'Sunrise')
ON CONFLICT (id) DO NOTHING;

-- Keep the sequence ahead of the explicit id 1
SELECT setval(pg_get_serial_sequence('schools', 'id'), GREATEST((SELECT MAX(id) FROM schools), 1));

-- -----------------------------------------------------
-- 2. school_settings
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS school_settings (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    key VARCHAR(100) NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT school_settings_school_key_unique UNIQUE (school_id, key)
);

COMMENT ON TABLE school_settings IS 'Per-school key/value settings (receipt prefix, WhatsApp templates, late fee rules, ...)';

-- -----------------------------------------------------
-- 3. school_id on tenant tables
-- -----------------------------------------------------
DO $$
DECLARE
    t TEXT;
    tenant_tables TEXT[] := ARRAY[
        -- School-owned data
        'users', 'students', 'teachers',
        'attendance_records', 'leave_requests',
        'expenses', 'vendors',
        'inventory_pricing', 'inventory_purchases', 'inventory_purchase_items',
        'inventory_stock', 'inventory_stock_procurements', 'inventory_stock_procurement_items',
        'gallery_images', 'alerts',
        'student_siblings', 'student_session_history',
        -- School-configurable lists
        'classes', 'session_years', 'departments', 'positions',
        'expense_categories', 'gallery_categories',
        'inventory_item_category', 'inventory_item_types', 'inventory_size_types',
        'leave_types'
    ];
BEGIN
    FOREACH t IN ARRAY tenant_tables LOOP
        IF to_regclass(t) IS NULL THEN
            RAISE NOTICE 'Skipping %, table does not exist', t;
            CONTINUE;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = current_schema() AND table_name = t AND column_name = 'school_id'
        ) THEN
            -- A constant default backfills existing rows without a table rewrite
            EXECUTE format('ALTER TABLE %I ADD COLUMN school_id INTEGER NOT NULL DEFAULT 1', t);
            RAISE NOTICE 'Added school_id to %', t;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint WHERE conname = t || '_school_id_fkey'
        ) THEN
            EXECUTE format(
                'ALTER TABLE %I ADD CONSTRAINT %I FOREIGN KEY (school_id) REFERENCES schools(id)',
                t, t || '_school_id_fkey'
            );
        END IF;

        EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %I (school_id)', 'idx_' || t || '_school_id', t);
    END LOOP;
END $$;

-- -----------------------------------------------------
-- 3b. Auto-increment ids on school-configurable lists
--     These lists were loaded with fixed ids and have no id default. Each new
--     school creates its own rows, so they need a sequence. Existing ids stay.
-- -----------------------------------------------------
DO $$
DECLARE
    t TEXT;
    seq TEXT;
    list_tables TEXT[] := ARRAY[
        'classes', 'session_years', 'departments', 'positions',
        'expense_categories', 'gallery_categories',
        'inventory_item_category', 'inventory_item_types', 'inventory_size_types',
        'leave_types'
    ];
BEGIN
    FOREACH t IN ARRAY list_tables LOOP
        IF to_regclass(t) IS NULL THEN
            CONTINUE;
        END IF;
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = current_schema() AND table_name = t AND column_name = 'id'
              AND (column_default IS NOT NULL OR is_identity = 'YES')
        ) THEN
            CONTINUE;
        END IF;

        seq := t || '_id_seq';
        EXECUTE format('CREATE SEQUENCE IF NOT EXISTS %I OWNED BY %I.id', seq, t);
        EXECUTE format('SELECT setval(%L, COALESCE((SELECT MAX(id) FROM %I), 0) + 1, false)', seq, t);
        EXECUTE format('ALTER TABLE %I ALTER COLUMN id SET DEFAULT nextval(%L)', t, seq);
        RAISE NOTICE 'Added id sequence to %', t;
    END LOOP;
END $$;

-- -----------------------------------------------------
-- 4. Per-school unique keys
-- -----------------------------------------------------

-- 4a. Lookup lists: name unique per school instead of globally
DO $$
DECLARE
    t TEXT;
    c RECORD;
    list_tables TEXT[] := ARRAY[
        'classes', 'session_years', 'departments', 'positions',
        'expense_categories', 'gallery_categories',
        'inventory_item_category', 'inventory_item_types', 'inventory_size_types',
        'leave_types'
    ];
BEGIN
    FOREACH t IN ARRAY list_tables LOOP
        IF to_regclass(t) IS NULL THEN
            CONTINUE;
        END IF;

        -- Drop any single-column UNIQUE constraint on name
        FOR c IN
            SELECT con.conname
            FROM pg_constraint con
            JOIN pg_class rel ON rel.oid = con.conrelid
            JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
            WHERE nsp.nspname = current_schema()
              AND rel.relname = t
              AND con.contype = 'u'
              AND con.conkey = ARRAY[(
                  SELECT attnum FROM pg_attribute WHERE attrelid = rel.oid AND attname = 'name'
              )]::smallint[]
        LOOP
            EXECUTE format('ALTER TABLE %I DROP CONSTRAINT %I', t, c.conname);
            RAISE NOTICE 'Dropped %.%', t, c.conname;
        END LOOP;

        EXECUTE format(
            'CREATE UNIQUE INDEX IF NOT EXISTS %I ON %I (school_id, name)',
            t || '_school_name_unique', t
        );
    END LOOP;
END $$;

-- 4b. students: admission_number and email unique per school (non-deleted rows)
DROP INDEX IF EXISTS students_admission_number_active_unique;
CREATE UNIQUE INDEX IF NOT EXISTS students_school_admission_number_active_unique
    ON students (school_id, admission_number)
    WHERE (is_deleted = FALSE OR is_deleted IS NULL);

DROP INDEX IF EXISTS students_email_active_unique;
CREATE UNIQUE INDEX IF NOT EXISTS students_school_email_active_unique
    ON students (school_id, email)
    WHERE (is_deleted = FALSE OR is_deleted IS NULL) AND email IS NOT NULL;

-- 4c. teachers: employee_id and email unique per school (non-deleted rows)
DROP INDEX IF EXISTS teachers_employee_id_active_unique;
CREATE UNIQUE INDEX IF NOT EXISTS teachers_school_employee_id_active_unique
    ON teachers (school_id, employee_id)
    WHERE (is_deleted = FALSE OR is_deleted IS NULL);

DROP INDEX IF EXISTS teachers_email_active_unique;
CREATE UNIQUE INDEX IF NOT EXISTS teachers_school_email_active_unique
    ON teachers (school_id, email)
    WHERE (is_deleted = FALSE OR is_deleted IS NULL) AND email IS NOT NULL;

-- 4d. users: email unique per school (decision 3)
DROP INDEX IF EXISTS users_email_active_unique;
CREATE UNIQUE INDEX IF NOT EXISTS users_school_email_active_unique
    ON users (school_id, email)
    WHERE (is_deleted = FALSE OR is_deleted IS NULL);

-- -----------------------------------------------------
-- 5. Verification
-- -----------------------------------------------------
DO $$
DECLARE
    missing TEXT;
    global_unique TEXT;
BEGIN
    SELECT string_agg(t, ', ') INTO missing
    FROM unnest(ARRAY['users', 'students', 'teachers', 'classes', 'session_years']) AS t
    WHERE NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = current_schema() AND table_name = t AND column_name = 'school_id'
    );
    IF missing IS NOT NULL THEN
        RAISE EXCEPTION 'V036 verification failed: school_id missing on %', missing;
    END IF;

    -- No old global unique index on the keys that must now be per school
    SELECT string_agg(indexname, ', ') INTO global_unique
    FROM pg_indexes
    WHERE schemaname = current_schema()
      AND indexname IN (
          'students_admission_number_active_unique', 'students_email_active_unique',
          'teachers_employee_id_active_unique', 'teachers_email_active_unique',
          'users_email_active_unique'
      );
    IF global_unique IS NOT NULL THEN
        RAISE EXCEPTION 'V036 verification failed: global unique indexes still present: %', global_unique;
    END IF;

    RAISE NOTICE 'V036 completed: schools table ready, school_id added to tenant tables';
END $$;

COMMIT;
