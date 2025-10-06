-- =====================================================
-- Table: expense_categories
-- Description: Stores expense category definitions with budget limits
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS expense_categories CASCADE;

-- Create table
CREATE TABLE expense_categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    budget_limit DECIMAL(15,2),
    requires_approval BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE expense_categories IS 'Expense category definitions for expense management';
COMMENT ON COLUMN expense_categories.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN expense_categories.name IS 'Category name (STATIONERY, MAINTENANCE, UTILITIES, etc.)';
COMMENT ON COLUMN expense_categories.budget_limit IS 'Budget limit for this category';
COMMENT ON COLUMN expense_categories.requires_approval IS 'Flag indicating if approval is required';

