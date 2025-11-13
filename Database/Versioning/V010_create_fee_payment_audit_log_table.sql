-- =====================================================
-- Migration: V010 - Create fee_payment_audit_log Table
-- Description: Creates comprehensive audit log table for tracking all payment operations
-- Date: 2025-01-12
-- Dependencies: fee_payments, users
-- =====================================================

-- Drop existing table if exists
DROP TABLE IF EXISTS fee_payment_audit_log CASCADE;

-- Create audit log table
CREATE TABLE fee_payment_audit_log (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    performed_by INTEGER NOT NULL,
    performed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reason TEXT,
    old_values JSONB,
    new_values JSONB,
    
    -- Foreign Keys
    FOREIGN KEY (payment_id) REFERENCES fee_payments(id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_fee_payment_audit_log_payment_id ON fee_payment_audit_log(payment_id);
CREATE INDEX IF NOT EXISTS idx_fee_payment_audit_log_performed_by ON fee_payment_audit_log(performed_by);
CREATE INDEX IF NOT EXISTS idx_fee_payment_audit_log_performed_at ON fee_payment_audit_log(performed_at);
CREATE INDEX IF NOT EXISTS idx_fee_payment_audit_log_action ON fee_payment_audit_log(action);

-- Add comments
COMMENT ON TABLE fee_payment_audit_log IS 'Comprehensive audit log for all fee payment operations';
COMMENT ON COLUMN fee_payment_audit_log.payment_id IS 'Foreign key to fee_payments table';
COMMENT ON COLUMN fee_payment_audit_log.action IS 'Action performed: CREATED, REVERSED, REVERSAL_CREATED, etc.';
COMMENT ON COLUMN fee_payment_audit_log.performed_by IS 'User who performed the action';
COMMENT ON COLUMN fee_payment_audit_log.performed_at IS 'Timestamp when action was performed';
COMMENT ON COLUMN fee_payment_audit_log.reason IS 'Reason for the action (especially for reversals)';
COMMENT ON COLUMN fee_payment_audit_log.old_values IS 'JSON object containing old values before the action';
COMMENT ON COLUMN fee_payment_audit_log.new_values IS 'JSON object containing new values after the action';

-- Add check constraint for action values
ALTER TABLE fee_payment_audit_log 
ADD CONSTRAINT chk_fee_payment_audit_log_action 
CHECK (action IN (
    'CREATED', 
    'UPDATED', 
    'DELETED', 
    'REVERSED_FULL', 
    'REVERSED_PARTIAL', 
    'REVERSAL_CREATED'
));

