# Legacy Database Files

This folder contains the original database files from the FastAPI backend project. These files have been moved here for reference and migration purposes.

## Files Moved to Legacy

### Original Files (from sunrise-backend-fastapi/)
- `create_tables.sql` - Original table creation script
- `insert_sample_data.sql` - Original sample data insertion
- `database_schema.sql` - Original database schema
- `setup_database.sql` - Original database setup script
- `sample_data.sql` - Additional sample data

### Migration Scripts
- `migrate_enum_to_varchar.py` - Python script for ENUM to VARCHAR migration
- `init_database.py` - Python database initialization script
- `setup_database.py` - Python setup script

## Migration to New Structure

The new database structure is organized as follows:

### Old → New Mapping
```
Legacy/                     →  New Structure/
├── create_tables.sql      →  Tables/01_enums.sql to 10_constraints.sql
├── insert_sample_data.sql →  DataLoads/01_initial_users.sql to 05_sample_attendance.sql
├── database_schema.sql    →  Tables/ (split into multiple files)
└── setup_database.sql     →  Init/99_complete_setup.sql
```

### Key Improvements in New Structure

1. **Modular Organization**: Tables split by functionality
2. **Better Versioning**: Dedicated versioning folder for migrations
3. **Complete Sample Data**: Comprehensive test data across all modules
4. **PostgreSQL Compatibility**: All scripts optimized for PostgreSQL
5. **ENUM to VARCHAR**: Better SQLAlchemy compatibility
6. **Comprehensive Indexes**: Performance-optimized indexes
7. **Proper Constraints**: Foreign keys and check constraints

### Migration Steps

If you want to migrate from the old structure to the new one:

1. **Backup existing data**:
   ```bash
   pg_dump your_database > backup.sql
   ```

2. **Clean old structure**:
   ```bash
   psql -d your_database -f ../Init/00_drop_all.sql
   ```

3. **Apply new structure**:
   ```bash
   psql -d your_database -f ../Init/99_complete_setup.sql
   ```

4. **Migrate existing data** (if needed):
   - Export data from backup
   - Transform to match new schema
   - Import using new DataLoads scripts

### Compatibility Notes

- **ENUM Types**: Old structure used PostgreSQL ENUMs, new structure uses VARCHAR with CHECK constraints
- **Field Names**: Some field names have been standardized
- **Relationships**: Foreign key relationships are more comprehensive
- **Indexes**: Performance indexes have been added
- **Data Types**: Some data types have been optimized

### Reference Only

These legacy files are kept for reference only. For new installations or updates, use the files in the main Database/ folder structure.
