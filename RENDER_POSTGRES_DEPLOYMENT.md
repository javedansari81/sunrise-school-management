# 🚀 PostgreSQL Database Deployment on Render.com

## 📋 Complete Guide for Sunrise School Management System

This guide provides step-by-step instructions for deploying your PostgreSQL database on Render.com with all necessary optimizations for production use.

---

## 🎯 Prerequisites

### Required Information
- **Render.com Account** (Free tier available)
- **Database Files** (All verified and ready in `Database/` folder)
- **Connection Tools** (psql client or database management tool)

### Database Structure Overview
- **25 Tables** (13 metadata + 12 core application tables)
- **4 Functions** (Age calculation, academic year, fee balance, monthly tracking)
- **4 Views** (Student summary, teacher summary, fee collection, enhanced fee status)
- **78+ Metadata Records** (Complete reference data)
- **30+ Indexes** (Performance optimized)

---

## 🌐 Step 1: Create PostgreSQL Database on Render.com

### 1.1 Login and Create Database
1. Go to [render.com](https://render.com) and login
2. Click **"New +"** → **"PostgreSQL"**
3. Configure database settings:

```
Name: sunrise-postgres-db
Database Name: sunrise_school_db
User: sunrise_user
Region: Singapore (nearest to India for optimal performance)
PostgreSQL Version: 15 (recommended)
Plan: Free (or paid for production)
```

### 1.2 Note Connection Details
After creation, save these connection strings:

```bash
# Internal Database URL (for applications on Render)
postgresql://sunrise_user:[password]@[host]/sunrise_school_db

# External Database URL (for external connections)
postgresql://sunrise_user:[password]@[host].singapore-postgres.render.com/sunrise_school_db
```

### 1.3 Database Specifications
- **Free Tier**: 1GB storage, 97 connections, daily backups
- **Starter ($7/month)**: 10GB storage, 97 connections, daily backups
- **Standard ($20/month)**: 100GB storage, 97 connections, daily backups
- **Pro ($65/month)**: 512GB storage, 500 connections, daily backups

---

## 🔧 Step 2: Prepare Local Environment

### 2.1 Install PostgreSQL Client
**Windows:**
```bash
# Download from https://www.postgresql.org/download/windows/
# Or use Chocolatey
choco install postgresql
```

**macOS:**
```bash
brew install postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql-client
```

### 2.2 Test Connection
```bash
# Test connection to your Render database
psql "postgresql://sunrise_user:[password]@[host].singapore-postgres.render.com/sunrise_school_db" -c "SELECT version();"
```

---

## 🚀 Step 3: Deploy Database Schema

### 3.1 Quick Deployment (Recommended)

**Single Command Deployment:**
```bash
# Navigate to your project directory
cd /path/to/your/project

# Deploy complete database
psql "postgresql://sunrise_user:[password]@[host].singapore-postgres.render.com/sunrise_school_db" -f Database/deploy_database.sql
```

This will execute all steps automatically:
1. ✅ Schema initialization (sunrise schema)
2. ✅ Create 13 metadata tables
3. ✅ Create 12 core application tables
4. ✅ Create 4 database functions
5. ✅ Create 4 database views
6. ✅ Load 78+ metadata records
7. ✅ Create admin user
8. ✅ Load fee structures data

### 3.2 Manual Step-by-Step Deployment (Alternative)

If you prefer manual control:

```bash
# Connect to database
psql "postgresql://sunrise_user:[password]@[host].singapore-postgres.render.com/sunrise_school_db"

# Execute scripts in order
\i Database/Schema/00_create_schema.sql
\i Database/Tables/T100_user_types.sql
\i Database/Tables/T110_session_years.sql
-- ... (continue with all table files)
\i Database/Functions/F100_calculate_age.sql
-- ... (continue with all function files)
\i Database/Views/V100_student_summary.sql
-- ... (continue with all view files)
\i Database/Init/01_load_metadata.sql
\i Database/Init/02_create_admin_user.sql
\i Database/Init/03_fee_structures_data.sql
```

---

## ✅ Step 4: Verify Deployment

### 4.1 Check Table Count
```sql
-- Should return 25 tables
SELECT COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'sunrise' AND table_type = 'BASE TABLE';

-- List all tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'sunrise' AND table_type = 'BASE TABLE' 
ORDER BY table_name;
```

### 4.2 Verify Metadata Records
```sql
-- Check metadata counts
SELECT 'user_types' as table_name, COUNT(*) as records FROM user_types
UNION ALL SELECT 'session_years', COUNT(*) FROM session_years
UNION ALL SELECT 'classes', COUNT(*) FROM classes
UNION ALL SELECT 'payment_methods', COUNT(*) FROM payment_methods
UNION ALL SELECT 'leave_types', COUNT(*) FROM leave_types
UNION ALL SELECT 'expense_categories', COUNT(*) FROM expense_categories
ORDER BY table_name;
```

### 4.3 Test Admin User
```sql
-- Verify admin user creation
SELECT email, user_type_id, is_active, created_at 
FROM users 
WHERE email = 'admin@sunrise.com';

-- Check current session year
SELECT name, is_current, start_date, end_date 
FROM session_years 
WHERE is_current = true;
```

### 4.4 Test Sample Queries
```sql
-- Test joins and relationships
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

## 🔒 Step 5: Security Configuration

### 5.1 Environment Variables
Set these in your application:

```bash
# For production applications
DATABASE_URL=postgresql://sunrise_user:[password]@[host].singapore-postgres.render.com/sunrise_school_db?sslmode=require

# For local development (if needed)
LOCAL_DATABASE_URL=postgresql://sunrise_user:[password]@localhost:5432/sunrise_school_db
```

### 5.2 SSL Configuration
Render.com enforces SSL by default. Ensure your application uses `sslmode=require`.

### 5.3 Connection Pooling
For production applications, configure connection pooling:
- **Max Pool Size**: 20 (for Free tier with 97 connections)
- **Pool Timeout**: 30 seconds
- **Pool Recycle**: 3600 seconds (1 hour)

---

## 📊 Step 6: Performance Optimization

### 6.1 Monitor Database Performance
```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('sunrise_school_db')) as database_size;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'sunrise'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 6.2 Index Usage Analysis
```sql
-- Monitor index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as scans,
    idx_tup_read as tuples_read
FROM pg_stat_user_indexes
WHERE schemaname = 'sunrise'
ORDER BY idx_scan DESC;
```

