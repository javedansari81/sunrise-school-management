-- =====================================================
-- Fee Management Tables
-- =====================================================

-- Fee Structures table (Fee structure for different classes)
CREATE TABLE IF NOT EXISTS fee_structures (
    id SERIAL PRIMARY KEY,
    class_name VARCHAR(20) NOT NULL,
    session_year VARCHAR(10) NOT NULL CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27')),
    
    -- Fee Components
    tuition_fee DECIMAL(10,2) DEFAULT 0.0,
    admission_fee DECIMAL(10,2) DEFAULT 0.0,
    development_fee DECIMAL(10,2) DEFAULT 0.0,
    activity_fee DECIMAL(10,2) DEFAULT 0.0,
    transport_fee DECIMAL(10,2) DEFAULT 0.0,
    library_fee DECIMAL(10,2) DEFAULT 0.0,
    lab_fee DECIMAL(10,2) DEFAULT 0.0,
    exam_fee DECIMAL(10,2) DEFAULT 0.0,
    other_fee DECIMAL(10,2) DEFAULT 0.0,
    
    -- Total
    total_annual_fee DECIMAL(10,2) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Unique constraint
    UNIQUE(class_name, session_year)
);

-- Fee Records table (Individual student fee records)
CREATE TABLE IF NOT EXISTS fee_records (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year VARCHAR(10) NOT NULL CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27')),
    payment_type VARCHAR(20) NOT NULL CHECK (payment_type IN ('Monthly', 'Quarterly', 'Half Yearly', 'Yearly')),
    
    -- Fee Details
    total_amount DECIMAL(10,2) NOT NULL,
    paid_amount DECIMAL(10,2) DEFAULT 0.0,
    balance_amount DECIMAL(10,2) NOT NULL,
    
    -- Payment Status
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Partial', 'Paid', 'Overdue')),
    
    -- Due Date
    due_date DATE NOT NULL,
    
    -- Payment Details (for single payment records)
    payment_method VARCHAR(20) CHECK (payment_method IN ('Cash', 'Cheque', 'Online', 'UPI', 'Card')),
    transaction_id VARCHAR(100),
    payment_date DATE,
    
    -- Additional Info
    remarks TEXT,
    late_fee DECIMAL(10,2) DEFAULT 0.0,
    discount_amount DECIMAL(10,2) DEFAULT 0.0,
    discount_reason VARCHAR(200),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Fee Payments table (Multiple payments for a single fee record)
CREATE TABLE IF NOT EXISTS fee_payments (
    id SERIAL PRIMARY KEY,
    fee_record_id INTEGER NOT NULL REFERENCES fee_records(id) ON DELETE CASCADE,
    
    -- Payment Details
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('Cash', 'Cheque', 'Online', 'UPI', 'Card')),
    payment_date DATE NOT NULL,
    transaction_id VARCHAR(100),
    
    -- Additional Info
    remarks TEXT,
    receipt_number VARCHAR(50),
    collected_by INTEGER REFERENCES users(id),
    
    -- Bank/Cheque Details
    bank_name VARCHAR(100),
    cheque_number VARCHAR(50),
    cheque_date DATE,
    
    -- Online Payment Details
    gateway_transaction_id VARCHAR(200),
    gateway_name VARCHAR(50),
    gateway_status VARCHAR(20),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fee Discounts table (Student-specific discounts)
CREATE TABLE IF NOT EXISTS fee_discounts (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year VARCHAR(10) NOT NULL CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27')),
    discount_type VARCHAR(50) NOT NULL, -- 'Scholarship', 'Sibling Discount', 'Merit', 'Financial Aid', etc.
    discount_name VARCHAR(200) NOT NULL,
    discount_percentage DECIMAL(5,2),
    discount_amount DECIMAL(10,2),
    applicable_fees TEXT, -- JSON array or comma-separated fee types
    
    -- Approval Details
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    approval_remarks TEXT,
    
    -- Validity
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Fee Reminders table (Payment reminders sent to parents)
CREATE TABLE IF NOT EXISTS fee_reminders (
    id SERIAL PRIMARY KEY,
    fee_record_id INTEGER NOT NULL REFERENCES fee_records(id) ON DELETE CASCADE,
    reminder_type VARCHAR(20) NOT NULL CHECK (reminder_type IN ('Email', 'SMS', 'Phone', 'Letter')),
    recipient_contact VARCHAR(255) NOT NULL, -- Email or phone number
    message_content TEXT NOT NULL,
    
    -- Status
    sent_at TIMESTAMP WITH TIME ZONE,
    delivery_status VARCHAR(20) DEFAULT 'Pending' CHECK (delivery_status IN ('Pending', 'Sent', 'Delivered', 'Failed')),
    delivery_response TEXT,
    
    -- Scheduling
    scheduled_for TIMESTAMP WITH TIME ZONE,
    sent_by INTEGER REFERENCES users(id),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fee Reports table (Generated fee reports)
CREATE TABLE IF NOT EXISTS fee_reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL, -- 'Monthly Collection', 'Outstanding Fees', 'Class-wise Collection', etc.
    report_name VARCHAR(200) NOT NULL,
    parameters JSONB, -- Report parameters like date range, class, etc.
    file_url VARCHAR(500),
    file_format VARCHAR(10), -- 'PDF', 'Excel', 'CSV'
    
    -- Generation Details
    generated_by INTEGER NOT NULL REFERENCES users(id),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    generation_time_ms INTEGER, -- Time taken to generate report
    
    -- Access Control
    is_public BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Comments and Notes
COMMENT ON TABLE fee_structures IS 'Fee structure definitions for different classes and sessions';
COMMENT ON TABLE fee_records IS 'Individual student fee records and payment tracking';
COMMENT ON TABLE fee_payments IS 'Detailed payment transactions for fee records';
COMMENT ON TABLE fee_discounts IS 'Student-specific fee discounts and scholarships';
COMMENT ON TABLE fee_reminders IS 'Payment reminder communications sent to parents';
COMMENT ON TABLE fee_reports IS 'Generated fee reports and their metadata';

COMMENT ON COLUMN fee_records.payment_type IS 'Payment frequency: Monthly, Quarterly, Half Yearly, Yearly';
COMMENT ON COLUMN fee_records.status IS 'Payment status: Pending, Partial, Paid, Overdue';
COMMENT ON COLUMN fee_payments.payment_method IS 'Payment method: Cash, Cheque, Online, UPI, Card';
