# Database Deployment Flow Diagram

## 🔄 Complete Deployment Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INITIATES DEPLOYMENT                     │
│                                                                  │
│  Methods:                                                        │
│  • curl -X POST /api/v1/database/deploy                        │
│  • Swagger UI (http://localhost:8000/docs)                     │
│  • Python test script (test_database_deployment.py)            │
│  • HTTP client (Postman, Insomnia, etc.)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI ENDPOINT RECEIVES REQUEST             │
│                                                                  │
│  POST /api/v1/database/deploy                                   │
│  File: app/api/v1/endpoints/database.py                        │
│  Function: deploy_database()                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION & SETUP                            │
│                                                                  │
│  ✓ Check DATABASE_URL exists                                    │
│  ✓ Verify PostgreSQL (not SQLite)                              │
│  ✓ Connect to database                                          │
│  ✓ Locate Database/ folder                                      │
│  ✓ Initialize steps tracking list                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 0: DROP EXISTING SCHEMA                                   │
│                                                                  │
│  SQL: DROP SCHEMA IF EXISTS sunrise CASCADE;                    │
│  Purpose: Clean slate for deployment                            │
│  Result: All existing data deleted                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: SCHEMA INITIALIZATION                                  │
│                                                                  │
│  File: Database/Schema/00_create_schema.sql                     │
│  Actions:                                                        │
│  • CREATE SCHEMA sunrise                                        │
│  • CREATE EXTENSION pgcrypto                                    │
│  • CREATE TABLE schema_versions                                 │
│  • GRANT permissions to sunrise_user                            │
│  • SET search_path                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: CREATE METADATA TABLES (13 tables)                    │
│                                                                  │
│  Files: Database/Tables/T1xx_*.sql                             │
│  Tables:                                                         │
│  • T100_user_types          • T110_session_years               │
│  • T120_genders             • T130_classes                      │
│  • T140_payment_types       • T150_payment_statuses            │
│  • T160_payment_methods     • T170_leave_types                 │
│  • T180_leave_statuses      • T190_expense_categories          │
│  • T200_expense_statuses    • T210_employment_statuses         │
│  • T220_qualifications                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: CREATE CORE TABLES (3 tables)                         │
│                                                                  │
│  Files: Database/Tables/T3xx_*.sql                             │
│  Tables:                                                         │
│  • T300_users                                                   │
│  • T310_students                                                │
│  • T320_teachers                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: CREATE FEE MANAGEMENT TABLES (4 tables)               │
│                                                                  │
│  Files: Database/Tables/T4xx_*.sql                             │
│  Tables:                                                         │
│  • T400_fee_structures                                          │
│  • T410_fee_records                                             │
│  • T420_monthly_fee_tracking                                    │
│  • T430_monthly_payment_allocations                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: CREATE EXPENSE MANAGEMENT TABLES (2 tables)           │
│                                                                  │
│  Files: Database/Tables/T5xx_*.sql                             │
│  Tables:                                                         │
│  • T500_expenses                                                │
│  • T510_vendors                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: CREATE LEAVE MANAGEMENT TABLES (1 table)              │
│                                                                  │
│  Files: Database/Tables/T6xx_*.sql                             │
│  Tables:                                                         │
│  • T600_leave_requests                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: CREATE FUNCTIONS (3 functions)                        │
│                                                                  │
│  Files: Database/Functions/F1xx_*.sql                          │
│  Functions:                                                      │
│  • F100_calculate_age                                           │
│  • F110_get_academic_year                                       │
│  • F120_calculate_fee_balance                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 8: CREATE VIEWS (4 views)                                │
│                                                                  │
│  Files: Database/Views/V1xx_*.sql                              │
│  Views:                                                          │
│  • V100_student_summary                                         │
│  • V110_teacher_summary                                         │
│  • V120_fee_collection_summary                                  │
│  • V130_enhanced_student_fee_status                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 9: LOAD METADATA (78 records)                            │
│                                                                  │
│  File: Database/Init/01_load_metadata.sql                      │
│  Data:                                                           │
│  • 5 User types          • 5 Session years                     │
│  • 3 Genders             • 16 Classes                          │
│  • 4 Payment types       • 5 Payment statuses                  │
│  • 6 Payment methods     • 5 Leave types                       │
│  • 4 Leave statuses      • 6 Expense categories                │
│  • 4 Expense statuses    • 6 Employment statuses               │
│  • 9 Qualifications                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 10: CREATE ADMIN USER                                    │
│                                                                  │
│  File: Database/Init/02_create_admin_user.sql                  │
│  User:                                                           │
│  • Email: admin@sunriseschool.edu                              │
│  • Password: admin123 (bcrypt hashed)                          │
│  • User Type: ADMIN                                             │
│  • Status: Active                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 11: VERIFICATION                                          │
│                                                                  │
│  Checks:                                                         │
│  • Count tables in sunrise schema                               │
│  • Count users in users table                                   │
│  • Count metadata records across all metadata tables            │
│  • Verify expected counts match                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GENERATE RESPONSE                             │
│                                                                  │
│  Response includes:                                              │
│  • success: true/false                                          │
│  • message: Summary message                                     │
│  • steps: Array of all step results                            │
│  • total_steps: Total number of steps                          │
│  • completed_steps: Number of successful steps                 │
│  • failed_steps: Number of failed steps                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RETURN TO USER                                │
│                                                                  │
│  HTTP 200 OK                                                     │
│  Content-Type: application/json                                 │
│  Body: DeploymentResponse                                        │
└─────────────────────────────────────────────────────────────────┘
```

## 🔍 Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    STEP EXECUTION                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌───────────────┐   ┌───────────────┐
            │   SUCCESS     │   │    FAILURE    │
            └───────────────┘   └───────────────┘
                    │                   │
                    │                   ▼
                    │           ┌───────────────┐
                    │           │ Log Error     │
                    │           │ Create Step   │
                    │           │ with Error    │
                    │           └───────────────┘
                    │                   │
                    │                   ▼
                    │           ┌───────────────┐
                    │           │ Stop Further  │
                    │           │ Execution     │
                    │           └───────────────┘
                    │                   │
                    └───────────┬───────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Return Response with  │
                    │ Partial Results       │
                    └───────────────────────┘
```

## 📊 Data Flow

```
┌──────────────┐
│  SQL Files   │
│  (Database/) │
└──────┬───────┘
       │
       │ Read
       ▼
┌──────────────┐
│  Python      │
│  Endpoint    │
└──────┬───────┘
       │
       │ Execute
       ▼
┌──────────────┐
│  PostgreSQL  │
│  Database    │
└──────┬───────┘
       │
       │ Verify
       ▼
┌──────────────┐
│  Response    │
│  JSON        │
└──────────────┘
```

## 🎯 File Processing Order

```
Database/
│
├── Schema/
│   └── 00_create_schema.sql ────────────────► STEP 1
│
├── Tables/
│   ├── T100_user_types.sql ─────────────────► STEP 2.1
│   ├── T110_session_years.sql ──────────────► STEP 2.2
│   ├── ... (11 more metadata tables) ───────► STEP 2.3-2.13
│   ├── T300_users.sql ──────────────────────► STEP 3.1
│   ├── T310_students.sql ───────────────────► STEP 3.2
│   ├── T320_teachers.sql ───────────────────► STEP 3.3
│   ├── T400_fee_structures.sql ─────────────► STEP 4.1
│   ├── ... (3 more fee tables) ─────────────► STEP 4.2-4.4
│   ├── T500_expenses.sql ───────────────────► STEP 5.1
│   ├── T510_vendors.sql ────────────────────► STEP 5.2
│   └── T600_leave_requests.sql ─────────────► STEP 6.1
│
├── Functions/
│   ├── F100_calculate_age.sql ──────────────► STEP 7.1
│   ├── F110_get_academic_year.sql ──────────► STEP 7.2
│   └── F120_calculate_fee_balance.sql ──────► STEP 7.3
│
├── Views/
│   ├── V100_student_summary.sql ────────────► STEP 8.1
│   ├── V110_teacher_summary.sql ────────────► STEP 8.2
│   ├── V120_fee_collection_summary.sql ─────► STEP 8.3
│   └── V130_enhanced_student_fee_status.sql ► STEP 8.4
│
└── Init/
    ├── 01_load_metadata.sql ────────────────► STEP 9
    └── 02_create_admin_user.sql ────────────► STEP 10
```

## 🔄 Retry Logic

```
┌─────────────────────────────────────────────────────────────────┐
│  Deployment Failed?                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ No Problem!     │
                    │ Just run again  │
                    └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 0 will drop everything and start fresh                    │
│  • No manual cleanup needed                                      │
│  • Safe to run multiple times                                    │
│  • Idempotent operation                                          │
└─────────────────────────────────────────────────────────────────┘
```

## 📈 Timeline

```
Time (seconds)
│
0 ─┬─ Start Request
   │
1 ─┼─ Drop Schema
   │
2 ─┼─ Create Schema
   │
3 ─┼─ Create Metadata Tables (13)
   │
4 ─┼─ Create Core Tables (3)
   │
5 ─┼─ Create Fee Tables (4)
   │
6 ─┼─ Create Expense Tables (2)
   │
7 ─┼─ Create Leave Tables (1)
   │
8 ─┼─ Create Functions (3)
   │
9 ─┼─ Create Views (4)
   │
10 ┼─ Load Metadata (78 records)
   │
11 ┼─ Create Admin User
   │
12 ┼─ Verification
   │
13 ┴─ Return Response

Total: ~5-15 seconds (depending on server)
```

## 🎨 Visual Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE DEPLOYMENT API                       │
│                                                                  │
│  Input:  POST /api/v1/database/deploy                          │
│  Output: Complete PostgreSQL database                           │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                 │
│  │   SQL    │───▶│  FastAPI │───▶│PostgreSQL│                 │
│  │  Files   │    │ Endpoint │    │ Database │                 │
│  └──────────┘    └──────────┘    └──────────┘                 │
│                                                                  │
│  Features:                                                       │
│  ✓ 45+ deployment steps                                         │
│  ✓ Detailed progress tracking                                   │
│  ✓ Error handling & recovery                                    │
│  ✓ Verification & validation                                    │
│  ✓ Idempotent (safe to re-run)                                 │
│                                                                  │
│  Result:                                                         │
│  • 23 Tables                                                     │
│  • 3 Functions                                                   │
│  • 4 Views                                                       │
│  • 78 Metadata Records                                           │
│  • 1 Admin User                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

**This visual guide helps you understand the complete flow of database deployment from start to finish!**

