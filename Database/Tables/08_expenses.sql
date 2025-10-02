-- =====================================================
-- Expense Management Tables
-- =====================================================

-- Expenses table (School expense records) - Updated for metadata-driven architecture
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,

    -- Basic Information
    expense_date DATE NOT NULL CHECK (expense_date >= '2020-01-01'),
    expense_category_id INTEGER NOT NULL REFERENCES expense_categories(id),
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
    payment_method_id INTEGER NOT NULL REFERENCES payment_methods(id),
    payment_status_id INTEGER DEFAULT 1 REFERENCES payment_statuses(id),
    payment_date DATE CHECK (payment_date IS NULL OR payment_date >= expense_date),
    payment_reference VARCHAR(100),

    -- Bank/Cheque Details
    bank_name VARCHAR(100),
    cheque_number VARCHAR(50),
    cheque_date DATE,

    -- Approval Workflow
    expense_status_id INTEGER DEFAULT 1 REFERENCES expense_statuses(id),
    requested_by INTEGER NOT NULL REFERENCES users(id),
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    approval_comments TEXT,

    -- Budget Information
    budget_category VARCHAR(100),
    session_year_id INTEGER REFERENCES session_years(id),
    is_budgeted BOOLEAN DEFAULT FALSE,
    
    -- Documents
    invoice_url VARCHAR(500),
    receipt_url VARCHAR(500),
    supporting_documents JSONB, -- Array of document URLs
    
    -- Additional Information
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_frequency VARCHAR(20) CHECK (recurring_frequency IN ('Monthly', 'Quarterly', 'Half Yearly', 'Yearly')),
    next_due_date DATE,
    
    -- Priority and Urgency
    priority VARCHAR(10) DEFAULT 'Medium' CHECK (priority IN ('Low', 'Medium', 'High', 'Urgent')),
    is_emergency BOOLEAN DEFAULT FALSE,

    -- Soft Delete Support (added in V005)
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_date TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Note: This table is now replaced by the metadata expense_categories table
-- The metadata expense_categories table is defined in 00_metadata_tables.sql

-- Vendors table (Vendor/Supplier information)
CREATE TABLE IF NOT EXISTS vendors (
    id SERIAL PRIMARY KEY,
    
    -- Basic Information
    vendor_name VARCHAR(200) UNIQUE NOT NULL,
    vendor_code VARCHAR(50) UNIQUE,
    contact_person VARCHAR(200),
    
    -- Contact Information
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    
    -- Address
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'India',
    
    -- Business Information
    gst_number VARCHAR(20),
    pan_number VARCHAR(20),
    business_type VARCHAR(50),
    
    -- Banking Details
    bank_name VARCHAR(100),
    account_number VARCHAR(50),
    ifsc_code VARCHAR(20),
    account_holder_name VARCHAR(200),
    
    -- Categories
    service_categories TEXT, -- JSON array of categories they serve
    
    -- Rating and Performance
    rating DECIMAL(3,2) CHECK (rating BETWEEN 0 AND 5),
    total_orders INTEGER DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0.0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER REFERENCES users(id)
);

-- Purchase Orders table (Purchase order management)
CREATE TABLE IF NOT EXISTS purchase_orders (
    id SERIAL PRIMARY KEY,
    po_number VARCHAR(50) UNIQUE NOT NULL,
    vendor_id INTEGER NOT NULL REFERENCES vendors(id),
    
    -- Order Details
    order_date DATE NOT NULL,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    
    -- Financial Details
    subtotal DECIMAL(12,2) NOT NULL CHECK (subtotal > 0),
    tax_amount DECIMAL(10,2) DEFAULT 0.0 CHECK (tax_amount >= 0),
    discount_amount DECIMAL(10,2) DEFAULT 0.0 CHECK (discount_amount >= 0),
    total_amount DECIMAL(12,2) NOT NULL CHECK (total_amount > 0),
    
    -- Status
    status VARCHAR(20) DEFAULT 'Draft' CHECK (status IN ('Draft', 'Sent', 'Acknowledged', 'Delivered', 'Completed', 'Cancelled')),
    
    -- Approval
    created_by INTEGER NOT NULL REFERENCES users(id),
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    
    -- Additional Information
    terms_and_conditions TEXT,
    delivery_address TEXT,
    special_instructions TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Purchase Order Items table (Items in purchase orders)
CREATE TABLE IF NOT EXISTS purchase_order_items (
    id SERIAL PRIMARY KEY,
    po_id INTEGER NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    
    -- Item Details
    item_name VARCHAR(200) NOT NULL,
    item_description TEXT,
    item_code VARCHAR(100),
    
    -- Quantity and Pricing
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    unit_of_measure VARCHAR(20), -- 'pieces', 'kg', 'liters', etc.
    
    -- Delivery
    quantity_delivered INTEGER DEFAULT 0,
    quantity_pending INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Budget table (Annual budget planning) - Updated for metadata-driven architecture
CREATE TABLE IF NOT EXISTS budgets (
    id SERIAL PRIMARY KEY,
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    expense_category_id INTEGER NOT NULL REFERENCES expense_categories(id),
    
    -- Budget Amounts
    allocated_amount DECIMAL(12,2) NOT NULL,
    spent_amount DECIMAL(12,2) DEFAULT 0.0,
    remaining_amount DECIMAL(12,2),
    
    -- Status
    is_approved BOOLEAN DEFAULT FALSE,
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER REFERENCES users(id),
    
    -- Unique constraint
    UNIQUE(session_year_id, expense_category_id)
);

-- Expense Reports table (Generated expense reports)
CREATE TABLE IF NOT EXISTS expense_reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL, -- 'Monthly Expenses', 'Category-wise', 'Vendor-wise', 'Budget vs Actual', etc.
    report_name VARCHAR(200) NOT NULL,
    parameters JSONB, -- Report parameters
    file_url VARCHAR(500),
    file_format VARCHAR(10), -- 'PDF', 'Excel', 'CSV'
    
    -- Generation Details
    generated_by INTEGER NOT NULL REFERENCES users(id),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    generation_time_ms INTEGER,
    
    -- Access Control
    is_public BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Comments and Notes
COMMENT ON TABLE expenses IS 'School expense records and financial transactions';
COMMENT ON TABLE vendors IS 'Vendor and supplier information';
COMMENT ON TABLE purchase_orders IS 'Purchase order management';
COMMENT ON TABLE purchase_order_items IS 'Items within purchase orders';
COMMENT ON TABLE budgets IS 'Annual budget planning and tracking';
COMMENT ON TABLE expense_reports IS 'Generated expense reports';

COMMENT ON COLUMN expenses.expense_category_id IS 'Foreign key reference to expense_categories metadata table';
COMMENT ON COLUMN expenses.payment_method_id IS 'Foreign key reference to payment_methods metadata table';
COMMENT ON COLUMN expenses.payment_status_id IS 'Foreign key reference to payment_statuses metadata table';
COMMENT ON COLUMN expenses.expense_status_id IS 'Foreign key reference to expense_statuses metadata table';
COMMENT ON COLUMN expenses.session_year_id IS 'Foreign key reference to session_years metadata table';
COMMENT ON COLUMN budgets.session_year_id IS 'Foreign key reference to session_years metadata table';
COMMENT ON COLUMN budgets.expense_category_id IS 'Foreign key reference to expense_categories metadata table';
