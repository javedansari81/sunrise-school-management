# Sunrise School Management System - Database

Complete database schema and scripts for the Sunrise School Management System.

**Version:** 2.1 (Refactored Structure)
**Last Updated:** 2025-10-06

---

## 📁 Folder Structure

```
Database/
├── Schema/                         # Schema initialization
│   └── 00_create_schema.sql       # Creates 'sunrise' schema and initial setup
│
├── Tables/                         # Individual table definitions
│   ├── T100_user_types.sql        # Metadata tables (T100-T220)
│   ├── T110_session_years.sql
│   ├── ...
│   ├── T300_users.sql             # Core tables (T300-T320)
│   ├── T310_students.sql
│   ├── T320_teachers.sql
│   ├── T400_fee_structures.sql    # Fee management (T400-T430)
│   ├── ...
│   ├── T500_expenses.sql          # Expense management (T500-T510)
│   ├── T510_vendors.sql
│   └── T600_leave_requests.sql    # Leave management (T600)
│
├── Functions/                      # Database functions
│   ├── F100_calculate_age.sql
│   ├── F110_get_academic_year.sql
│   └── F120_calculate_fee_balance.sql
│
├── Views/                          # Database views
│   ├── V100_student_summary.sql
│   ├── V110_teacher_summary.sql
│   ├── V120_fee_collection_summary.sql
│   └── V130_enhanced_student_fee_status.sql
│
├── DataLoads/                      # Data loading scripts
│   └── (metadata loading scripts)
│
├── Init/                           # Legacy scripts (kept for compatibility)
│   ├── 01_load_metadata.sql       # Metadata data
│   └── 02_create_admin_user.sql   # Admin user creation
│
├── Scripts/                        # Legacy scripts (deprecated)
│   └── (old view scripts)
│
├── deploy_database.sql             # ⭐ Master deployment script
├── README.md                       # This file
└── (documentation files)
```

---

## 🚀 Quick Start - Fresh Database Deployment

### Prerequisites
- PostgreSQL 12+ installed
- Database `sunrise_school_db` created
- User `sunrise_user` created with proper permissions

### Option 1: One-Command Deployment (Recommended)

```bash
psql -U sunrise_user -d sunrise_school_db -f Database/deploy_database.sql
```

**That's it!** The master script will deploy everything in the correct order.

### Option 2: Manual Step-by-Step Deployment

Execute scripts in this exact order:

```bash
# Step 1: Schema initialization
psql -U sunrise_user -d sunrise_school_db -f Database/Schema/00_create_schema.sql

# Step 2: Create metadata tables (T100-T220)
psql -U sunrise_user -d sunrise_school_db -f Database/Tables/T100_user_types.sql
psql -U sunrise_user -d sunrise_school_db -f Database/Tables/T110_session_years.sql
# ... (continue with all T1xx tables)

# Step 3: Create core tables (T300-T320)
psql -U sunrise_user -d sunrise_school_db -f Database/Tables/T300_users.sql
psql -U sunrise_user -d sunrise_school_db -f Database/Tables/T310_students.sql
psql -U sunrise_user -d sunrise_school_db -f Database/Tables/T320_teachers.sql

# Step 4: Create fee management tables (T400-T430)
# Step 5: Create expense management tables (T500-T510)
# Step 6: Create leave management tables (T600)
# Step 7: Create functions (F100-F120)
# Step 8: Create views (V100-V130)

# Step 9: Load metadata
psql -U sunrise_user -d sunrise_school_db -f Database/Init/01_load_metadata.sql

# Step 10: Create admin user
psql -U sunrise_user -d sunrise_school_db -f Database/Init/02_create_admin_user.sql
```

---

## 📊 Database Schema Overview

### File Naming Convention

All database objects follow a standardized naming pattern:

- **Tables:** `T<version>_<table_name>.sql` (e.g., T100_user_types.sql)
- **Views:** `V<version>_<view_name>.sql` (e.g., V100_student_summary.sql)
- **Functions:** `F<version>_<function_name>.sql` (e.g., F100_calculate_age.sql)

**Version Numbering:**
- Start at 100 for the first object of each type
- Increment by 10 for each subsequent object (100, 110, 120, etc.)
- Allows inserting new objects between existing ones (e.g., 105, 115)
- Version numbers are independent for each object type

### Tables Created: 23

