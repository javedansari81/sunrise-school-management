# 🗄️ Database Deployment Guide - Sunrise School Management System

## 📋 **Complete PostgreSQL Database Setup and Cloud Deployment**

This guide provides comprehensive instructions for deploying the optimized PostgreSQL database for the Sunrise National Public School Management System to Render.com cloud platform.

---

## 🎯 **Prerequisites**

### **Required Tools**
- **PostgreSQL Client** (psql) - Version 12+ recommended
- **Git** - For repository access
- **Render.com Account** - Free tier available
- **Text Editor** - For configuration files

### **Required Knowledge**
- Basic SQL and PostgreSQL concepts
- Command line interface usage
- Cloud deployment fundamentals

---

## 🏗️ **Database Architecture Overview**

### **Complete Schema Structure**
- **21 Core Tables** - Complete tables for full functionality
- **3 Simple Deployment Scripts** - Streamlined deployment process
- **Metadata-Driven Architecture** - 11 reference tables with 57 records
- **Complete School Management** - Students, Teachers, Fees, Leaves, Expenses, Monthly Tracking
- **Automated Deployment** - Python scripts with verification and error handling

### **Key Features**
- **Soft Delete Implementation** - `is_deleted` and `deleted_date` columns
- **Foreign Key Relationships** - Complete referential integrity
- **Performance Indexes** - Optimized for Indian school operations
- **Session Year Management** - Academic year 2024-25 support
- **Role-Based Access** - Admin, Teacher, Student, Staff, Parent

---

## 🌐 **Cloud Deployment on Render.com**

### **Step 1: Create PostgreSQL Database**

1. **Login to Render.com**
   ```
   https://render.com/
   ```

2. **Create New PostgreSQL Database**
   - Click "New +" → "PostgreSQL"
   - **Name**: `sunrise-postgres`
   - **Database Name**: `sunrise_school`
   - **User**: `sunrise_user`
   - **Region**: **Singapore** (nearest to India for optimal performance)
   - **Plan**: Free (or paid for production)

3. **Note Connection Details**
   ```
   Internal Database URL: postgresql://sunrise_user:password@dpg-xxx/sunrise_school
   External Database URL: postgresql://sunrise_user:password@dpg-xxx.singapore-postgres.render.com/sunrise_school
   ```

### **Step 2: Database Configuration**
- **Connection Limit**: 97 (Free tier)
- **Storage**: 1GB (Free tier)
- **Backup**: Automatic daily backups
- **SSL**: Enabled by default

---

## 📊 **Local Development Setup**

### **Step 1: Install PostgreSQL Locally**

**Windows:**
```bash
# Download from https://www.postgresql.org/download/windows/
# Or use Chocolatey
choco install postgresql
```

**macOS:**
```bash
# Using Homebrew
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### **Step 2: Create Local Database**
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE sunrise_school;
CREATE USER sunrise_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE sunrise_school TO sunrise_user;
\q
```

### **Step 3: Set Environment Variables**
```bash
# Create .env file in project root
DATABASE_URL=postgresql://sunrise_user:your_password@localhost:5432/sunrise_school
```

---

## 🚀 **Schema Deployment Process**

### **Step 1: Clone Repository**
```bash
git clone <repository-url>
cd sunrise-school-management
```

### **Step 2: Quick Deployment (Recommended)**

**Connect to Database:**
```bash
# For cloud deployment
psql "postgresql://sunrise_user:password@dpg-xxx.singapore-postgres.render.com/sunrise_school"

# For local development
psql -U sunrise_user -d sunrise_school_db -h localhost
```

**Execute Complete Setup (Single Command):**
```sql
-- Complete database setup with all tables and metadata
\i Database/Init/00_complete_database_setup.sql
\i Database/Init/01_load_metadata.sql
\i Database/Init/02_create_admin_user.sql
```

### **Step 3: Alternative - Manual Step-by-Step Deployment**

**Execute Scripts in Order (if you prefer manual control):**
```sql
-- 1. Core Database Structure (17 tables)
\i Database/Init/00_complete_database_setup.sql

-- 2. Load All Metadata (57 records across 11 tables)
\i Database/Init/01_load_metadata.sql

-- 3. Create Admin User
\i Database/Init/02_create_admin_user.sql

-- 4. Optional: Create Enhanced Views
\i Database/Scripts/create_enhanced_views.sql
```

### **Step 4: Python Deployment Script (Recommended)**

For automated deployment, you can use the Python script:
```bash
# Run the complete automated deployment script
python database_deployment_complete.py
```

This script will:
- Create all 21 database tables (including expenses, vendors, leave_requests, etc.)
- Load all 57 metadata records
- Create the admin user
- Verify the deployment with comprehensive checks
- Provide detailed progress reporting

