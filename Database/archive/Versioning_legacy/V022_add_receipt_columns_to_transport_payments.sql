-- =====================================================
-- Migration: V022 - Add Receipt Columns to transport_payments
-- Description: Adds columns to support receipt PDF generation and Cloudinary storage for transport payments
-- Date: 2025-01-14
-- Dependencies: transport_payments
-- Phase: Phase 1 - Receipt Generation and Storage
-- =====================================================

-- Add receipt columns to transport_payments table
ALTER TABLE transport_payments 
ADD COLUMN IF NOT EXISTS receipt_url TEXT,
ADD COLUMN IF NOT EXISTS receipt_cloudinary_public_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS receipt_generated_at TIMESTAMP WITH TIME ZONE;

-- Add comments for new columns
COMMENT ON COLUMN transport_payments.receipt_url IS 'Cloudinary URL for the receipt PDF';
COMMENT ON COLUMN transport_payments.receipt_cloudinary_public_id IS 'Cloudinary public ID for receipt management';
COMMENT ON COLUMN transport_payments.receipt_generated_at IS 'Timestamp when receipt was generated';

-- Note: receipt_number column already exists in the base table
-- This migration only adds the Cloudinary-related columns for Phase 1 implementation

