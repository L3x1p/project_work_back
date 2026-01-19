# How to View Database Entries

There are several ways to view the current database entries. Choose the method that works best for you.

## Method 1: Using the Python Script (Recommended)

I've created a simple Python script that displays all database entries in a readable format.

**Run the script:**
```bash
python view_database.py
```

This will show:
- All users
- All refresh tokens
- All career fields (with user associations)
- All user skills (grouped by user)
- Summary statistics

## Method 2: Using PostgreSQL Command Line (psql)

If you have `psql` installed, you can connect directly to the database:

```bash
# Connect to database
psql -h localhost -p 5433 -U auth_user -d auth_db

# When prompted, enter password: Qqwerty1!
```

**Once connected, run these queries:**

```sql
-- View all users
SELECT * FROM users;

-- View all career fields
SELECT * FROM career_fields;

-- View all user skills
SELECT * FROM user_skills;

-- View career fields with user info
SELECT 
    cf.id,
    cf.field_name,
    cf.summary,
    u.username,
    cf.created_at
FROM career_fields cf
LEFT JOIN users u ON cf.user_id = u.id
ORDER BY cf.created_at DESC;

-- View skills with user and career field info
SELECT 
    us.id,
    us.skill_name,
    u.username,
    cf.field_name,
    us.created_at
FROM user_skills us
LEFT JOIN users u ON us.user_id = u.id
LEFT JOIN career_fields cf ON us.career_field_id = cf.id
ORDER BY us.created_at DESC;

-- Count skills per user
SELECT 
    u.username,
    COUNT(us.id) as skill_count
FROM users u
LEFT JOIN user_skills us ON u.id = us.user_id
GROUP BY u.id, u.username
ORDER BY skill_count DESC;

-- Count career fields per user
SELECT 
    u.username,
    COUNT(cf.id) as field_count
FROM users u
LEFT JOIN career_fields cf ON u.id = cf.user_id
GROUP BY u.id, u.username
ORDER BY field_count DESC;
```

## Method 3: Using a Database GUI Tool

You can use any PostgreSQL GUI tool like:
- **pgAdmin** (official PostgreSQL tool)
- **DBeaver** (free, cross-platform)
- **TablePlus** (paid, macOS/Windows)
- **DataGrip** (JetBrains, paid)

**Connection Details:**
- Host: `localhost`
- Port: `5433`
- Database: `auth_db`
- Username: `auth_user`
- Password: `Qqwerty1!`

## Method 4: Add an API Endpoint (Optional)

If you want to view data through the API, you can add this endpoint to `main.py`:

```python
@app.get("/admin/database-stats")
async def get_database_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get database statistics (requires authentication)"""
    users_count = db.query(User).count()
    career_fields_count = db.query(CareerField).count()
    skills_count = db.query(UserSkill).count()
    
    return {
        "users": users_count,
        "career_fields": career_fields_count,
        "skills": skills_count
    }
```

## Quick Check Commands

**Check if database is accessible:**
```bash
python -c "from main import engine; from sqlalchemy import inspect; print('Tables:', inspect(engine).get_table_names())"
```

**Count entries quickly:**
```bash
python -c "
from main import User, CareerField, UserSkill, SessionLocal
db = SessionLocal()
print('Users:', db.query(User).count())
print('Career Fields:', db.query(CareerField).count())
print('Skills:', db.query(UserSkill).count())
db.close()
"
```

## Troubleshooting

**If you get connection errors:**
1. Make sure PostgreSQL is running
2. Check the connection string in `main.py` matches your setup
3. Verify the database `auth_db` exists
4. Check that user `auth_user` has proper permissions

**If tables don't exist:**
- The tables are created automatically when you run `main.py`
- Or run: `python -c "from main import Base, engine; Base.metadata.create_all(bind=engine)"`


