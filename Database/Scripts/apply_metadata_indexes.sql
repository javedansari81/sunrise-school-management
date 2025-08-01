-- =====================================================
-- Apply Metadata Performance Indexes
-- Run this script to improve configuration endpoint performance
-- =====================================================

-- Metadata tables performance indexes for configuration endpoint optimization
CREATE INDEX IF NOT EXISTS idx_user_types_active_id ON user_types(is_active, id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_session_years_active_id ON session_years(is_active, id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_genders_active_id ON genders(is_active, id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_classes_active_id ON classes(is_active, id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_payment_types_active_id ON payment_types(is_active, id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_payment_statuses_active_id ON payment_statuses(is_active, id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_payment_methods_active_id ON payment_methods(is_active, id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_leave_types_active_id ON leave_types(is_active, id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_leave_statuses_active_id ON leave_statuses(is_active, id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_expense_categories_active_id ON expense_categories(is_active, id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_expense_statuses_active_id ON expense_statuses(is_active, id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_employment_statuses_active_id ON employment_statuses(is_active, id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_qualifications_active_id ON qualifications(is_active, id) WHERE is_active = true;

-- Verify indexes were created
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE indexname LIKE 'idx_%_active_id'
ORDER BY tablename, indexname;

-- Show index usage statistics (run after some time to see usage)
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes 
WHERE indexname LIKE 'idx_%_active_id'
ORDER BY idx_scan DESC;