---

## 🔄 Step 7: Backup Strategy

### 7.1 Automated Backups
Render.com provides:
- **Daily automated backups** (retained for 7 days on Free tier)
- **Point-in-time recovery** (available on paid plans)

### 7.2 Manual Backup Commands
```bash
# Full database backup
pg_dump "postgresql://sunrise_user:[password]@[host].singapore-postgres.render.com/sunrise_school_db" > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
pg_dump "postgresql://sunrise_user:[password]@[host].singapore-postgres.render.com/sunrise_school_db" | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Schema-only backup
pg_dump --schema-only "postgresql://sunrise_user:[password]@[host].singapore-postgres.render.com/sunrise_school_db" > schema_backup.sql
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Connection Issues
```bash
# Test basic connectivity
psql "postgresql://sunrise_user:[password]@[host].singapore-postgres.render.com/sunrise_school_db" -c "SELECT 1;"

# Check SSL requirements
psql "postgresql://sunrise_user:[password]@[host].singapore-postgres.render.com/sunrise_school_db?sslmode=require" -c "SELECT 1;"
```

#### Permission Issues
```sql
-- Grant necessary permissions (if needed)
GRANT USAGE ON SCHEMA sunrise TO sunrise_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sunrise TO sunrise_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA sunrise TO sunrise_user;
```

#### Script Execution Errors
- Ensure all files exist in the correct paths
- Check for syntax errors in SQL files
- Verify dependencies are met (metadata tables before core tables)

---

## 📈 Production Readiness Checklist

### Pre-Deployment
- [ ] Render.com PostgreSQL database created
- [ ] Connection string tested and working
- [ ] All database files verified and accessible
- [ ] Backup strategy planned

### Deployment
- [ ] Schema initialization completed
- [ ] All 25 tables created successfully
- [ ] All 4 functions created successfully
- [ ] All 4 views created successfully
- [ ] Metadata loaded (78+ records)
- [ ] Admin user created and tested
- [ ] Fee structures data loaded

### Post-Deployment
- [ ] Database connectivity verified
- [ ] Sample queries tested
- [ ] Performance monitoring set up
- [ ] Backup procedures documented
- [ ] Application connection string configured

---

## 🎯 Next Steps

After successful database deployment:

1. **Backend Connection**: Update your FastAPI application with the Render database URL
2. **Environment Variables**: Set DATABASE_URL in your backend deployment
3. **Testing**: Run comprehensive tests to ensure all functionality works
4. **Monitoring**: Set up logging and performance monitoring
5. **Documentation**: Update your team with new connection details

---

## 📞 Support Information

### Admin Login Credentials
- **Email**: admin@sunrise.com
- **Password**: admin123
- **⚠️ Important**: Change password after first login!

### Database Connection Details
- **Schema**: sunrise
- **Tables**: 25 (13 metadata + 12 core)
- **Functions**: 4
- **Views**: 4
- **Indexes**: 30+

---

**🎉 Database deployment completed successfully!**
**Your PostgreSQL database is now ready for production use on Render.com.**
