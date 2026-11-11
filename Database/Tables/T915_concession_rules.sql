-- =====================================================
-- Table: concession_rules
-- Description: A school's discount and waiver rules. SIBLING rules use tiers
--              (family size and position among enrolled siblings, eldest first
--              by date of birth); other rules give a percent or fixed amount.
-- Dependencies: schools
-- =====================================================

DROP TABLE IF EXISTS concession_rules CASCADE;

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
