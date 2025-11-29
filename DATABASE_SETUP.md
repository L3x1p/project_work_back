# PostgreSQL Database Setup - Step by Step Commands

## Step 1: Install PostgreSQL (if not installed)

Download and install from: https://www.postgresql.org/download/windows/

Or use chocolatey:
```powershell
choco install postgresql
```

## Step 2: Start PostgreSQL Service

```powershell
# Check if PostgreSQL service is running
Get-Service -Name postgresql*

# If not running, start it (replace X with your version number)
Start-Service postgresql-x64-XX
```

## Step 3: Open PostgreSQL Command Line (psql)

```powershell
# Navigate to PostgreSQL bin directory (adjust version number)
cd "C:\Program Files\PostgreSQL\16\bin"

# Or if PostgreSQL is in your PATH:
psql -U postgres
```

## Step 4: Create Database and User

Run these commands in psql (or copy-paste all at once):

```sql
-- Create a new database
CREATE DATABASE auth_db;

-- Create a user (optional, or use default postgres user)
CREATE USER auth_user WITH PASSWORD 'your_password_here';

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;

-- Connect to the new database
\c auth_db

-- Grant schema privileges (if using a specific user)
GRANT ALL ON SCHEMA public TO auth_user;
```

## Step 5: Update main.py with Database URL

Update line 18 in `main.py`:

```python
DATABASE_URL = "postgresql://auth_user:your_password_here@localhost:5432/auth_db"
```

Or if using default postgres user:
```python
DATABASE_URL = "postgresql://postgres:your_postgres_password@localhost:5432/auth_db"
```

## Step 6: Tables Will Be Created Automatically

When you run the FastAPI app, SQLAlchemy will automatically create the `users` table with this structure:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

## Step 7: Verify Tables Were Created

After running your FastAPI app once, verify in psql:

```sql
-- Connect to your database
\c auth_db

-- List all tables
\dt

-- View users table structure
\d users

-- View all users (if any)
SELECT * FROM users;
```

## Quick Setup Script (All Commands at Once)

```sql
-- Run this in psql as postgres superuser
CREATE DATABASE auth_db;
CREATE USER auth_user WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;
\c auth_db
GRANT ALL ON SCHEMA public TO auth_user;
\q
```

## Alternative: Using Environment Variable

Set environment variable instead of hardcoding:

```powershell
# Windows PowerShell
$env:DATABASE_URL="postgresql://auth_user:your_password_here@localhost:5432/auth_db"
```

Then in `main.py`, it will automatically use this value.


