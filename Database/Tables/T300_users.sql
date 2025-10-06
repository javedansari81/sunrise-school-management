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
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    user_type_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_type_id) REFERENCES user_types(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type_id);

-- Add comments
COMMENT ON TABLE users IS 'User authentication and basic information';
COMMENT ON COLUMN users.id IS 'Primary key - auto-increment';
COMMENT ON COLUMN users.email IS 'Unique email for login';
COMMENT ON COLUMN users.password IS 'Hashed password';
COMMENT ON COLUMN users.user_type_id IS 'Foreign key to user_types table';