---

## 📋 **Database Schema Documentation**

### **Complete Tables (21 Essential Tables)**

#### **Metadata Tables (11 tables)**
- `user_types` - Role definitions (Admin, Teacher, Student, Staff, Parent)
- `session_years` - Academic year management (2022-23 to 2026-27)
- `genders` - Gender reference data (Male, Female, Other)
- `classes` - Class structure (Pre-Nursery to Class 12)
- `payment_types` - Payment frequency (Monthly, Quarterly, Annual, One-time)
- `payment_statuses` - Payment state management (Pending, Paid, Partial, Overdue, Cancelled)
- `payment_methods` - Payment channels (Cash, UPI, Bank Transfer, Cheque, Card, Online)
- `leave_types` - Leave categories (Sick, Casual, Emergency, Maternity, Paternity)
- `leave_statuses` - Workflow status tracking (Pending, Approved, Rejected, Cancelled)
- `expense_categories` - Expense classification (Stationery, Maintenance, Utilities, etc.)
- `expense_statuses` - Approval workflow (Pending, Approved, Rejected, Paid)

#### **Core Application Tables (10 tables)**
- `users` - System authentication and user management (email, password, user_type)
- `students` - Student profiles and academic records with guardian information (includes user_id, soft delete support)
- `teachers` - Teacher profiles and employment details (includes user_id, soft delete support)
- `fee_structures` - Fee definitions by class and session
- `fee_records` - Individual student fee tracking and payment status
- `expenses` - School expense management with approval workflow (soft delete support)
- `vendors` - Vendor management for expense tracking (soft delete support)
- `leave_requests` - Leave application system for teachers and students
- `monthly_fee_tracking` - Month-wise fee tracking for students
- `monthly_payment_allocations` - Payment allocation to specific months

**Note:** User names (first_name, last_name) are stored in entity tables (students, teachers) for proper data normalization. See Migration 09/10 documentation for details.

---

## 🔄 **Database Migrations and Schema Evolution**

### **Migration 09: User Data Normalization and Soft Delete (Phase 1)**

**Status:** ✅ Safe, Non-Breaking, Backward Compatible

**Changes:**
- Added `user_id` column to `students` table with foreign key to `users(id)`
- Added soft delete columns (`is_deleted`, `deleted_date`) to `students` table
- Added soft delete columns (`is_deleted`, `deleted_date`) to `vendors` table
- Created 5 performance indexes for soft delete queries
- **Does NOT drop** `first_name`/`last_name` from `users` table (backward compatible)

**How to Apply:**
```bash
psql -U sunrise_user -d sunrise_school_db -f Database/Versioning/09_normalize_user_data_and_soft_delete.sql
```

**Rollback:**
```bash
psql -U sunrise_user -d sunrise_school_db -f Database/Versioning/09_rollback_normalize_user_data_and_soft_delete.sql
```

### **Migration 10: Remove User Name Columns (Phase 2)**

**Status:** ⚠️ Breaking Change, Requires Code Updates

**Prerequisites:**
- ✅ Migration 09 must be applied
- ✅ All backend code must be updated to NOT use `user.first_name` or `user.last_name`
- ✅ Full database backup must be created
- ✅ All testing must be completed

**Changes:**
- Drops `first_name` column from `users` table
- Drops `last_name` column from `users` table
- Creates `users_name_backup` table for safety

**How to Apply:**
```bash
# Create backup first!
pg_dump -U sunrise_user -d sunrise_school_db -F c -f backup_before_migration_10.dump

# Apply migration (includes 10-second countdown)
psql -U sunrise_user -d sunrise_school_db -f Database/Versioning/10_remove_user_name_columns.sql
```

**Rollback:**
```bash
psql -U sunrise_user -d sunrise_school_db -f Database/Versioning/10_rollback_remove_user_name_columns.sql
```

**📖 Detailed Documentation:**
See `Database/Versioning/MIGRATION_09_10_README.md` for complete migration guide including:
- Step-by-step instructions
- Backend code update examples
- Testing checklist
- Troubleshooting guide

---

## 🔧 **Configuration and Optimization**

### **Performance Indexes**
```sql
-- Key performance indexes automatically created:
-- Student queries: idx_students_class_session, idx_students_active
-- Fee queries: idx_fee_records_student_session, idx_monthly_fee_tracking_composite
-- Leave queries: idx_leave_requests_user_session, idx_leave_requests_status
-- Expense queries: idx_expenses_category_status, idx_expenses_session_year
-- Metadata queries: idx_*_active (for all reference tables)
```

### **Constraint Strategy**
- **Inline Constraints (40%)**: Basic validations in CREATE TABLE statements
- **Separate Constraints (60%)**: Complex business logic in `10_constraints.sql`

