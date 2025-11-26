-- =====================================================
-- Table: users
-- Description: Stores user authentication and basic information
-- Dependencies: user_types
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS users CASCADE;

-- Create table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_type_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_date TIMESTAMP WITH TIME ZONE,
    password_last_changed TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_type_id) REFERENCES user_types(id)
);

-- Create indexes
-- Note: Using partial unique index instead of UNIQUE constraint to support soft delete
CREATE UNIQUE INDEX IF NOT EXISTS users_email_active_unique
ON users (email)
WHERE (is_deleted = FALSE OR is_deleted IS NULL);

CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type_id);
CREATE INDEX IF NOT EXISTS idx_users_is_deleted ON users(is_deleted);
CREATE INDEX IF NOT EXISTS idx_users_password_last_changed ON users(password_last_changed);

-- Add comments
COMMENT ON TABLE users IS 'User authentication and basic information';
COMMENT ON COLUMN users.id IS 'Primary key - auto-increment';
COMMENT ON COLUMN users.email IS 'Unique email for login (unique only for non-deleted users)';
COMMENT ON COLUMN users.password IS 'Hashed password';
COMMENT ON COLUMN users.user_type_id IS 'Foreign key to user_types table';
COMMENT ON COLUMN users.is_active IS 'Whether user account is active (can be temporarily disabled)';
COMMENT ON COLUMN users.is_deleted IS 'Soft delete flag - marks user as permanently deleted';
COMMENT ON COLUMN users.deleted_date IS 'Timestamp when user was soft deleted';
COMMENT ON COLUMN users.password_last_changed IS 'Timestamp of last password change (for tracking purposes)';

