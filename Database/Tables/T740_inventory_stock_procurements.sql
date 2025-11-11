-- =====================================================
-- Table: inventory_stock_procurements
-- Description: Records stock purchases from vendors
-- Dependencies: vendors, payment_methods, payment_statuses, users
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS inventory_stock_procurements CASCADE;

-- Create table
CREATE TABLE inventory_stock_procurements (
    id SERIAL PRIMARY KEY,
    vendor_id INTEGER,
    procurement_date DATE NOT NULL,
    invoice_number VARCHAR(100),
    total_amount DECIMAL(12,2) NOT NULL CHECK (total_amount > 0),
    
    -- Payment Details
    payment_method_id INTEGER NOT NULL,
    payment_status_id INTEGER DEFAULT 1,
    payment_date DATE,
    payment_reference VARCHAR(100),
    
    -- Additional Info
    remarks TEXT,
    invoice_url VARCHAR(500),
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER,
    
    -- Foreign Keys
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id),
    FOREIGN KEY (payment_status_id) REFERENCES payment_statuses(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_stock_procurements_vendor ON inventory_stock_procurements(vendor_id);
CREATE INDEX IF NOT EXISTS idx_stock_procurements_date ON inventory_stock_procurements(procurement_date);
CREATE INDEX IF NOT EXISTS idx_stock_procurements_status ON inventory_stock_procurements(payment_status_id);

-- Add comments
COMMENT ON TABLE inventory_stock_procurements IS 'Stock procurement records from vendors';
COMMENT ON COLUMN inventory_stock_procurements.vendor_id IS 'Reference to vendor (nullable for direct purchases)';
COMMENT ON COLUMN inventory_stock_procurements.procurement_date IS 'Date of stock procurement';
COMMENT ON COLUMN inventory_stock_procurements.invoice_number IS 'Vendor invoice number';
COMMENT ON COLUMN inventory_stock_procurements.total_amount IS 'Total procurement amount';
COMMENT ON COLUMN inventory_stock_procurements.payment_method_id IS 'Payment method used';
COMMENT ON COLUMN inventory_stock_procurements.payment_status_id IS 'Payment status (Pending/Paid)';
COMMENT ON COLUMN inventory_stock_procurements.payment_date IS 'Date of payment to vendor';
COMMENT ON COLUMN inventory_stock_procurements.payment_reference IS 'Payment reference/transaction ID';
COMMENT ON COLUMN inventory_stock_procurements.invoice_url IS 'URL to invoice document';

