# Database Management Structure

This folder contains all database-related scripts and documentation for the Sunrise School Management System.

## Folder Structure

### 📁 Tables/
Contains DDL (Data Definition Language) scripts for creating database tables and schemas.
- `01_enums.sql` - PostgreSQL ENUM type definitions
- `02_users.sql` - Users and authentication tables
- `03_students.sql` - Student management tables
- `04_teachers.sql` - Teacher management tables
- `05_fees.sql` - Fee management tables
- `06_attendance.sql` - Attendance tracking tables
- `07_leaves.sql` - Leave management tables
- `08_expenses.sql` - Expense tracking tables
- `09_indexes.sql` - Database indexes for performance
- `10_constraints.sql` - Foreign key constraints and relationships

### 📁 DataLoads/
Contains DML (Data Manipulation Language) scripts for inserting and updating data.
- `01_initial_users.sql` - Default admin and user accounts
- `02_sample_students.sql` - Sample student data
- `03_sample_teachers.sql` - Sample teacher data
- `04_sample_fees.sql` - Sample fee records
- `05_sample_attendance.sql` - Sample attendance data

### 📁 Versioning/
Contains ALTER TABLE scripts for database schema changes and migrations.
- `v1.0_to_v1.1.sql` - Migration scripts between versions
- `v1.1_to_v1.2.sql` - Version upgrade scripts
- `enum_to_varchar_migration.sql` - ENUM to VARCHAR conversion

### 📁 Init/
Contains complete database initialization scripts.
- `00_drop_all.sql` - Clean database (drop all tables)
- `01_create_database.sql` - Complete database creation
- `02_load_initial_data.sql` - Load essential initial data
- `99_complete_setup.sql` - Full database setup script

## Usage Instructions

### 🚀 Quick Setup (Recommended)
```bash
# One-command complete setup
psql -d your_database -f Init/99_complete_setup.sql
```

### 📋 Step-by-Step Setup
```bash
# 1. Clean existing database (CAUTION: Deletes all data)
psql -d your_database -f Init/00_drop_all.sql

# 2. Create complete database schema
psql -d your_database -f Init/01_create_database.sql

# 3. Load initial data
psql -d your_database -f Init/02_load_initial_data.sql
```

### 🔧 Individual Component Management
```bash
# Create specific tables
psql -d your_database -f Tables/02_users.sql
psql -d your_database -f Tables/03_students.sql
psql -d your_database -f Tables/05_fees.sql

# Load specific data
psql -d your_database -f DataLoads/01_initial_users.sql
psql -d your_database -f DataLoads/02_sample_students.sql
psql -d your_database -f DataLoads/04_sample_fees.sql
```

### 🔄 Database Migration
```bash
# Apply ENUM to VARCHAR migration
psql -d your_database -f Versioning/enum_to_varchar_migration.sql

# Apply version upgrades
psql -d your_database -f Versioning/v1.0_to_v1.1_session_year_update.sql
```

### 📊 Load Complete Sample Data
```bash
# Load all sample data for testing
psql -d your_database -f DataLoads/01_initial_users.sql
psql -d your_database -f DataLoads/02_sample_students.sql
psql -d your_database -f DataLoads/03_sample_teachers.sql
psql -d your_database -f DataLoads/04_sample_fees.sql
psql -d your_database -f DataLoads/05_sample_attendance.sql
```

## Database Connection
- **Host**: As per your environment configuration
- **Database**: sunrise_school_db
- **User**: As per your environment configuration
- **Port**: 5432 (default PostgreSQL port)

## 🔐 Default Login Credentials
After running the setup scripts, you can login with:
- **Email**: `admin@sunriseschool.edu`
- **Password**: `admin123`
- **Role**: Admin (full access)

## 📈 Database Statistics (After Full Setup)
- **Tables**: 25+ core tables
- **Sample Students**: 15 students across different classes
- **Sample Teachers**: 10 teachers with different subjects
- **Fee Records**: Complete fee structure and payment tracking
- **Attendance**: Sample attendance data for testing
- **Session Years**: Support for 2022-23 to 2026-27

## 🛠️ Troubleshooting

### Common Issues
1. **Permission Denied**: Ensure you have database owner/superuser privileges
2. **Table Already Exists**: Use `00_drop_all.sql` to clean before fresh install
3. **Foreign Key Errors**: Run scripts in the correct order (numbered sequence)
4. **ENUM Errors**: Use `enum_to_varchar_migration.sql` for compatibility

### Verification Commands
```sql
-- Check all tables are created
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Verify sample data
SELECT COUNT(*) as student_count FROM students;
SELECT COUNT(*) as fee_records FROM fee_records;
SELECT COUNT(*) as users FROM users;

-- Check version
SELECT * FROM schema_versions ORDER BY applied_at DESC;
```

## 📝 Notes
- All scripts are PostgreSQL compatible
- Scripts are numbered for execution order
- Always backup your database before running migration scripts
- Test scripts in development environment first
- Use `99_complete_setup.sql` for quickest setup
- Individual scripts allow granular control
