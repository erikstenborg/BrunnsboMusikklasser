# Database Backup and Migration Instructions

## Database Schema Overview
The Brunnsbo Musikklasser database contains the following tables:
- **users** - User accounts with roles and authentication
- **groups** - Role-based access control groups (admin, applications_manager, event_manager, parent)
- **user_groups** - Many-to-many relationship between users and groups
- **application** - Student applications for music classes
- **confirmation_codes** - Email verification and password reset codes
- **contact** - Contact form submissions
- **event** - Events and concerts
- **event_tasks** - Tasks assigned to users for events
- **news_post** - News articles and announcements
- **swish_payment** - Swedish Swish payment records

## Method 1: Using pg_dump (Professional Method)

### Export Development Database
```bash
# Export all core tables with data (recommended for production migration)
pg_dump $DATABASE_URL \
  -t users -t groups -t user_groups \
  -t application -t contact -t event -t event_tasks \
  -t news_post -t swish_payment -t confirmation_codes \
  --data-only --column-inserts > production_import.sql

# Export complete database structure and data
pg_dump $DATABASE_URL > full_backup.sql

# Export only structure (schema) without data
pg_dump $DATABASE_URL --schema-only > schema_only.sql

# Export specific tables only
pg_dump $DATABASE_URL -t users -t groups -t user_groups --data-only --column-inserts > users_and_roles.sql
pg_dump $DATABASE_URL -t event -t event_tasks --data-only --column-inserts > events_backup.sql
pg_dump $DATABASE_URL -t application --data-only --column-inserts > applications_backup.sql
pg_dump $DATABASE_URL -t swish_payment --data-only --column-inserts > payments_backup.sql
```

### Import to Production
```bash
# Connect to production database and run:
psql $PRODUCTION_DATABASE_URL < production_import.sql

# Or import specific backup files:
psql $PRODUCTION_DATABASE_URL < users_and_roles.sql
psql $PRODUCTION_DATABASE_URL < events_backup.sql
```

## Method 2: Using Python Export Script

```python
import os
import psycopg2
import json
from datetime import datetime

def export_database():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    
    # Export all main tables
    tables_to_export = {
        'users': "SELECT id, first_name, last_name, email, active, created_at, last_login FROM users",
        'groups': "SELECT id, name, description, created_at FROM groups",
        'user_groups': "SELECT user_id, group_id FROM user_groups",
        'applications': "SELECT id, student_name, parent_name, parent_email, grade_applying_for, application_year, status, created_at FROM application",
        'events': "SELECT id, title, description, event_date, location, is_active, created_at FROM event",
        'event_tasks': "SELECT id, event_id, title, description, assigned_to_user_id, completed, due_offset_days FROM event_tasks",
        'news_posts': "SELECT id, title, content, author, published_date, is_published, featured FROM news_post",
        'contact_messages': "SELECT id, name, email, subject, message, created_at, is_read FROM contact",
        'swish_payments': "SELECT id, amount, currency, status, date_created, date_paid FROM swish_payment"
    }
    
    export_data = {'exported_at': datetime.now().isoformat()}
    
    for table_name, query in tables_to_export.items():
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        
        export_data[table_name] = {
            'columns': columns,
            'data': [dict(zip(columns, row)) for row in rows]
        }
        print(f"Exported {len(rows)} records from {table_name}")
    
    # Save to JSON file
    filename = f'brunnsbo_db_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"Database exported to {filename}")
    conn.close()

if __name__ == "__main__":
    export_database()
```

## Method 3: Using the Existing Export Script

```bash
# Run the existing export script
python export_database.py
```

This will create timestamped JSON files for easy backup and migration.

## Important Notes

### Before Production Migration:
1. **Test the import on a staging database first**
2. **Backup production database before importing**
3. **Verify all foreign key relationships**
4. **Check user permissions and role assignments**

### Security Considerations:
- Never commit database URLs or passwords to version control
- Use environment variables for database connections
- Consider anonymizing sensitive data like personal emails and phone numbers
- The export excludes password hashes for security

### Data Validation After Import:
```sql
-- Verify user counts
SELECT COUNT(*) FROM users;

-- Verify group assignments
SELECT g.name, COUNT(ug.user_id) as user_count 
FROM groups g 
LEFT JOIN user_groups ug ON g.id = ug.group_id 
GROUP BY g.name;

-- Verify application data
SELECT application_year, COUNT(*) as count, status 
FROM application 
GROUP BY application_year, status 
ORDER BY application_year DESC;

-- Verify event data
SELECT COUNT(*) as total_events, 
       COUNT(CASE WHEN is_active THEN 1 END) as active_events 
FROM event;
```