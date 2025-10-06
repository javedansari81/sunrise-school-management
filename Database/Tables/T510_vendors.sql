-- =====================================================
-- Table: vendors
-- Description: Stores vendor information for expense management
-- Dependencies: users
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS vendors CASCADE;

-- Create table
CREATE TABLE vendors (
    id SERIAL PRIMARY KEY,
    vendor_name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    country VARCHAR(100) DEFAULT 'India',

    -- Business Information
    gst_number VARCHAR(20),
    pan_number VARCHAR(15),
    vendor_categories JSONB,

    -- Banking Information
    bank_name VARCHAR(100),
    account_number VARCHAR(50),
    ifsc_code VARCHAR(15),
    account_holder_name VARCHAR(200),

    -- Contract Information
    contract_start_date DATE,
    contract_end_date DATE,
    payment_terms VARCHAR(100),
    credit_limit DECIMAL(12,2) DEFAULT 0.0,

    -- Performance Metrics
    rating DECIMAL(3,2) CHECK (rating BETWEEN 0 AND 5),
    total_orders INTEGER DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0.0,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,

    -- Soft Delete
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_date TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER,

    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_vendors_name ON vendors(vendor_name);
CREATE INDEX IF NOT EXISTS idx_vendors_active ON vendors(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_vendors_not_deleted ON vendors(is_deleted) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_vendors_active_not_deleted ON vendors(is_active, is_deleted) WHERE is_active = TRUE AND is_deleted = FALSE;

-- Add comments
COMMENT ON TABLE vendors IS 'Vendor information for expense management';
COMMENT ON COLUMN vendors.is_deleted IS 'Soft delete flag';
COMMENT ON COLUMN vendors.deleted_date IS 'Timestamp when record was soft deleted';

