-- =====================================================
-- Table: payment_methods
-- Description: Stores payment method options (CASH, UPI, BANK_TRANSFER, etc.)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS payment_methods CASCADE;

-- Create table
CREATE TABLE payment_methods (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    requires_reference BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE payment_methods IS 'Payment method options for transactions';
COMMENT ON COLUMN payment_methods.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN payment_methods.name IS 'Payment method name (CASH, UPI, BANK_TRANSFER, CHEQUE, CARD, ONLINE)';
COMMENT ON COLUMN payment_methods.requires_reference IS 'Flag indicating if reference number is required';

