-- =====================================================
-- Fee Management Tables
-- =====================================================

-- Fee Structures table (Fee structure for different classes) - Updated for metadata-driven architecture
CREATE TABLE IF NOT EXISTS fee_structures (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL REFERENCES classes(id),
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),

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

    -- Versioning and Status (added in Database_Enhancement_Scripts.sql)
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE DEFAULT CURRENT_DATE,
    effective_to DATE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    -- Unique constraint
    UNIQUE(class_id, session_year_id)
);

-- Fee Records table (Individual student fee records) - Updated for metadata-driven architecture
CREATE TABLE IF NOT EXISTS fee_records (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    payment_type_id INTEGER NOT NULL REFERENCES payment_types(id),

    -- Fee Details
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount > 0),
    paid_amount DECIMAL(10,2) DEFAULT 0.0 CHECK (paid_amount >= 0),
    balance_amount DECIMAL(10,2) NOT NULL CHECK (balance_amount >= 0),

    -- Payment Status
    payment_status_id INTEGER DEFAULT 1 REFERENCES payment_statuses(id),

    -- Due Date
    due_date DATE NOT NULL CHECK (due_date >= '2020-01-01'),

    -- Enhanced fields for monthly tracking system
    fee_structure_id INTEGER REFERENCES fee_structures(id),
    is_monthly_tracked BOOLEAN DEFAULT FALSE,
    academic_month INTEGER,
    academic_year INTEGER,

    -- Payment Details (for single payment records)
    payment_method_id INTEGER REFERENCES payment_methods(id),
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

-- Fee Payments table (Multiple payments for a single fee record) - Updated for metadata-driven architecture
CREATE TABLE IF NOT EXISTS fee_payments (
    id SERIAL PRIMARY KEY,
    fee_record_id INTEGER NOT NULL REFERENCES fee_records(id) ON DELETE CASCADE,

    -- Payment Details
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    payment_method_id INTEGER NOT NULL REFERENCES payment_methods(id),
    payment_date DATE NOT NULL CHECK (payment_date <= CURRENT_DATE),
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

-- Fee Discounts table (Student-specific discounts) - Updated for metadata-driven architecture
CREATE TABLE IF NOT EXISTS fee_discounts (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
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

-- =====================================================
-- Enhanced Monthly Fee Tracking System
-- =====================================================

-- Monthly Fee Tracking table (Month-wise fee tracking for enhanced payment system)
CREATE TABLE IF NOT EXISTS monthly_fee_tracking (
    id SERIAL PRIMARY KEY,
    fee_record_id INTEGER NOT NULL REFERENCES fee_records(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),

    -- Month Details
    academic_month INTEGER NOT NULL CHECK (academic_month BETWEEN 1 AND 12),
    academic_year INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL, -- 'April', 'May', etc.

    -- Amount Details
    monthly_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    paid_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    balance_amount DECIMAL(10,2) GENERATED ALWAYS AS (monthly_amount - paid_amount) STORED,

    -- Status and Dates
    due_date DATE NOT NULL,
    payment_status_id INTEGER REFERENCES payment_statuses(id) DEFAULT 1,

    -- Additional Charges
    late_fee DECIMAL(10,2) DEFAULT 0.00,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    UNIQUE(fee_record_id, academic_month, academic_year)
);

-- Monthly Payment Allocations table (Links payments to specific months)
CREATE TABLE IF NOT EXISTS monthly_payment_allocations (
    id SERIAL PRIMARY KEY,
    fee_payment_id INTEGER NOT NULL REFERENCES fee_payments(id) ON DELETE CASCADE,
    monthly_tracking_id INTEGER NOT NULL REFERENCES monthly_fee_tracking(id) ON DELETE CASCADE,
    allocated_amount DECIMAL(10,2) NOT NULL CHECK (allocated_amount > 0),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id),

    UNIQUE(fee_payment_id, monthly_tracking_id)
);

-- Comments and Notes
COMMENT ON TABLE fee_structures IS 'Fee structure definitions for different classes and sessions';
COMMENT ON TABLE fee_records IS 'Individual student fee records and payment tracking';
COMMENT ON TABLE fee_payments IS 'Detailed payment transactions for fee records';
COMMENT ON TABLE fee_discounts IS 'Student-specific fee discounts and scholarships';
COMMENT ON TABLE fee_reminders IS 'Payment reminder communications sent to parents';
COMMENT ON TABLE fee_reports IS 'Generated fee reports and their metadata';
COMMENT ON TABLE monthly_fee_tracking IS 'Enhanced monthly fee tracking system supporting partial payments, multi-month payments, and automatic allocation. Prevents duplicate payments for already-paid months.';
COMMENT ON TABLE monthly_payment_allocations IS 'Links fee payments to specific months with automatic allocation logic. Supports scenarios like 3200 rs = 3 full months + 200 rs partial for 4th month.';

-- =====================================================
-- Performance Indexes for Enhanced Fee System
-- =====================================================

-- Index for monthly fee tracking queries by student and session
CREATE INDEX IF NOT EXISTS idx_monthly_fee_tracking_student_session
ON monthly_fee_tracking(student_id, session_year_id, academic_month);

-- Index for monthly payment allocations
CREATE INDEX IF NOT EXISTS idx_monthly_payment_allocations_tracking
ON monthly_payment_allocations(monthly_tracking_id);

-- Index for fee payments by date
CREATE INDEX IF NOT EXISTS idx_fee_payments_date
ON fee_payments(payment_date);

-- Index for fee records by student and session
CREATE INDEX IF NOT EXISTS idx_fee_records_student_session
ON fee_records(student_id, session_year_id);

-- Composite index for efficient payment history queries
CREATE INDEX IF NOT EXISTS idx_monthly_fee_tracking_composite
ON monthly_fee_tracking(student_id, session_year_id, academic_month, payment_status_id);

-- Additional constraints for data integrity
ALTER TABLE monthly_fee_tracking
ADD CONSTRAINT IF NOT EXISTS chk_academic_month_valid
CHECK (academic_month >= 1 AND academic_month <= 12);

COMMENT ON COLUMN fee_structures.class_id IS 'Foreign key reference to classes table';
COMMENT ON COLUMN fee_structures.session_year_id IS 'Foreign key reference to session_years table';
COMMENT ON COLUMN fee_records.session_year_id IS 'Foreign key reference to session_years table';
COMMENT ON COLUMN fee_records.payment_type_id IS 'Foreign key reference to payment_types table';
COMMENT ON COLUMN fee_records.payment_status_id IS 'Foreign key reference to payment_statuses table';
COMMENT ON COLUMN fee_records.payment_method_id IS 'Foreign key reference to payment_methods table';
COMMENT ON COLUMN fee_payments.payment_method_id IS 'Foreign key reference to payment_methods table';
COMMENT ON COLUMN fee_discounts.session_year_id IS 'Foreign key reference to session_years table';
