-- =====================================================
-- Table: fee_audit_log
-- Description: Who changed what in the fee module.
-- Dependencies: schools, users
-- =====================================================

DROP TABLE IF EXISTS fee_audit_log CASCADE;

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
