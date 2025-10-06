-- =====================================================
-- Table: expenses
-- Description: Stores expense records with approval workflow
-- Dependencies: expense_categories, payment_methods, payment_statuses, expense_statuses, users, session_years
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS expenses CASCADE;

-- Create table
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,

    -- Basic Information
    expense_date DATE NOT NULL,
    expense_category_id INTEGER NOT NULL,
    subcategory VARCHAR(100),
    description TEXT NOT NULL,

    -- Financial Details
    amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
    tax_amount DECIMAL(10,2) DEFAULT 0.0 CHECK (tax_amount >= 0),
    total_amount DECIMAL(12,2) NOT NULL CHECK (total_amount > 0),
    currency VARCHAR(3) DEFAULT 'INR',

    -- Vendor Information
    vendor_name VARCHAR(200),
    vendor_contact VARCHAR(20),
    vendor_email VARCHAR(255),
    vendor_address TEXT,
    vendor_gst_number VARCHAR(20),

    -- Payment Details
    payment_method_id INTEGER NOT NULL,
    payment_status_id INTEGER DEFAULT 1,
    payment_date DATE,
    payment_reference VARCHAR(100),

    -- Bank/Cheque Details
    bank_name VARCHAR(100),
    cheque_number VARCHAR(50),
    cheque_date DATE,

    -- Approval Workflow
    expense_status_id INTEGER DEFAULT 1,
    requested_by INTEGER NOT NULL,
    approved_by INTEGER,
    approved_at TIMESTAMP WITH TIME ZONE,
    approval_comments TEXT,

    -- Budget Information
    budget_category VARCHAR(100),
    session_year_id INTEGER,
    is_budgeted BOOLEAN DEFAULT FALSE,

    -- Documents
    invoice_url VARCHAR(500),
    receipt_url VARCHAR(500),
    supporting_documents JSONB,

    -- Additional Information
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_frequency VARCHAR(20) CHECK (recurring_frequency IN ('Monthly', 'Quarterly', 'Half Yearly', 'Yearly')),
    next_due_date DATE,

    -- Priority and Urgency
    priority VARCHAR(10) DEFAULT 'Medium' CHECK (priority IN ('Low', 'Medium', 'High', 'Urgent')),
    is_emergency BOOLEAN DEFAULT FALSE,

    -- Soft Delete Support
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_date TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    FOREIGN KEY (expense_category_id) REFERENCES expense_categories(id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id),
    FOREIGN KEY (payment_status_id) REFERENCES payment_statuses(id),
    FOREIGN KEY (expense_status_id) REFERENCES expense_statuses(id),
    FOREIGN KEY (requested_by) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(expense_category_id);
CREATE INDEX IF NOT EXISTS idx_expenses_status ON expenses(expense_status_id);
CREATE INDEX IF NOT EXISTS idx_expenses_requested_by ON expenses(requested_by);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date);
CREATE INDEX IF NOT EXISTS idx_expenses_not_deleted ON expenses(is_deleted) WHERE is_deleted = FALSE;

-- Add comments
COMMENT ON TABLE expenses IS 'Expense records with approval workflow';
COMMENT ON COLUMN expenses.is_deleted IS 'Soft delete flag';
COMMENT ON COLUMN expenses.deleted_date IS 'Timestamp when record was soft deleted';

