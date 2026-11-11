-- =====================================================
-- V002: Unified fee module core (Phase 2)
-- =====================================================
-- 1. Renames the pre-redesign fee_structures table (and its constraints,
--    indexes and sequence) to legacy_fee_structures, so the new fee module can
--    use the name. The old fee code points at legacy_fee_structures until
--    Phase 4 removes it. The old function enable_monthly_tracking_complete is
--    rewritten to read legacy_fee_structures.
-- 2. Creates the 11 tables of the unified fee module (same as Tables/T900-T950).
-- 3. Seeds default fee heads, the sibling concession rule and fee settings for
--    every existing school, and fills in Sunrise's receipt branding (same as
--    Init/04_fee_module_defaults.sql).
-- =====================================================

-- 1. Legacy rename
ALTER TABLE fee_structures RENAME TO legacy_fee_structures;
ALTER SEQUENCE fee_structures_id_seq RENAME TO legacy_fee_structures_id_seq;
ALTER TABLE legacy_fee_structures RENAME CONSTRAINT fee_structures_pkey TO legacy_fee_structures_pkey;
ALTER TABLE legacy_fee_structures RENAME CONSTRAINT fee_structures_class_id_session_year_id_key TO legacy_fee_structures_class_id_session_year_id_key;
ALTER TABLE legacy_fee_structures RENAME CONSTRAINT fee_structures_class_id_fkey TO legacy_fee_structures_class_id_fkey;
ALTER TABLE legacy_fee_structures RENAME CONSTRAINT fee_structures_session_year_id_fkey TO legacy_fee_structures_session_year_id_fkey;
ALTER INDEX idx_fee_structures_class_session RENAME TO idx_legacy_fee_structures_class_session;
ALTER INDEX idx_fee_structures_class_id RENAME TO idx_legacy_fee_structures_class_id;
ALTER INDEX idx_fee_structures_session_year_id RENAME TO idx_legacy_fee_structures_session_year_id;
COMMENT ON TABLE legacy_fee_structures IS 'Pre-redesign fee structures; removed in Phase 4';

DO $$
DECLARE
    f RECORD;
    def TEXT;
BEGIN
    FOR f IN
        SELECT p.oid FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname = current_schema() AND p.proname = 'enable_monthly_tracking_complete'
    LOOP
        def := pg_get_functiondef(f.oid);
        IF def ~ '\mfee_structures\M' THEN
            EXECUTE regexp_replace(def, '\mfee_structures\M', 'legacy_fee_structures', 'g');
        END IF;
    END LOOP;
END $$;

-- 2. Unified fee module tables
-- =====================================================
-- Table: fee_heads
-- Description: A school's list of fee types (Tuition, Transport, Admission, ...).
--              A new fee type is a row, not a schema change.
-- Dependencies: schools
-- =====================================================

CREATE TABLE fee_heads (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    code VARCHAR(30) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(20) NOT NULL DEFAULT 'ACADEMIC'
        CHECK (category IN ('ACADEMIC', 'TRANSPORT', 'ONE_TIME', 'PENALTY', 'OTHER')),
    default_frequency VARCHAR(20) NOT NULL DEFAULT 'MONTHLY'
        CHECK (default_frequency IN ('MONTHLY', 'QUARTERLY', 'HALF_YEARLY', 'ANNUAL', 'ONE_TIME')),
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fee_heads_school_code_unique UNIQUE (school_id, code),
    CONSTRAINT fee_heads_school_name_unique UNIQUE (school_id, name)
);

CREATE INDEX idx_fee_heads_school_id ON fee_heads (school_id);

COMMENT ON TABLE fee_heads IS 'Fee types defined per school (unified fee module)';
COMMENT ON COLUMN fee_heads.code IS 'Stable code, unique per school (TUITION, TRANSPORT, LATE_FEE, ...)';
COMMENT ON COLUMN fee_heads.is_system IS 'Used by the system (TRANSPORT, LATE_FEE): cannot be deleted or have its code changed';
COMMENT ON COLUMN fee_heads.school_id IS 'School (tenant) this row belongs to';

-- =====================================================
-- Table: fee_structures
-- Description: Header of a price list for one session. Moves from DRAFT to
--              PUBLISHED; publishing archives the previously published list of
--              the session. A published list is never edited: it is copied into
--              a new draft instead.
-- Dependencies: schools, session_years, users
-- Note: the pre-redesign table of the same name is now legacy_fee_structures (T400).
-- =====================================================

