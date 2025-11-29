# PowerShell script to set up PostgreSQL database
# Run this in PowerShell (may need to run as Administrator)

Write-Host "PostgreSQL Database Setup Script" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Step 1: Check if PostgreSQL is installed
Write-Host "`nStep 1: Checking PostgreSQL installation..." -ForegroundColor Yellow
$pgPath = "C:\Program Files\PostgreSQL\16\bin\psql.exe"
if (-not (Test-Path $pgPath)) {
    Write-Host "PostgreSQL not found at default location. Please install PostgreSQL first." -ForegroundColor Red
    Write-Host "Download from: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    exit
}

# Step 2: Prompt for database credentials
Write-Host "`nStep 2: Enter PostgreSQL credentials" -ForegroundColor Yellow
$dbName = Read-Host "Database name (default: auth_db)"
if ([string]::IsNullOrWhiteSpace($dbName)) { $dbName = "auth_db" }

$dbUser = Read-Host "Database user (default: auth_user)"
if ([string]::IsNullOrWhiteSpace($dbUser)) { $dbUser = "auth_user" }

$dbPassword = Read-Host "Database password" -AsSecureString
$dbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword)
)

$postgresPassword = Read-Host "PostgreSQL superuser (postgres) password" -AsSecureString
$postgresPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($postgresPassword)
)

# Step 3: Create database and user
Write-Host "`nStep 3: Creating database and user..." -ForegroundColor Yellow

$env:PGPASSWORD = $postgresPasswordPlain

# Create database
& $pgPath -U postgres -c "CREATE DATABASE $dbName;" 2>&1 | Out-Null

# Create user
& $pgPath -U postgres -c "CREATE USER $dbUser WITH PASSWORD '$dbPasswordPlain';" 2>&1 | Out-Null

# Grant privileges
& $pgPath -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $dbName TO $dbUser;" 2>&1 | Out-Null

# Connect and grant schema privileges
& $pgPath -U postgres -d $dbName -c "GRANT ALL ON SCHEMA public TO $dbUser;" 2>&1 | Out-Null

# Clear password from environment
Remove-Item Env:\PGPASSWORD

Write-Host "`n✅ Database setup complete!" -ForegroundColor Green
Write-Host "`nUpdate DATABASE_URL in main.py to:" -ForegroundColor Yellow
Write-Host "postgresql://$dbUser`:$dbPasswordPlain@localhost:5432/$dbName" -ForegroundColor Cyan

Write-Host "`nOr set environment variable:" -ForegroundColor Yellow
Write-Host "`$env:DATABASE_URL=`"postgresql://$dbUser`:$dbPasswordPlain@localhost:5432/$dbName`"" -ForegroundColor Cyan


