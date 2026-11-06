-- =====================================================
-- Table: expense_categories
-- Description: Stores expense category definitions with budget limits
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS expense_categories CASCADE;

-- Create table
CREATE TABLE expense_categories (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    budget_limit DECIMAL(15,2),
    requires_approval BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE expense_categories IS 'Expense category definitions for expense management';
COMMENT ON COLUMN expense_categories.id IS 'Primary key - auto-increment';
COMMENT ON COLUMN expense_categories.name IS 'Category name (STATIONERY, MAINTENANCE, UTILITIES, etc.)';
COMMENT ON COLUMN expense_categories.budget_limit IS 'Budget limit for this category';
COMMENT ON COLUMN expense_categories.requires_approval IS 'Flag indicating if approval is required';

-- Multi-tenancy: every row belongs to one school
CREATE INDEX IF NOT EXISTS idx_expense_categories_school_id ON expense_categories (school_id);
CREATE UNIQUE INDEX IF NOT EXISTS expense_categories_school_name_unique ON expense_categories (school_id, name);
COMMENT ON COLUMN expense_categories.school_id IS 'School (tenant) this row belongs to';