#### Metadata Tables (T100-T220)
| File | Table | Description |
|------|-------|-------------|
| T100 | user_types | User role definitions |
| T110 | session_years | Academic years |
| T120 | genders | Gender options |
| T130 | classes | Class definitions (Pre-Nursery to Class 12) |
| T140 | payment_types | Payment type options |
| T150 | payment_statuses | Payment status options with color codes |
| T160 | payment_methods | Payment method options |
| T170 | leave_types | Leave type definitions |
| T180 | leave_statuses | Leave status options with color codes |
| T190 | expense_categories | Expense category definitions |
| T200 | expense_statuses | Expense status options with color codes |
| T210 | employment_statuses | Employment status options |
| T220 | qualifications | Qualification options |

#### Core Tables (T300-T320)
| File | Table | Description |
|------|-------|-------------|
| T300 | users | User authentication |
| T310 | students | Student profiles |
| T320 | teachers | Teacher profiles |

#### Fee Management (T400-T430)
| File | Table | Description |
|------|-------|-------------|
| T400 | fee_structures | Fee structure definitions |
| T410 | fee_records | Student fee records |
| T420 | monthly_fee_tracking | Monthly fee breakdown |
| T430 | monthly_payment_allocations | Payment allocations |

#### Expense Management (T500-T510)
| File | Table | Description |
|------|-------|-------------|
| T500 | expenses | Expense records |
| T510 | vendors | Vendor information |

#### Leave Management (T600)
| File | Table | Description |
|------|-------|-------------|
| T600 | leave_requests | Leave request records |

### Functions Created: 4

| File | Function | Description |
|------|----------|-------------|
| F100 | calculate_age | Calculates age from date of birth |
| F110 | get_academic_year | Returns academic year for a given date |
| F120 | calculate_fee_balance | Trigger function to calculate fee balance |
| F130 | enable_monthly_tracking_complete | Creates fee records and 12 monthly tracking records |

### Views Created: 4

| File | View | Description |
|------|------|-------------|
| V100 | student_summary | Student information summary |
| V110 | teacher_summary | Teacher information summary |
| V120 | fee_collection_summary | Fee collection statistics |
| V130 | enhanced_student_fee_status | Enhanced fee tracking |

### Indexes Created: 26+
Optimized indexes for all major query patterns

---

## 📚 Detailed Documentation

### Schema Folder

#### `00_create_schema.sql`
**Purpose:** Initializes the database schema and environment

**Creates:**
- `sunrise` schema
- Search path configuration
- pgcrypto extension
- Version tracking table
- Permission grants

**Execution Time:** <1 second

---

### Tables Folder

Each table is in its own file with:
- DROP IF EXISTS statement
- Complete table definition
- All indexes for that table
- Foreign key constraints
- Check constraints
- Comments and documentation

**Execution Order:**
1. **Metadata Tables (T100-T220)** - No dependencies
2. **Core Tables (T300-T320)** - Depend on metadata tables
3. **Fee Management (T400-T430)** - Depend on core tables
4. **Expense Management (T500-T510)** - Depend on core tables
5. **Leave Management (T600)** - Depend on core tables

**Features:**
- Self-contained and independently executable
- Metadata-driven architecture
- Soft delete support (is_deleted, deleted_date)
- Foreign key relationships
- Check constraints
- Default values
- Timestamps (created_at, updated_at)
- Comprehensive indexing

---

### Functions Folder

#### `F100_calculate_age.sql`
**Purpose:** Calculates age from date of birth
**Parameters:** birth_date (DATE)
**Returns:** INTEGER (age in years)

#### `F110_get_academic_year.sql`
**Purpose:** Returns academic year for a given date (April to March)
**Parameters:** input_date (DATE, default CURRENT_DATE)
**Returns:** VARCHAR (format: YYYY-YY)

#### `F120_calculate_fee_balance.sql`
**Purpose:** Trigger function to auto-calculate balance_amount
**Trigger:** Fires on INSERT/UPDATE of fee_records table
**Action:** Sets balance_amount = total_amount - paid_amount

---

### Views Folder

#### `V100_student_summary.sql`
**Purpose:** Student information with metadata relationships
**Includes:** Full name, class, session, gender, parent info, age

#### `V110_teacher_summary.sql`
**Purpose:** Teacher information with metadata relationships
**Includes:** Full name, position, department, qualification, employment status

#### `V120_fee_collection_summary.sql`
**Purpose:** Fee collection statistics
**Groups By:** Session year, class, payment type, payment status
**Includes:** Total students, fees, collected amount, pending amount, collection %

