# Database Backup and Migration Instructions

## Method 1: Using pg_dump (Professional Method)

### Export Development Database
```bash
# Export specific tables only
pg_dump $DATABASE_URL -t admin_users -t event --data-only --column-inserts > production_import.sql

# Or export entire database structure and data
pg_dump $DATABASE_URL > full_backup.sql
```

### Import to Production
```bash
# Connect to production database and run:
psql $PRODUCTION_DATABASE_URL < production_import.sql
```

## Method 2: Using SQL Export (Simple Method)

1. Use the provided `database_export.sql` file
2. Copy the content
3. Run in your production database

## Method 3: Using Python Script

Run `python3 export_database.py` to generate custom SQL export statements.

## Important Tables to Export:
- `admin_users` - Your admin login credentials
- `event` - All your concerts and events
- `news_post` - Any news articles (currently empty)
- `application` - Student applications (if any)
- `contact` - Contact form submissions (if any)

## Notes:
- The export uses `ON CONFLICT` clauses to handle duplicate IDs safely
- Sequences are updated to prevent ID conflicts
- All data preserves original timestamps and relationships