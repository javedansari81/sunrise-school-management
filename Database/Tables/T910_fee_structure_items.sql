-- =====================================================
-- Table: fee_structure_items
-- Description: One price line in a fee structure: a fee head, for one class
--              (or every class when class_id is NULL), with its amount and
--              billing frequency.
-- Dependencies: fee_structures, fee_heads, classes
-- =====================================================

DROP TABLE IF EXISTS fee_structure_items CASCADE;

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