#### `V130_enhanced_student_fee_status.sql`
**Purpose:** Enhanced fee tracking combining annual and monthly data
**Includes:** Annual fee records, monthly tracking stats, collection %, payment status

---

### Init Folder (Legacy)

#### `01_load_metadata.sql`
**Purpose:** Loads all 78 metadata records into reference tables

**Loads:**
- 5 User types
- 5 Session years (2022-23 to 2026-27)
- 3 Genders
- 16 Classes (Pre-Nursery to Class 12)
- 4 Payment types
- 5 Payment statuses (with color codes)
- 6 Payment methods (with reference requirements)
- 5 Leave types
- 4 Leave statuses (with color codes)
- 6 Expense categories
- 4 Expense statuses (with color codes)
- 6 Employment statuses
- 9 Qualifications

**Features:**
- ON CONFLICT DO UPDATE for idempotency
- Color codes for UI display
- Proper descriptions
- Active/inactive flags

#### `02_create_admin_user.sql`
**Purpose:** Creates default admin user for initial login

**Default Credentials:**
- Email: admin@sunrise.com
- Password: admin123

**⚠️ IMPORTANT:** Change default password after first login!

---

## 🔧 Database Features

### 1. Modular Structure
- **Self-Contained Files:** Each database object in its own file
- **Independent Execution:** Files can be run individually for updates
- **Version Control Friendly:** Easy to track changes per object
- **Standardized Naming:** Consistent naming convention across all objects

### 2. Metadata-Driven Architecture
All reference data is stored in metadata tables with foreign key relationships:
- Easy updates without code changes
- Consistent data across the application
- UI-driven configuration
- Color codes for status display

### 3. Soft Delete Support
Tables support soft delete functionality:
- `is_deleted` - Boolean flag
- `deleted_date` - Timestamp of deletion
- Indexes for efficient queries
- Views automatically filter deleted records

### 4. Performance Optimization
- 26+ indexes for common query patterns
- Partial indexes for active records
- Composite indexes for complex queries
- Foreign key indexes for joins

### 5. Data Integrity
- Foreign key constraints
- Check constraints
- NOT NULL constraints
- Unique constraints
- Default values

### 6. Audit Trail
- `created_at` - Record creation timestamp
- `updated_at` - Last update timestamp
- Automatic timestamp updates via triggers

---

## 📈 Schema Version

**Current Version:** 2.1 (Refactored Structure)

**Features:**
- Modular file structure with standardized naming
- Each database object in separate file
- Master deployment script for easy deployment
- Optimized schema with inline constraints
- Enhanced monthly fee tracking system
- Leave request applicant tracking
- Soft delete support
- Comprehensive indexing

---

## 🔄 Migration History

### Version 2.1 (2025-10-06) - Refactored Structure
- ✅ Refactored database structure into modular files
- ✅ Implemented standardized naming convention (T/V/F + version number)
- ✅ Created separate folders for Tables, Views, Functions
- ✅ Created master deployment script (deploy_database.sql)
- ✅ Each table in its own file with all related indexes and constraints
- ✅ Each view in its own file
- ✅ Each function in its own file
- ✅ Improved documentation and deployment process

### Version 2.0
- Added enhanced monthly fee tracking
- Added soft delete support
- Added employment statuses and qualifications
- Merged versioning scripts into Init folder

### Version 1.0
- Initial schema with core tables
- Basic metadata structure

---

## 🧪 Testing

### Verify Installation

