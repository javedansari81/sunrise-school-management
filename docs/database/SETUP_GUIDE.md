# 🗄️ Sunrise School Database Setup Guide

Complete database management system for the Sunrise School Management project.

## 📁 Folder Structure Overview

```
Database/
├── 📖 README.md                    # Main documentation
├── 🚀 SETUP_GUIDE.md              # This setup guide
├── 📊 Tables/                      # DDL scripts (table definitions)
│   ├── 01_enums.sql               # ENUM type definitions
│   ├── 02_users.sql               # User authentication tables
│   ├── 03_students.sql            # Student management tables
│   ├── 04_teachers.sql            # Teacher management tables
│   ├── 05_fees.sql                # Fee management tables
│   ├── 06_attendance.sql          # Attendance tracking tables
│   ├── 07_leaves.sql              # Leave management tables
│   ├── 08_expenses.sql            # Expense management tables
│   ├── 09_indexes.sql             # Performance indexes
│   └── 10_constraints.sql         # Foreign keys & constraints
├── 💾 DataLoads/                  # Sample data insertion scripts
│   ├── 01_initial_users.sql      # Admin users & permissions
│   ├── 02_sample_students.sql     # Sample student data
│   ├── 03_sample_teachers.sql     # Sample teacher data
│   ├── 04_sample_fees.sql         # Sample fee records
│   └── 05_sample_attendance.sql   # Sample attendance data
├── 🔄 Versioning/                 # Database migration scripts
│   ├── enum_to_varchar_migration.sql      # ENUM to VARCHAR conversion
│   └── v1.0_to_v1.1_session_year_update.sql  # Version upgrades
├── 🎯 Init/                       # Complete setup scripts
│   ├── 00_drop_all.sql           # Clean database (DANGER!)
│   ├── 01_create_database.sql     # Create complete schema
│   ├── 02_load_initial_data.sql   # Load essential data
│   └── 99_complete_setup.sql      # One-click complete setup
└── 📚 Legacy/                     # Original files (reference only)
    ├── README.md                  # Legacy documentation
    └── original_create_tables.sql # Original table script
```

## 🚀 Quick Start (Recommended)

### Option 1: One-Click Setup
```bash
# Complete setup in one command
psql -d your_database -f Init/99_complete_setup.sql
```

### Option 2: Step-by-Step Setup
```bash
# 1. Clean existing database (CAUTION: Deletes all data!)
psql -d your_database -f Init/00_drop_all.sql

# 2. Create complete schema
psql -d your_database -f Init/01_create_database.sql

# 3. Load initial data
psql -d your_database -f Init/02_load_initial_data.sql
```

## 🔐 Default Login Credentials

After setup, login with:
- **Email**: `admin@sunriseschool.edu`
- **Password**: `admin123`
- **Role**: Admin (full system access)

## 📊 What Gets Created

### Database Tables (25+ tables)
- **Authentication**: Users, sessions, permissions
- **Student Management**: Students, academic history, documents
- **Teacher Management**: Teachers, qualifications, assignments
- **Fee Management**: Structures, records, payments, discounts
- **Attendance**: Student/teacher attendance, summaries
- **Leave Management**: Requests, balances, policies
- **Expense Management**: Expenses, vendors, purchase orders

### Sample Data
- **15 Students** across different classes (PG to Class 8)
- **10 Teachers** with various subjects and qualifications
- **Complete Fee Structure** for 2024-25 session
- **Fee Records** with payment tracking
- **Attendance Data** for testing
- **Admin User** ready for immediate use

### Performance Features
- **50+ Indexes** for optimal query performance
- **Foreign Key Constraints** for data integrity
- **Check Constraints** for data validation
- **Views** for common queries
- **Functions** for calculations

## 🔧 Advanced Usage

### Individual Component Setup
```bash
# Create specific tables only
psql -d your_database -f Tables/02_users.sql
psql -d your_database -f Tables/05_fees.sql

# Load specific data only
psql -d your_database -f DataLoads/01_initial_users.sql
psql -d your_database -f DataLoads/04_sample_fees.sql
```

### Database Migration
```bash
# Apply ENUM to VARCHAR migration (for SQLAlchemy compatibility)
psql -d your_database -f Versioning/enum_to_varchar_migration.sql

# Apply version updates
psql -d your_database -f Versioning/v1.0_to_v1.1_session_year_update.sql
```

### Load Complete Sample Data
```bash
# Load all sample data for comprehensive testing
psql -d your_database -f DataLoads/01_initial_users.sql
psql -d your_database -f DataLoads/02_sample_students.sql
psql -d your_database -f DataLoads/03_sample_teachers.sql
psql -d your_database -f DataLoads/04_sample_fees.sql
psql -d your_database -f DataLoads/05_sample_attendance.sql
```

## ✅ Verification

After setup, verify with these SQL commands:

```sql
-- Check tables created
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Verify sample data
SELECT COUNT(*) as students FROM students;
SELECT COUNT(*) as teachers FROM teachers;
SELECT COUNT(*) as fee_records FROM fee_records;
SELECT COUNT(*) as users FROM users;

-- Check admin user
SELECT email, first_name, role FROM users WHERE role = 'admin';

-- Verify version
SELECT * FROM schema_versions ORDER BY applied_at DESC;
```

## 🛠️ Troubleshooting

### Common Issues
1. **Permission Denied**: Ensure database owner/superuser privileges
2. **Table Already Exists**: Use `00_drop_all.sql` to clean before fresh install
3. **Foreign Key Errors**: Run scripts in numbered order
4. **ENUM Errors**: Use `enum_to_varchar_migration.sql` for compatibility

### Reset Database
```bash
# Complete reset (DANGER: Deletes all data!)
psql -d your_database -f Init/00_drop_all.sql
psql -d your_database -f Init/99_complete_setup.sql
```

## 🎯 Integration with FastAPI

This database structure is designed to work seamlessly with:
- **SQLAlchemy ORM** (VARCHAR instead of ENUM for compatibility)
- **FastAPI** backend application
- **Pydantic** models for validation
- **Alembic** for future migrations

## 📈 Performance Optimized

- **Indexed columns** for fast queries
- **Composite indexes** for complex searches
- **Partial indexes** for filtered queries
- **Text search indexes** for name searches
- **Optimized data types** for storage efficiency

## 🔒 Security Features

- **Hashed passwords** using bcrypt
- **Role-based permissions** system
- **Audit logging** capabilities
- **Session management** tables
- **Email verification** system

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Ensure PostgreSQL version compatibility
4. Review error logs for specific issues

---

**Ready to get started?** Run the one-click setup command and you'll have a fully functional school management database in seconds! 🎉
