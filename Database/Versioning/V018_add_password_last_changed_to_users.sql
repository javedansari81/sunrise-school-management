-- Migration: Add password_last_changed column to users table
-- Purpose: Track when users last changed their password (optional tracking)
-- Date: 2025-11-26

-- Add password_last_changed column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS password_last_changed TIMESTAMP WITH TIME ZONE;

-- Add index for performance (optional, for future queries)
CREATE INDEX IF NOT EXISTS idx_users_password_last_changed 
ON users(password_last_changed);

-- Add comment
COMMENT ON COLUMN users.password_last_changed IS 'Timestamp of last password change (for tracking purposes)';

-- Note: We are NOT adding password_reset_required, password_reset_by, or password_reset_at
-- as per requirements - password changes are optional, not forced