```sql
-- Check schema
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'sunrise';

-- Check version
SELECT * FROM schema_versions ORDER BY applied_at DESC LIMIT 1;

-- Check table count (should be 23)
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'sunrise' AND table_type = 'BASE TABLE';

-- Check metadata records (should be 78)
SELECT
    (SELECT COUNT(*) FROM user_types) +
    (SELECT COUNT(*) FROM session_years) +
    (SELECT COUNT(*) FROM genders) +
    (SELECT COUNT(*) FROM classes) +
    (SELECT COUNT(*) FROM payment_types) +
    (SELECT COUNT(*) FROM payment_statuses) +
    (SELECT COUNT(*) FROM payment_methods) +
    (SELECT COUNT(*) FROM leave_types) +
    (SELECT COUNT(*) FROM leave_statuses) +
    (SELECT COUNT(*) FROM expense_categories) +
    (SELECT COUNT(*) FROM expense_statuses) +
    (SELECT COUNT(*) FROM employment_statuses) +
    (SELECT COUNT(*) FROM qualifications) AS total_metadata;

-- Check functions (should be 3)
SELECT COUNT(*) FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'sunrise';

-- Check views (should be 4)
SELECT COUNT(*) FROM pg_views WHERE schemaname = 'sunrise';

-- Check indexes (should be 26+)
SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'sunrise';

-- List all tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'sunrise' AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- List all views
SELECT table_name FROM information_schema.views
WHERE table_schema = 'sunrise'
ORDER BY table_name;

-- List all functions
SELECT routine_name FROM information_schema.routines
WHERE routine_schema = 'sunrise'
ORDER BY routine_name;
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue:** "relation already exists"
- **Solution:** Each file has DROP IF EXISTS statement. Run the specific file again, or drop the entire schema and redeploy.

**Issue:** "permission denied"
- **Solution:** Ensure user has proper permissions:
  ```sql
  GRANT ALL ON DATABASE sunrise_school_db TO sunrise_user;
  GRANT USAGE ON SCHEMA sunrise TO sunrise_user;
  GRANT ALL ON ALL TABLES IN SCHEMA sunrise TO sunrise_user;
  ```

**Issue:** "foreign key constraint violation"
- **Solution:** Ensure scripts are run in correct order. Use `deploy_database.sql` for automatic ordering.

**Issue:** "schema sunrise does not exist"
- **Solution:** Run `Schema/00_create_schema.sql` first before any other scripts.

**Issue:** Views return no data
- **Solution:** Ensure metadata is loaded (`Init/01_load_metadata.sql`) and tables have data.

**Issue:** Function not found
- **Solution:** Ensure functions are created before views that use them.

---

## � Updating Individual Objects

One of the key benefits of the refactored structure is the ability to update individual objects:

### Update a Single Table
```bash
# Update just the students table
psql -U sunrise_user -d sunrise_school_db -f Database/Tables/T310_students.sql
```

### Update a Single View
```bash
# Update just the student summary view
psql -U sunrise_user -d sunrise_school_db -f Database/Views/V100_student_summary.sql
```

### Update a Single Function
```bash
# Update just the calculate_age function
psql -U sunrise_user -d sunrise_school_db -f Database/Functions/F100_calculate_age.sql
```

### Add a New Table
1. Create new file with next available version number (e.g., T610_new_table.sql)
2. Follow the same structure as existing table files
3. Run the file: `psql -U sunrise_user -d sunrise_school_db -f Database/Tables/T610_new_table.sql`
4. Update `deploy_database.sql` to include the new table

---

## 📞 Support

For issues or questions:
1. Check this README for deployment instructions
2. Check individual file comments for object-specific details
3. Review PostgreSQL logs for errors
4. Check `MERGE_SUMMARY.md` for historical migration details

---

## 📝 Notes

### Benefits of Refactored Structure

✅ **Modular:** Each object in its own file
✅ **Maintainable:** Easy to find and update specific objects
✅ **Version Control Friendly:** Clear diffs for each change
✅ **Flexible:** Update individual objects without full redeployment
✅ **Documented:** Each file has clear comments and dependencies
✅ **Standardized:** Consistent naming convention across all objects
✅ **Scalable:** Easy to add new objects with proper versioning

### Legacy Folders

- **Init/**: Contains metadata loading and admin user creation scripts (still used)
  - `01_load_metadata.sql` - Loads 78 metadata records
  - `02_create_admin_user.sql` - Creates default admin user
- **Scripts/**: Empty folder (legacy files removed)
- **Versioning/**: Empty folder (can be deleted)
- **DataLoads/**: Existing data loading scripts (kept as is)

### For Existing Databases

If you have an existing production database:
1. **Option 1 (Recommended):** Backup data, drop schema, redeploy using new structure
2. **Option 2:** Manually run individual table files to update specific objects
3. **Option 3:** Keep existing structure and gradually migrate to new structure

---

## ✨ Summary

**For Fresh Deployments:**
1. Run master deployment script: `psql -U sunrise_user -d sunrise_school_db -f Database/deploy_database.sql`
2. Database is ready in ~10 seconds
3. 23 tables, 3 functions, 4 views, 78 metadata records, 26+ indexes
4. Production-ready with all features

**For Updates:**
1. Modify the specific file (e.g., T310_students.sql)
2. Run just that file to update the object
3. No need to redeploy entire database

**Modular. Maintainable. Professional.** 🎉

