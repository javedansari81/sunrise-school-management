-- =====================================================
-- Table: expense_statuses
-- Description: Stores expense status options with color codes
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS expense_statuses CASCADE;

-- Create table
CREATE TABLE expense_statuses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color_code VARCHAR(10),
    is_final BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE expense_statuses IS 'Expense status options (PENDING, APPROVED, REJECTED, PAID)';
COMMENT ON COLUMN expense_statuses.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN expense_statuses.name IS 'Status name';
COMMENT ON COLUMN expense_statuses.color_code IS 'Hex color code for UI display';
COMMENT ON COLUMN expense_statuses.is_final IS 'Flag indicating if this is a final status';

