-- =====================================================
-- Migration: V021 - Add Receipt Columns to fee_payments
-- Description: Adds columns to support receipt PDF generation and Cloudinary storage
-- Date: 2025-01-14
-- Dependencies: fee_payments
-- Phase: Phase 1 - Receipt Generation and Storage
-- =====================================================

-- Add receipt columns to fee_payments table
ALTER TABLE fee_payments 
ADD COLUMN IF NOT EXISTS receipt_cloudinary_url TEXT,
ADD COLUMN IF NOT EXISTS receipt_cloudinary_id VARCHAR(255);

-- Add comments for new columns
COMMENT ON COLUMN fee_payments.receipt_cloudinary_url IS 'Cloudinary URL for the receipt PDF';
COMMENT ON COLUMN fee_payments.receipt_cloudinary_id IS 'Cloudinary public ID for receipt management';

-- Create index for faster receipt lookups
CREATE INDEX IF NOT EXISTS idx_fee_payments_receipt_cloudinary_id ON fee_payments(receipt_cloudinary_id);

-- Verify the changes
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'fee_payments' 
        AND column_name = 'receipt_cloudinary_url'
    ) THEN
        RAISE NOTICE 'Migration V021 completed successfully: receipt_cloudinary_url column added';
    ELSE
        RAISE EXCEPTION 'Migration V021 failed: receipt_cloudinary_url column not found';
    END IF;

    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'fee_payments' 
        AND column_name = 'receipt_cloudinary_id'
    ) THEN
        RAISE NOTICE 'Migration V021 completed successfully: receipt_cloudinary_id column added';
    ELSE
        RAISE EXCEPTION 'Migration V021 failed: receipt_cloudinary_id column not found';
    END IF;
END $$;

