-- =====================================================
-- Close the default-school seed window
-- =====================================================
-- 1. Removes the temporary school_id DEFAULT added by 00_create_default_school.sql.
-- 2. Moves every id sequence past the ids the seed scripts inserted explicitly,
--    so the next row created by the application does not collide.
-- =====================================================

DO $$
DECLARE
    t TEXT;
    seq TEXT;
    max_id BIGINT;
BEGIN
    FOR t IN
        SELECT c.table_name
        FROM information_schema.columns c
        JOIN information_schema.tables tb
          ON tb.table_schema = c.table_schema AND tb.table_name = c.table_name AND tb.table_type = 'BASE TABLE'
        WHERE c.table_schema = current_schema() AND c.column_name = 'school_id'
    LOOP
        EXECUTE format('ALTER TABLE %I ALTER COLUMN school_id DROP DEFAULT', t);
    END LOOP;

    FOR t IN
        SELECT table_name FROM information_schema.columns
        WHERE table_schema = current_schema() AND column_name = 'id'
          AND column_default LIKE 'nextval(%'
    LOOP
        seq := pg_get_serial_sequence(quote_ident(t), 'id');
        IF seq IS NOT NULL THEN
            EXECUTE format('SELECT MAX(id) FROM %I', t) INTO max_id;
            IF max_id IS NULL THEN
                PERFORM setval(seq, 1, false);
            ELSE
                PERFORM setval(seq, max_id, true);
            END IF;
        END IF;
    END LOOP;
END $$;