CREATE TABLE fee_structures (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    name VARCHAR(150) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT'
        CHECK (status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED')),
    copied_from_id INTEGER REFERENCES fee_structures(id),
    published_at TIMESTAMP WITH TIME ZONE,
    published_by INTEGER REFERENCES users(id),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_fee_structures_school_id ON fee_structures (school_id);
CREATE INDEX idx_fee_structures_session ON fee_structures (school_id, session_year_id);
-- At most one published price list per school and session
CREATE UNIQUE INDEX fee_structures_one_published
    ON fee_structures (school_id, session_year_id) WHERE status = 'PUBLISHED';

COMMENT ON TABLE fee_structures IS 'Price list header per session (unified fee module)';
COMMENT ON COLUMN fee_structures.school_id IS 'School (tenant) this row belongs to';

-- =====================================================
-- Table: fee_structure_items
-- Description: One price line in a fee structure: a fee head, for one class
--              (or every class when class_id is NULL), with its amount and
--              billing frequency.
-- Dependencies: fee_structures, fee_heads, classes
-- =====================================================

CREATE TABLE fee_structure_items (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    fee_structure_id INTEGER NOT NULL REFERENCES fee_structures(id) ON DELETE CASCADE,
    fee_head_id INTEGER NOT NULL REFERENCES fee_heads(id),
    class_id INTEGER REFERENCES classes(id),
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    frequency VARCHAR(20) NOT NULL DEFAULT 'MONTHLY'
        CHECK (frequency IN ('MONTHLY', 'QUARTERLY', 'HALF_YEARLY', 'ANNUAL', 'ONE_TIME')),
    billing_months SMALLINT[],
    due_day SMALLINT NOT NULL DEFAULT 10 CHECK (due_day BETWEEN 1 AND 28),
    applies_to VARCHAR(20) NOT NULL DEFAULT 'ALL'
        CHECK (applies_to IN ('ALL', 'NEW_STUDENTS', 'EXISTING_STUDENTS')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_fee_structure_items_school_id ON fee_structure_items (school_id);
CREATE INDEX idx_fee_structure_items_structure ON fee_structure_items (fee_structure_id);
-- One line per head and class in a structure (NULL class = all classes)
CREATE UNIQUE INDEX fee_structure_items_unique_line
    ON fee_structure_items (fee_structure_id, fee_head_id, COALESCE(class_id, 0));

COMMENT ON TABLE fee_structure_items IS 'Price lines of a fee structure (unified fee module)';
COMMENT ON COLUMN fee_structure_items.class_id IS 'Class the line applies to; NULL = every class without its own line for this head';
COMMENT ON COLUMN fee_structure_items.billing_months IS 'Calendar months (1-12) billed. NULL = derived from the frequency and the session start month';
COMMENT ON COLUMN fee_structure_items.applies_to IS 'NEW_STUDENTS = admitted during the session (e.g. admission fee)';
COMMENT ON COLUMN fee_structure_items.school_id IS 'School (tenant) this row belongs to';

-- =====================================================
-- Table: concession_rules
-- Description: A school's discount and waiver rules. SIBLING rules use tiers
--              (family size and position among enrolled siblings, eldest first
--              by date of birth); other rules give a percent or fixed amount.
-- Dependencies: schools
-- =====================================================

CREATE TABLE concession_rules (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    concession_type VARCHAR(20) NOT NULL
        CHECK (concession_type IN ('SIBLING', 'STAFF', 'SCHOLARSHIP', 'CUSTOM')),
    value_type VARCHAR(10) NOT NULL DEFAULT 'PERCENT'
        CHECK (value_type IN ('PERCENT', 'FIXED')),
    value DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (value >= 0),
    fee_head_ids INTEGER[],
    tiers JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT concession_rules_school_name_unique UNIQUE (school_id, name),
    CONSTRAINT concession_rules_percent_max CHECK (value_type <> 'PERCENT' OR value <= 100)
);

CREATE INDEX idx_concession_rules_school_id ON concession_rules (school_id);
-- At most one active sibling rule per school
CREATE UNIQUE INDEX concession_rules_one_sibling
    ON concession_rules (school_id) WHERE concession_type = 'SIBLING' AND is_active;

COMMENT ON TABLE concession_rules IS 'Discount and waiver rules per school (unified fee module)';
COMMENT ON COLUMN concession_rules.fee_head_ids IS 'Fee heads the rule covers; NULL = every head';
COMMENT ON COLUMN concession_rules.tiers IS 'SIBLING rules: [{min_siblings, max_siblings, position_basis (ELDEST or YOUNGEST), position_from, position_to, percent}]';
COMMENT ON COLUMN concession_rules.value IS 'Percent (0-100) or fixed amount per billed due; not used by SIBLING rules';
COMMENT ON COLUMN concession_rules.school_id IS 'School (tenant) this row belongs to';

-- =====================================================
-- Table: student_fee_plans
-- Description: Which fee heads a student pays in a session, at what amount and
--              from which month to which month. Dues are generated from here.
-- Dependencies: students, session_years, fee_heads, users
-- =====================================================

CREATE TABLE student_fee_plans (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    fee_head_id INTEGER NOT NULL REFERENCES fee_heads(id),
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    frequency VARCHAR(20) NOT NULL DEFAULT 'MONTHLY'
        CHECK (frequency IN ('MONTHLY', 'QUARTERLY', 'HALF_YEARLY', 'ANNUAL', 'ONE_TIME')),
    billing_months SMALLINT[],
    due_day SMALLINT NOT NULL DEFAULT 10 CHECK (due_day BETWEEN 1 AND 28),
    start_period DATE NOT NULL,
    end_period DATE,
    source VARCHAR(20) NOT NULL CHECK (source IN ('CLASS', 'TRANSPORT', 'MANUAL')),
    source_ref_id INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    remarks TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT student_fee_plans_period_order CHECK (end_period IS NULL OR end_period >= start_period),
    CONSTRAINT student_fee_plans_first_of_month CHECK (
        EXTRACT(DAY FROM start_period) = 1 AND (end_period IS NULL OR EXTRACT(DAY FROM end_period) = 1)
    )
);

CREATE INDEX idx_student_fee_plans_school_id ON student_fee_plans (school_id);
CREATE INDEX idx_student_fee_plans_student_session ON student_fee_plans (student_id, session_year_id);
-- One open-ended class-based line per student, session and head. A line ended by a
-- class or price change keeps billing up to its end_period; is_active = FALSE means cancelled.
CREATE UNIQUE INDEX student_fee_plans_one_class_line
    ON student_fee_plans (school_id, student_id, session_year_id, fee_head_id)
    WHERE source = 'CLASS' AND is_active AND end_period IS NULL;

COMMENT ON TABLE student_fee_plans IS 'Fee heads a student pays per session (unified fee module)';
COMMENT ON COLUMN student_fee_plans.start_period IS 'First billed month (first day of the month)';
COMMENT ON COLUMN student_fee_plans.end_period IS 'Last billed month (first day of the month); NULL = to the end of the session';
COMMENT ON COLUMN student_fee_plans.source_ref_id IS 'fee_structure_items.id for CLASS, the transport assignment id for TRANSPORT';
COMMENT ON COLUMN student_fee_plans.school_id IS 'School (tenant) this row belongs to';

-- =====================================================
-- Table: student_concessions
-- Description: A concession granted to one student (staff child, scholarship,
--              custom), with reason and approver. Sibling concessions are not
--              stored here: they are worked out from the SIBLING rule and the
--              student's linked siblings each time dues are generated.
-- Dependencies: students, session_years, concession_rules, users
-- =====================================================

CREATE TABLE student_concessions (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    concession_rule_id INTEGER REFERENCES concession_rules(id),
    concession_type VARCHAR(20) NOT NULL
        CHECK (concession_type IN ('STAFF', 'SCHOLARSHIP', 'CUSTOM')),
    value_type VARCHAR(10) NOT NULL CHECK (value_type IN ('PERCENT', 'FIXED')),
    value DECIMAL(10,2) NOT NULL CHECK (value >= 0),
    fee_head_ids INTEGER[],
    start_period DATE,
    end_period DATE,
    reason TEXT NOT NULL,
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT student_concessions_percent_max CHECK (value_type <> 'PERCENT' OR value <= 100)
);

CREATE INDEX idx_student_concessions_school_id ON student_concessions (school_id);
CREATE INDEX idx_student_concessions_student_session ON student_concessions (student_id, session_year_id);

COMMENT ON TABLE student_concessions IS 'Concessions granted to individual students (unified fee module)';
COMMENT ON COLUMN student_concessions.fee_head_ids IS 'Fee heads covered; NULL = every head';
COMMENT ON COLUMN student_concessions.school_id IS 'School (tenant) this row belongs to';

-- =====================================================
-- Table: student_dues
-- Description: One billable line per student, fee head and period. The
--              student's balance is the sum of open dues. A paid or part-paid
--              due is never edited: changes are ADJUSTMENT lines or reversals.
-- Dependencies: students, session_years, fee_heads, student_fee_plans, users
-- =====================================================

CREATE TABLE student_dues (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    fee_head_id INTEGER NOT NULL REFERENCES fee_heads(id),
    student_fee_plan_id INTEGER REFERENCES student_fee_plans(id),
    line_type VARCHAR(20) NOT NULL DEFAULT 'REGULAR'
        CHECK (line_type IN ('REGULAR', 'LATE_FEE', 'ADJUSTMENT', 'MANUAL')),
    related_due_id INTEGER REFERENCES student_dues(id),
    period DATE NOT NULL,
    due_date DATE NOT NULL,
    description VARCHAR(255),
    gross_amount DECIMAL(10,2) NOT NULL,
    concession_amount DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (concession_amount >= 0),
    net_amount DECIMAL(10,2) NOT NULL,
    paid_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'PARTIAL', 'PAID', 'CANCELLED', 'WAIVED')),
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancelled_by INTEGER REFERENCES users(id),
    cancel_reason TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT student_dues_first_of_month CHECK (EXTRACT(DAY FROM period) = 1),
    CONSTRAINT student_dues_net CHECK (net_amount = gross_amount - concession_amount),
    CONSTRAINT student_dues_paid_range CHECK (paid_amount >= 0 AND paid_amount <= GREATEST(net_amount, 0))
);

CREATE INDEX idx_student_dues_school_id ON student_dues (school_id);
CREATE INDEX idx_student_dues_student_session ON student_dues (student_id, session_year_id);
CREATE INDEX idx_student_dues_open ON student_dues (school_id, due_date) WHERE status IN ('PENDING', 'PARTIAL');
-- A regular or late-fee line is generated once per student, head and period
CREATE UNIQUE INDEX student_dues_one_per_period
    ON student_dues (school_id, student_id, fee_head_id, session_year_id, period)
    WHERE line_type IN ('REGULAR', 'LATE_FEE') AND status <> 'CANCELLED';

COMMENT ON TABLE student_dues IS 'Billable lines per student, head and period (unified fee module)';
COMMENT ON COLUMN student_dues.period IS 'Billing month (first day of the month); for quarterly and longer, the first month of the period';
COMMENT ON COLUMN student_dues.related_due_id IS 'ADJUSTMENT: the due it adjusts. LATE_FEE: not used (one late fee per student and month)';
COMMENT ON COLUMN student_dues.paid_amount IS 'Sum of allocations to this due, kept in the same transaction; checked by the consistency report';
COMMENT ON COLUMN student_dues.school_id IS 'School (tenant) this row belongs to';

-- =====================================================
-- Table: receipt_sequences
-- Description: Receipt numbering per school and session, e.g. SUN/2026-27/000123.
--              The next number is taken with SELECT ... FOR UPDATE inside the
--              payment transaction, so two cashiers never get the same number.
-- Dependencies: schools, session_years
-- =====================================================

CREATE TABLE receipt_sequences (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    prefix VARCHAR(20) NOT NULL,
    next_number INTEGER NOT NULL DEFAULT 1 CHECK (next_number > 0),
    padding SMALLINT NOT NULL DEFAULT 6,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT receipt_sequences_school_session_unique UNIQUE (school_id, session_year_id)
);

CREATE INDEX idx_receipt_sequences_school_id ON receipt_sequences (school_id);

COMMENT ON TABLE receipt_sequences IS 'Receipt number series per school and session (unified fee module)';
COMMENT ON COLUMN receipt_sequences.school_id IS 'School (tenant) this row belongs to';

-- =====================================================
-- Table: payments
-- Description: Money received (kind PAYMENT) or given back (kind REVERSAL,
--              negative amount, pointing at the payment it reverses). The part
--              of a payment not allocated to dues is the student's credit.
-- Dependencies: students, session_years, payment_methods, reversal_reasons, users
-- =====================================================

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    student_id INTEGER NOT NULL REFERENCES students(id),
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    kind VARCHAR(10) NOT NULL DEFAULT 'PAYMENT' CHECK (kind IN ('PAYMENT', 'REVERSAL')),
    receipt_number VARCHAR(40),
    amount DECIMAL(10,2) NOT NULL,
    payment_method_id INTEGER REFERENCES payment_methods(id),
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    transaction_id VARCHAR(100),
    remarks TEXT,

    -- Reversal
    reverses_payment_id INTEGER REFERENCES payments(id),
    reversal_reason_id INTEGER REFERENCES reversal_reasons(id),

    -- Receipt document
    receipt_url TEXT,
    receipt_cloudinary_id TEXT,

    -- Online gateway (decision 11: not used yet)
    gateway_name VARCHAR(30),
    gateway_order_id VARCHAR(100),
    gateway_payment_id VARCHAR(100),
    gateway_status VARCHAR(30),

    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT payments_receipt_unique UNIQUE (school_id, receipt_number),
    CONSTRAINT payments_kind_shape CHECK (
        (kind = 'PAYMENT' AND amount > 0 AND reverses_payment_id IS NULL AND payment_method_id IS NOT NULL)
        OR (kind = 'REVERSAL' AND amount < 0 AND reverses_payment_id IS NOT NULL AND reversal_reason_id IS NOT NULL)
    )
);

CREATE INDEX idx_payments_school_id ON payments (school_id);
CREATE INDEX idx_payments_student ON payments (student_id, session_year_id);
CREATE INDEX idx_payments_date ON payments (school_id, payment_date);
CREATE INDEX idx_payments_reverses ON payments (reverses_payment_id) WHERE reverses_payment_id IS NOT NULL;

COMMENT ON TABLE payments IS 'Payments and reversals (unified fee module)';
COMMENT ON COLUMN payments.receipt_number IS 'Per school and session, e.g. SUN/2026-27/000123; NULL for reversals';
COMMENT ON COLUMN payments.school_id IS 'School (tenant) this row belongs to';

-- =====================================================
-- Table: payment_allocations
-- Description: Which dues a payment settled. Reversals add negative rows
--              (is_reversal) instead of editing or deleting the original ones.
-- Dependencies: payments, student_dues
-- =====================================================

CREATE TABLE payment_allocations (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    payment_id INTEGER NOT NULL REFERENCES payments(id),
    student_due_id INTEGER NOT NULL REFERENCES student_dues(id),
    amount DECIMAL(10,2) NOT NULL,
    is_reversal BOOLEAN NOT NULL DEFAULT FALSE,
    reversal_payment_id INTEGER REFERENCES payments(id),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT payment_allocations_sign CHECK (
        (NOT is_reversal AND amount > 0 AND reversal_payment_id IS NULL)
        OR (is_reversal AND amount < 0 AND reversal_payment_id IS NOT NULL)
    )
);

CREATE INDEX idx_payment_allocations_school_id ON payment_allocations (school_id);
CREATE INDEX idx_payment_allocations_payment ON payment_allocations (payment_id);
CREATE INDEX idx_payment_allocations_due ON payment_allocations (student_due_id);

COMMENT ON TABLE payment_allocations IS 'Payment to due allocations (unified fee module)';
COMMENT ON COLUMN payment_allocations.payment_id IS 'The PAYMENT whose money is allocated; reversal rows point at the same original payment';
COMMENT ON COLUMN payment_allocations.reversal_payment_id IS 'Reversal rows: the REVERSAL payment that took the money back';
COMMENT ON COLUMN payment_allocations.school_id IS 'School (tenant) this row belongs to';

-- =====================================================
-- Table: fee_audit_log
-- Description: Who changed what in the fee module.
-- Dependencies: schools, users
-- =====================================================

CREATE TABLE fee_audit_log (
    id BIGSERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    remarks TEXT,
    performed_by INTEGER REFERENCES users(id),
    performed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_fee_audit_log_school_id ON fee_audit_log (school_id);
CREATE INDEX idx_fee_audit_log_entity ON fee_audit_log (entity_type, entity_id);

COMMENT ON TABLE fee_audit_log IS 'Audit trail of the unified fee module';
COMMENT ON COLUMN fee_audit_log.school_id IS 'School (tenant) this row belongs to';

-- 3. Defaults for every existing school and Sunrise's receipt branding (same as Init/04_fee_module_defaults.sql)
UPDATE schools SET
    name = 'Sunrise National Public School',
    address = 'Sena road, Farsauliyana, Rath, Hamirpur, UP - 210431',
    email = 'sunrise.nps008@gmail.com',
    website = 'https://sunrisenps.com'
WHERE code = 'sunrise' AND name = 'Sunrise School' AND address IS NULL;

INSERT INTO school_settings (school_id, key, value, description)
SELECT id, 'receipt.logo', 'static:images/school_logo_bw.jpeg',
       'Logo on receipts: static:<path under app/static> or an https URL'
FROM schools WHERE code = 'sunrise'
ON CONFLICT (school_id, key) DO NOTHING;

DO $$
DECLARE
    s RECORD;
    tuition_id INTEGER;
BEGIN
    FOR s IN
        SELECT sc.id, sc.code FROM schools sc
        WHERE NOT EXISTS (SELECT 1 FROM fee_heads h WHERE h.school_id = sc.id)
        ORDER BY sc.id
    LOOP
        INSERT INTO fee_heads (school_id, code, name, category, default_frequency, is_system, sort_order) VALUES
            (s.id, 'TUITION',     'Tuition Fee',     'ACADEMIC',  'MONTHLY',  FALSE, 10),
            (s.id, 'ADMISSION',   'Admission Fee',   'ONE_TIME',  'ONE_TIME', FALSE, 20),
            (s.id, 'DEVELOPMENT', 'Development Fee', 'ACADEMIC',  'ANNUAL',   FALSE, 30),
            (s.id, 'ACTIVITY',    'Activity Fee',    'ACADEMIC',  'ANNUAL',   FALSE, 40),
            (s.id, 'LIBRARY',     'Library Fee',     'ACADEMIC',  'ANNUAL',   FALSE, 50),
            (s.id, 'LAB',         'Lab Fee',         'ACADEMIC',  'ANNUAL',   FALSE, 60),
            (s.id, 'EXAM',        'Exam Fee',        'ACADEMIC',  'ANNUAL',   FALSE, 70),
            (s.id, 'TRANSPORT',   'Transport Fee',   'TRANSPORT', 'MONTHLY',  TRUE,  80),
            (s.id, 'LATE_FEE',    'Late Fee',        'PENALTY',   'ONE_TIME', TRUE,  90),
            (s.id, 'OTHER',       'Other Charges',   'OTHER',     'ONE_TIME', FALSE, 100);

        SELECT id INTO tuition_id FROM fee_heads WHERE school_id = s.id AND code = 'TUITION';

        INSERT INTO concession_rules (school_id, name, description, concession_type, value_type, value, fee_head_ids, tiers)
        VALUES (
            s.id, 'Sibling concession',
            'Younger siblings in large families. Siblings ordered eldest first by date of birth.',
            'SIBLING', 'PERCENT', 0, ARRAY[tuition_id],
            '[
              {"min_siblings": 3, "max_siblings": 3,    "position_basis": "YOUNGEST", "position_from": 1, "position_to": 1, "percent": 100},
              {"min_siblings": 4, "max_siblings": 4,    "position_basis": "YOUNGEST", "position_from": 1, "position_to": 1, "percent": 100},
              {"min_siblings": 4, "max_siblings": 4,    "position_basis": "YOUNGEST", "position_from": 2, "position_to": 2, "percent": 50},
              {"min_siblings": 5, "max_siblings": null, "position_basis": "YOUNGEST", "position_from": 1, "position_to": 2, "percent": 100}
            ]'::jsonb
        );

        INSERT INTO school_settings (school_id, key, value, description) VALUES
            (s.id, 'fee.receipt_prefix', UPPER(LEFT(s.code, 3)), 'Receipt number prefix, e.g. SUN in SUN/2026-27/000123'),
            (s.id, 'fee.late_fee.enabled', 'false', 'Add a Late fee due automatically after the grace days'),
            (s.id, 'fee.late_fee.mode', 'FIXED', 'FIXED amount or PERCENT of the overdue amount'),
            (s.id, 'fee.late_fee.value', '0', 'Late fee amount or percent per overdue month'),
            (s.id, 'fee.late_fee.grace_days', '7', 'Days after the due date before a late fee is added'),
            (s.id, 'fee.transport.cutoff_day', '15', 'Transport started after this day of the month is billed from the next month')
        ON CONFLICT (school_id, key) DO NOTHING;
    END LOOP;
END $$;
