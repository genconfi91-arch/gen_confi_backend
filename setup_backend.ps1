# Gen_Confi_Backend Setup Script
# This script creates a new virtual environment named "backend" and installs dependencies

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Gen_Confi_Backend Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Step 1: Remove old venv if exists
Write-Host "[1/5] Checking for old virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Remove-Item -Recurse -Force venv
    Write-Host "  ✓ Deleted old venv folder" -ForegroundColor Green
} else {
    Write-Host "  ✓ No old venv found" -ForegroundColor Green
}

# Step 2: Create new virtual environment
Write-Host "[2/5] Creating new virtual environment named 'backend'..." -ForegroundColor Yellow
if (Test-Path "backend") {
    Write-Host "  ⚠ 'backend' folder already exists. Removing..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force backend
}
python -m venv backend
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Virtual environment created successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Step 3: Activate virtual environment
Write-Host "[3/5] Activating virtual environment..." -ForegroundColor Yellow
& ".\backend\Scripts\Activate.ps1"
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green

# Step 4: Upgrade pip
Write-Host "[4/5] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "  ✓ pip upgraded" -ForegroundColor Green

# Step 5: Install dependencies
Write-Host "[5/5] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ All dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete! ✓" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Make sure your .env file is configured" -ForegroundColor White
Write-Host "  2. Run database migrations: alembic upgrade head" -ForegroundColor White
Write-Host "  3. Start the server: uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload" -ForegroundColor White
Write-Host ""
Write-Host "Note: Server will run on port 8002 (to avoid conflict with port 8000)" -ForegroundColor Cyan
Write-Host ""