### **Backup Configuration**
```sql
-- Automated backup command for production
pg_dump "postgresql://user:pass@host/db" > backup_$(date +%Y%m%d_%H%M%S).sql

-- Restore command
psql "postgresql://user:pass@host/db" < backup_file.sql
```

---

## ✅ **Verification Steps**

### **Step 1: Verify Table Creation**
```sql
-- Check table count (should be 21)
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'sunrise' AND table_type = 'BASE TABLE';

-- List all tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'sunrise' AND table_type = 'BASE TABLE'
ORDER BY table_name;
```

### **Step 2: Verify Metadata Population**
```sql
-- Check metadata record counts (should total 57)
SELECT 'user_types' as table_name, COUNT(*) as records FROM user_types
UNION ALL SELECT 'session_years', COUNT(*) FROM session_years
UNION ALL SELECT 'classes', COUNT(*) FROM classes
UNION ALL SELECT 'payment_methods', COUNT(*) FROM payment_methods
UNION ALL SELECT 'leave_types', COUNT(*) FROM leave_types
UNION ALL SELECT 'expense_categories', COUNT(*) FROM expense_categories
ORDER BY table_name;
```

### **Step 3: Verify Admin User Creation**
```sql
-- Check admin user
SELECT email, user_type_id, is_active FROM users WHERE email = 'admin@sunriseschool.edu';

-- Check current session year
SELECT name, is_current FROM session_years WHERE is_current = true;
```

### **Step 4: Test Database Connectivity**
```sql
-- Test basic queries
SELECT 
    s.first_name || ' ' || s.last_name as student_name,
    c.display_name as class_name,
    sy.name as session_year
FROM students s
JOIN classes c ON s.class_id = c.id
JOIN session_years sy ON s.session_year_id = sy.id
LIMIT 5;
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Connection Issues**
```bash
# Test connection
psql "your_database_url" -c "SELECT version();"

# Check SSL requirements
psql "your_database_url?sslmode=require" -c "SELECT 1;"
```

#### **Permission Issues**
```sql
-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sunrise_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sunrise_user;
```

#### **Script Execution Errors**
```sql
-- Check for existing tables before creation
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Drop and recreate if needed (CAUTION: Data loss)
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

### **Performance Issues**
```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan 
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;

-- Analyze table statistics
ANALYZE;
```

---

## 📈 **Monitoring and Maintenance**

### **Database Health Checks**
```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('sunrise_school'));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### **Regular Maintenance**
```sql
-- Update table statistics (run weekly)
ANALYZE;

-- Vacuum tables (run monthly)
VACUUM ANALYZE;

-- Reindex if needed (run quarterly)
REINDEX DATABASE sunrise_school;
```

---

## 🎯 **Production Deployment Checklist**

### **Pre-Deployment**
- [ ] Render.com PostgreSQL database created
- [ ] Connection string obtained and tested
- [ ] All 9 table creation scripts ready
- [ ] Metadata initialization script prepared
- [ ] Backup strategy planned

### **Deployment**
- [ ] Execute table creation scripts in order
- [ ] Load metadata (113 records)
- [ ] Verify table count (57 tables)
- [ ] Test sample queries
- [ ] Create database user for application

### **Post-Deployment**
- [ ] Configure application connection string
- [ ] Test application connectivity
- [ ] Set up monitoring and alerts
- [ ] Schedule regular backups
- [ ] Document access credentials securely

---

## 🔗 **Next Steps**

After successful database deployment:

1. **Backend Deployment**: Follow `BACKEND_DEPLOYMENT_GUIDE.md`
2. **Frontend Deployment**: Follow `FRONTEND_DEPLOYMENT_GUIDE.md`
3. **Integration Testing**: Verify end-to-end functionality
4. **Production Monitoring**: Set up logging and alerts

---

## 🔄 **Backup and Restore Procedures**

### **Automated Backup Strategy**
```bash
# Daily backup script (recommended for production)
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="sunrise_school_backup_$DATE.sql"

pg_dump "$DATABASE_URL" > "$BACKUP_FILE"
gzip "$BACKUP_FILE"

# Upload to cloud storage (AWS S3, Google Cloud, etc.)
# Keep last 30 days of backups
```

### **Manual Backup Commands**
```bash
# Full database backup
pg_dump "postgresql://user:pass@host/db" > full_backup.sql

# Schema-only backup
pg_dump --schema-only "postgresql://user:pass@host/db" > schema_backup.sql

# Data-only backup
pg_dump --data-only "postgresql://user:pass@host/db" > data_backup.sql

# Specific tables backup
pg_dump -t students -t teachers "postgresql://user:pass@host/db" > tables_backup.sql
```

### **Restore Procedures**
```bash
# Full database restore (CAUTION: Overwrites existing data)
psql "postgresql://user:pass@host/db" < full_backup.sql

