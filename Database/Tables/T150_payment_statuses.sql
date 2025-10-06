-- =====================================================
-- Table: payment_statuses
-- Description: Stores payment status options with color codes for UI
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS payment_statuses CASCADE;

-- Create table
CREATE TABLE payment_statuses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color_code VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE payment_statuses IS 'Payment status options (PENDING, PAID, PARTIAL, OVERDUE, CANCELLED)';
COMMENT ON COLUMN payment_statuses.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN payment_statuses.name IS 'Status name';
COMMENT ON COLUMN payment_statuses.color_code IS 'Hex color code for UI display';

