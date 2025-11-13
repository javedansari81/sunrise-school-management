-- =====================================================
-- Data Load: reversal_reasons
-- Description: Insert default reversal reasons
-- =====================================================

INSERT INTO reversal_reasons (id, name, description, is_active) VALUES
(1, 'INCORRECT_AMOUNT', 'Incorrect Amount Entered', TRUE),
(2, 'DUPLICATE_PAYMENT', 'Duplicate Payment', TRUE),
(3, 'WRONG_STUDENT', 'Wrong Student Account', TRUE),
(4, 'WRONG_PAYMENT_METHOD', 'Wrong Payment Method', TRUE),
(5, 'PROCESSING_ERROR', 'Payment Processing Error', TRUE),
(6, 'STUDENT_REQUEST', 'Student Request/Refund', TRUE),
(7, 'ADMINISTRATIVE_CORRECTION', 'Administrative Correction', TRUE),
(8, 'OTHER', 'Other', TRUE)
ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = CURRENT_TIMESTAMP;

-- Reset sequence to ensure next auto-generated ID is correct
SELECT setval('reversal_reasons_id_seq', (SELECT MAX(id) FROM reversal_reasons));