# Restore specific tables
psql "postgresql://user:pass@host/db" -c "TRUNCATE students CASCADE;"
psql "postgresql://user:pass@host/db" < students_backup.sql
```

---

## 📊 **Performance Tuning**

### **Index Optimization**
```sql
-- Monitor index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE idx_scan > 0
ORDER BY idx_scan DESC;

-- Identify missing indexes
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    seq_tup_read / seq_scan as avg_tuples_per_scan
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC;
```

### **Query Performance Analysis**
```sql
-- Enable query logging (for development)
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log queries > 1s

-- Analyze slow queries
SELECT
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### **Connection Pool Optimization**
```sql
-- Monitor connection usage
SELECT
    state,
    count(*)
FROM pg_stat_activity
GROUP BY state;

-- Recommended connection pool settings for Render.com:
-- Max connections: 97 (Free tier limit)
-- Pool size: 20
-- Max overflow: 0
```

---

## 🔒 **Security Hardening**

### **Database User Permissions**
```sql
-- Create application-specific user with limited permissions
CREATE USER sunrise_app WITH PASSWORD 'secure_app_password';

-- Grant only necessary permissions
GRANT CONNECT ON DATABASE sunrise_school TO sunrise_app;
GRANT USAGE ON SCHEMA public TO sunrise_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO sunrise_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO sunrise_app;

-- Revoke dangerous permissions
REVOKE CREATE ON SCHEMA public FROM sunrise_app;
REVOKE ALL ON pg_user FROM sunrise_app;
```

### **SSL Configuration**
```bash
# Ensure SSL is enforced
DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"

# Verify SSL connection
psql "$DATABASE_URL" -c "SELECT ssl_is_used();"
```

### **Audit Logging**
```sql
-- Enable audit logging for sensitive operations
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50),
    operation VARCHAR(10),
    user_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, old_values)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD));
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, old_values, new_values)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, new_values)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(NEW));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

---

## 📈 **Scaling Considerations**

### **Vertical Scaling (Render.com)**
```bash
# Upgrade database plan for better performance:
# Free: 1GB storage, 97 connections
# Starter ($7/month): 10GB storage, 97 connections
# Standard ($20/month): 100GB storage, 97 connections
# Pro ($65/month): 512GB storage, 500 connections
```

### **Horizontal Scaling Strategies**
```sql
-- Read replicas for reporting (future consideration)
-- Table partitioning for large datasets
-- Connection pooling optimization

-- Example: Partition fee_payments by session_year
CREATE TABLE fee_payments_2024_25 PARTITION OF fee_payments
FOR VALUES FROM ('2024-04-01') TO ('2025-03-31');

CREATE TABLE fee_payments_2025_26 PARTITION OF fee_payments
FOR VALUES FROM ('2025-04-01') TO ('2026-03-31');
```

### **Data Archiving Strategy**
```sql
-- Archive old session data (keep last 3 years active)
CREATE TABLE archived_students AS
SELECT * FROM students
WHERE session_year_id IN (
    SELECT id FROM session_years
    WHERE start_date < '2021-04-01'
);

-- Move old fee records to archive
CREATE TABLE archived_fee_records AS
SELECT * FROM fee_records
WHERE session_year_id IN (
    SELECT id FROM session_years
    WHERE start_date < '2021-04-01'
);
```

---

## 🎯 **Production Readiness Checklist**

### **Database Configuration**
- [ ] PostgreSQL 12+ deployed on Render.com Singapore region
- [ ] SSL connections enforced
- [ ] Connection pooling configured
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting set up

### **Schema Deployment**
- [ ] All 9 table creation scripts executed successfully
- [ ] 113 metadata records loaded across 13 tables
- [ ] Sample data loaded for testing (optional)
- [ ] Enhanced views created for fee management
- [ ] All constraints and indexes applied

### **Security**
- [ ] Database user permissions restricted
- [ ] Sensitive data encrypted
- [ ] Audit logging enabled for critical tables
- [ ] Connection strings secured
- [ ] Regular security updates planned

### **Performance**
- [ ] Query performance analyzed
- [ ] Indexes optimized for common queries
- [ ] Connection pool tuned for workload
- [ ] Slow query logging enabled
- [ ] Performance monitoring implemented

### **Backup & Recovery**
- [ ] Automated daily backups configured
- [ ] Backup retention policy defined
- [ ] Restore procedures tested
- [ ] Disaster recovery plan documented
- [ ] Point-in-time recovery capability verified

---

**Database deployment completed successfully!** 🎉
**Production-ready PostgreSQL database with 57 optimized tables, comprehensive metadata, and enhanced security measures.**
**Ready for backend service connection and application deployment.**
