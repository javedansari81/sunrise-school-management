# Database Documentation

This directory contains comprehensive database documentation for the Sunrise School Management System, including setup guides, schema documentation, and migration procedures.

## 📋 Available Documentation

### 🚀 [README.md](./README.md)
**Database Structure and Usage Guide**
- Complete database schema overview
- Table organization and relationships
- Usage instructions for different scenarios
- File organization within Database/ folder

### 📖 [SETUP_GUIDE.md](./SETUP_GUIDE.md)
**Database Setup Instructions**
- Step-by-step installation procedures
- Environment configuration
- Sample data loading
- Verification and troubleshooting

### 📚 [LEGACY_README.md](./LEGACY_README.md)
**Legacy Database Files Documentation**
- Historical database file information
- Migration from old structure to new
- Reference for legacy system understanding

## 🗄️ Database Structure Overview

The database is organized into logical folders within the `Database/` directory:

### 📁 Tables/
DDL (Data Definition Language) scripts for creating database tables:
- `00_metadata_tables.sql` - Reference tables and metadata
- `01_enums.sql` - PostgreSQL ENUM type definitions
- `02_users.sql` - User authentication and management
- `03_students.sql` - Student information and enrollment
- `04_teachers.sql` - Teacher profiles and assignments
- `05_fees.sql` - Fee structures and payment tracking
- `06_attendance.sql` - Attendance tracking system
- `07_leaves.sql` - Leave management system
- `08_expenses.sql` - Expense tracking and management
- `09_indexes.sql` - Performance optimization indexes
- `10_constraints.sql` - Foreign key relationships

### 📊 DataLoads/
DML (Data Manipulation Language) scripts for sample data:
- `00_metadata_data.sql` - Reference data and lookups
- `06_enhanced_leave_test_data.sql` - Leave management test data
- `06_sample_leave_data.sql` - Sample leave requests
- `07_sample_expense_data.sql` - Sample expense records

### 🔄 Versioning/
Database migration and schema change scripts:
- `enum_to_varchar_migration.sql` - ENUM to VARCHAR conversion
- `v1.0_to_v1.1_session_year_update.sql` - Version upgrade scripts
- `add_aadhar_no_columns.sql` - Aadhar number field additions
- `V006_expenses_soft_delete_migration.sql` - Soft delete implementation
- Various enhancement and fix scripts

### 🎯 Init/
Complete database initialization scripts:
- `00_drop_all.sql` - Clean database reset (DANGER!)
- `00_render_delete_all.sql` - Render.com specific cleanup
- `01_create_database.sql` - Complete database creation
- `02_load_initial_data_clean.sql` - Essential initial data

### 🛠️ Scripts/
Utility and maintenance scripts:
- `apply_metadata_indexes.sql` - Index optimization
- `create_enhanced_views.sql` - Database views for reporting

### 📜 Legacy/
Historical database files for reference:
- `original_create_tables.sql` - Original table creation script

## 🎯 Quick Start Database Setup

### 1. Complete Setup (Recommended)
```bash
# One-command complete setup
psql -d your_database -f Database/Init/01_create_database.sql
psql -d your_database -f Database/Init/02_load_initial_data_clean.sql
```

### 2. Step-by-Step Setup
```bash
# Create tables in order
psql -d your_database -f Database/Tables/00_metadata_tables.sql
psql -d your_database -f Database/Tables/02_users.sql
psql -d your_database -f Database/Tables/03_students.sql
# ... continue with other tables

# Load sample data
psql -d your_database -f Database/DataLoads/00_metadata_data.sql
psql -d your_database -f Database/DataLoads/07_sample_expense_data.sql
```

### 3. Apply Migrations
```bash
# Apply version upgrades
psql -d your_database -f Database/Versioning/enum_to_varchar_migration.sql
psql -d your_database -f Database/Versioning/V006_expenses_soft_delete_migration.sql
```

## 🏗️ Database Architecture

### Core Entities
- **Users**: Authentication and role management
- **Students**: Student profiles and academic information
- **Teachers**: Staff profiles and assignments
- **Classes**: Academic class structure and organization

### Management Systems
- **Fee Management**: Payment structures, transactions, and tracking
- **Leave Management**: Leave requests, approvals, and tracking
- **Expense Management**: School expense tracking and categorization
- **Attendance**: Student and staff attendance tracking

### Supporting Systems
- **Metadata**: Reference tables for dropdowns and configurations
- **Audit**: Change tracking and data integrity
- **Reporting**: Views and aggregations for analytics

## 🔧 Database Features

### Performance Optimizations
- **Proper Indexing**: All foreign keys and frequently queried columns
- **Query Optimization**: Efficient joins and filtering strategies
- **Connection Pooling**: Optimized database connection management
- **Partitioning**: Large table partitioning where appropriate

### Data Integrity
- **Foreign Key Constraints**: Referential integrity enforcement
- **Check Constraints**: Data validation at database level
- **Unique Constraints**: Duplicate prevention
- **Not Null Constraints**: Required field enforcement

### Advanced Features
- **Soft Delete**: Logical deletion with data preservation
- **Audit Trails**: Change tracking for critical data
- **Versioning**: Schema version management with Alembic
- **Backup Strategy**: Automated backup and recovery procedures

## 🚨 Important Considerations

### Data Security
- **Sensitive Data**: Proper handling of personal information
- **Access Control**: Role-based database access
- **Encryption**: Sensitive field encryption where required
- **Audit Logging**: Change tracking for compliance

### Performance Monitoring
- **Query Performance**: Regular query optimization
- **Index Usage**: Monitor and optimize index effectiveness
- **Connection Monitoring**: Track connection pool usage
- **Storage Management**: Monitor database growth and cleanup

### Backup and Recovery
- **Regular Backups**: Automated daily backups
- **Point-in-Time Recovery**: Transaction log backups
- **Disaster Recovery**: Cross-region backup strategy
- **Testing**: Regular backup restoration testing

## 🔍 Troubleshooting Common Issues

### Connection Issues
- Check database server status
- Verify connection string format
- Confirm network connectivity
- Review authentication credentials

### Performance Issues
- Analyze slow query logs
- Check index usage statistics
- Monitor connection pool status
- Review table statistics

### Migration Issues
- Verify migration script syntax
- Check for data conflicts
- Review dependency order
- Test on development environment first

## 📊 Database Monitoring

### Key Metrics
- **Connection Count**: Active database connections
- **Query Performance**: Average query execution time
- **Storage Usage**: Database size and growth rate
- **Index Efficiency**: Index hit ratio and usage

### Monitoring Tools
- **PostgreSQL Stats**: Built-in statistics views
- **Query Analysis**: EXPLAIN ANALYZE for query optimization
- **Connection Monitoring**: pg_stat_activity for active sessions
- **Performance Insights**: Cloud provider monitoring tools

## 🔗 Related Documentation

- **Setup Guides**: [../setup/](../setup/)
- **Testing Procedures**: [../testing/](../testing/)
- **Feature Documentation**: [../features/](../features/)
- **Deployment Guides**: [../deployment/](../deployment/)

## 📞 Database Support

### Getting Help
1. Check the specific database documentation
2. Review setup guides for configuration issues
3. Consult testing procedures for validation
4. Check deployment guides for production issues

### Best Practices
- Always test migrations on development environment first
- Keep regular backups before major changes
- Monitor performance after schema changes
- Document custom modifications and procedures
