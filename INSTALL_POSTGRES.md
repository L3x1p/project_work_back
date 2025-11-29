# Install PostgreSQL - Step by Step

## Method 1: Download and Install (Easiest)

1. **Download PostgreSQL:**
   - Go to: https://www.postgresql.org/download/windows/
   - Click "Download the installer"
   - Download the latest version (16.x recommended)

2. **Run the Installer:**
   - Double-click the downloaded `.exe` file
   - Click "Next" through the setup wizard
   - **IMPORTANT:** When you see "Select Components", make sure "Command Line Tools" is checked
   - **IMPORTANT:** When you see "Password", set a password for the `postgres` superuser (remember this!)
   - **IMPORTANT:** When you see "Advanced Options", check "Add PostgreSQL bin directory to PATH"
   - Click "Next" and "Finish"

3. **Restart PowerShell** (close and reopen)

4. **Test Installation:**
   ```powershell
   psql -U postgres
   ```
   (Enter the password you set during installation)

5. **Create Database:**
   ```sql
   CREATE DATABASE auth_db;
   CREATE USER auth_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;
   \c auth_db
   GRANT ALL ON SCHEMA public TO auth_user;
   \q
   ```

6. **Update main.py:**
   ```python
   DATABASE_URL = "postgresql://auth_user:your_password@localhost:5432/auth_db"
   ```

---

## Method 2: Use Docker (If You Have Docker)

If you have Docker Desktop installed:

```powershell
# Start PostgreSQL container
docker run --name postgres-auth -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=auth_db -p 5432:5432 -d postgres

# Test connection
docker exec -it postgres-auth psql -U postgres -d auth_db
```

Then in `main.py`:
```python
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/auth_db"
```

To stop container later:
```powershell
docker stop postgres-auth
docker rm postgres-auth
```

---

## Method 3: Use SQLite (Simpler, No Installation)

If you want to skip PostgreSQL installation for now, you can use SQLite instead.

Update `main.py` line 18:
```python
DATABASE_URL = "sqlite:///./auth.db"
```

And change the import in `main.py`:
```python
# Change this line:
from sqlalchemy import create_engine, Column, Integer, String, Boolean

# To:
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
```

SQLite doesn't need a server - it's a file-based database. Perfect for development/testing!

---

## After Installation - Quick Commands

```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database (inside psql)
CREATE DATABASE auth_db;

# Create user
CREATE USER auth_user WITH PASSWORD 'your_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;

# Connect to new database
\c auth_db

# Grant schema privileges
GRANT ALL ON SCHEMA public TO auth_user;

# Exit
\q
```


