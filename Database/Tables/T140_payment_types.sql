-- =====================================================
-- Table: payment_types
-- Description: Stores payment type options (MONTHLY, QUARTERLY, ANNUAL, ONE_TIME)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS payment_types CASCADE;

-- Create table
CREATE TABLE payment_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE payment_types IS 'Payment type options for fee management';
COMMENT ON COLUMN payment_types.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN payment_types.name IS 'Payment type name (MONTHLY, QUARTERLY, ANNUAL, ONE_TIME)';

