# Quick PostgreSQL Setup Guide

## Problem: `psql` command not found

This means PostgreSQL is either not installed or not in your PATH.

## Solution Options:

### Option 1: Install PostgreSQL (Recommended)

**Using winget (Windows Package Manager):**
```powershell
winget install PostgreSQL.PostgreSQL
```

**Using Chocolatey:**
```powershell
choco install postgresql
```

**Manual Download:**
1. Go to: https://www.postgresql.org/download/windows/
2. Download and run the installer
3. **IMPORTANT:** During installation, check "Add PostgreSQL bin directory to PATH"

After installation, restart PowerShell and try:
```powershell
psql -U postgres
```

---

### Option 2: Use Full Path (If Already Installed)

Find where PostgreSQL is installed, then use full path:

```powershell
# Common locations - try these:
"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
"C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres
```

Or find it manually:
```powershell
Get-ChildItem -Path "C:\Program Files" -Filter "psql.exe" -Recurse -ErrorAction SilentlyContinue
```

---

### Option 3: Add PostgreSQL to PATH (If Already Installed)

**Temporary (for current PowerShell session):**
```powershell
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"
psql -U postgres
```

**Permanent:**
```powershell
# Replace 16 with your version number
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\PostgreSQL\16\bin", "User")
```

Then restart PowerShell.

---

### Option 4: Use Docker (Alternative - No Installation Needed)

If you have Docker installed:

```powershell
# Start PostgreSQL container
docker run --name postgres-auth -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=auth_db -p 5432:5432 -d postgres

# Connect to it
docker exec -it postgres-auth psql -U postgres
```

Then update `main.py`:
```python
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/auth_db"
```

---

### Option 5: Use pgAdmin (GUI Tool)

1. Install PostgreSQL (includes pgAdmin)
2. Open pgAdmin
3. Right-click "Databases" → Create → Database
4. Name: `auth_db`
5. Use pgAdmin's Query Tool to run SQL commands

---

## After PostgreSQL is Working:

Run the database setup:

```sql
CREATE DATABASE auth_db;
CREATE USER auth_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;
\c auth_db
GRANT ALL ON SCHEMA public TO auth_user;
\q
```

Update `main.py`:
```python
DATABASE_URL = "postgresql://auth_user:your_password@localhost:5432/auth_db"
```

---

## Quick Check Script

Run this to check if PostgreSQL is installed:
```powershell
.\check_postgres.ps1
```


