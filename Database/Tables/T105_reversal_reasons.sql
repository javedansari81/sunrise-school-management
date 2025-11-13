-- =====================================================
-- Table: reversal_reasons
-- Description: Metadata table for payment reversal reasons
-- =====================================================

CREATE TABLE IF NOT EXISTS reversal_reasons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on name for faster lookups
CREATE INDEX IF NOT EXISTS idx_reversal_reasons_name ON reversal_reasons(name);
CREATE INDEX IF NOT EXISTS idx_reversal_reasons_is_active ON reversal_reasons(is_active);

-- Add comment
COMMENT ON TABLE reversal_reasons IS 'Metadata table for payment reversal reasons';
COMMENT ON COLUMN reversal_reasons.id IS 'Primary key';
COMMENT ON COLUMN reversal_reasons.name IS 'Unique identifier name (e.g., INCORRECT_AMOUNT)';
COMMENT ON COLUMN reversal_reasons.description IS 'Human-readable description (e.g., Incorrect Amount Entered)';
COMMENT ON COLUMN reversal_reasons.is_active IS 'Whether this reversal reason is currently active';

