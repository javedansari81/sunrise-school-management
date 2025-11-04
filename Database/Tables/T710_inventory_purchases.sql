-- =====================================================
-- Table: inventory_purchases
-- Description: Stores inventory purchase transactions
-- Dependencies: students, session_years, payment_methods, users
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS inventory_purchases CASCADE;

-- Create table
CREATE TABLE inventory_purchases (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    
    -- Purchase Details
    purchase_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount > 0),
    
    -- Payment Details
    payment_method_id INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    transaction_id VARCHAR(100),
    receipt_number VARCHAR(50),
    
    -- Additional Info
    remarks TEXT,
    purchased_by VARCHAR(200), -- Parent/Guardian name
    contact_number VARCHAR(20),
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER,
    
    -- Foreign Keys
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_inventory_purchases_student ON inventory_purchases(student_id);
CREATE INDEX IF NOT EXISTS idx_inventory_purchases_session ON inventory_purchases(session_year_id);
CREATE INDEX IF NOT EXISTS idx_inventory_purchases_date ON inventory_purchases(purchase_date);
CREATE INDEX IF NOT EXISTS idx_inventory_purchases_payment_method ON inventory_purchases(payment_method_id);
CREATE INDEX IF NOT EXISTS idx_inventory_purchases_receipt ON inventory_purchases(receipt_number);

-- Add comments
COMMENT ON TABLE inventory_purchases IS 'Inventory purchase transactions for students';
COMMENT ON COLUMN inventory_purchases.student_id IS 'Reference to student who purchased items';
COMMENT ON COLUMN inventory_purchases.session_year_id IS 'Reference to session year';
COMMENT ON COLUMN inventory_purchases.purchase_date IS 'Date of purchase';
COMMENT ON COLUMN inventory_purchases.total_amount IS 'Total amount of purchase (sum of all items)';
COMMENT ON COLUMN inventory_purchases.payment_method_id IS 'Reference to payment method';
COMMENT ON COLUMN inventory_purchases.payment_date IS 'Date of payment';
COMMENT ON COLUMN inventory_purchases.transaction_id IS 'Transaction ID for digital payments';
COMMENT ON COLUMN inventory_purchases.receipt_number IS 'Unique receipt number';
COMMENT ON COLUMN inventory_purchases.purchased_by IS 'Name of parent/guardian who made the purchase';
COMMENT ON COLUMN inventory_purchases.contact_number IS 'Contact number of purchaser';

