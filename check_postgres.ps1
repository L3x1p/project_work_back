# Script to check PostgreSQL installation and provide setup instructions

Write-Host "Checking PostgreSQL Installation..." -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Common PostgreSQL installation paths
$possiblePaths = @(
    "C:\Program Files\PostgreSQL\16\bin\psql.exe",
    "C:\Program Files\PostgreSQL\15\bin\psql.exe",
    "C:\Program Files\PostgreSQL\14\bin\psql.exe",
    "C:\Program Files\PostgreSQL\13\bin\psql.exe",
    "C:\Program Files (x86)\PostgreSQL\16\bin\psql.exe",
    "C:\Program Files (x86)\PostgreSQL\15\bin\psql.exe"
)

$foundPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $foundPath = $path
        Write-Host "`n✅ PostgreSQL found at: $path" -ForegroundColor Green
        break
    }
}

if (-not $foundPath) {
    Write-Host "`n❌ PostgreSQL not found in common locations." -ForegroundColor Red
    Write-Host "`nYou have two options:" -ForegroundColor Yellow
    Write-Host "`n1. INSTALL POSTGRESQL:" -ForegroundColor Cyan
    Write-Host "   Download from: https://www.postgresql.org/download/windows/" -ForegroundColor White
    Write-Host "   Or use winget: winget install PostgreSQL.PostgreSQL" -ForegroundColor White
    Write-Host "   Or use chocolatey: choco install postgresql" -ForegroundColor White
    
    Write-Host "`n2. USE FULL PATH:" -ForegroundColor Cyan
    Write-Host "   If PostgreSQL is installed, find it manually and use full path" -ForegroundColor White
    Write-Host "   Example: `"C:\Program Files\PostgreSQL\16\bin\psql.exe`" -U postgres" -ForegroundColor White
    
    Write-Host "`n3. USE DOCKER (Alternative):" -ForegroundColor Cyan
    Write-Host "   docker run --name postgres-auth -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=auth_db -p 5432:5432 -d postgres" -ForegroundColor White
} else {
    $binDir = Split-Path $foundPath
    Write-Host "`nTo use psql, you can:" -ForegroundColor Yellow
    Write-Host "`n1. Use full path:" -ForegroundColor Cyan
    Write-Host "   `"$foundPath`" -U postgres" -ForegroundColor White
    
    Write-Host "`n2. Add to PATH (temporary for this session):" -ForegroundColor Cyan
    Write-Host "   `$env:Path += `";$binDir`"" -ForegroundColor White
    
    Write-Host "`n3. Add to PATH permanently:" -ForegroundColor Cyan
    Write-Host "   [Environment]::SetEnvironmentVariable(`"Path`", `$env:Path + `";$binDir`", `"User`")" -ForegroundColor White
    
    Write-Host "`nWould you like to add PostgreSQL to PATH for this session? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        $env:Path += ";$binDir"
        Write-Host "`n✅ Added to PATH. You can now use 'psql' command." -ForegroundColor Green
        Write-Host "`nTry: psql -U postgres" -ForegroundColor Cyan
    }
}


