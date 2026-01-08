# Backend Server - Quick Start Commands

## 🚀 Start the Server

### Option 1: Using uvicorn (Recommended)
```powershell
cd D:\Freelance\GenConfi\Gen_Confi_Backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Using Python directly
```powershell
cd D:\Freelance\GenConfi\Gen_Confi_Backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: One-liner (if venv is already activated)
```powershell
cd D:\Freelance\GenConfi\Gen_Confi_Backend; .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## ✅ Verify Server is Running

### Test Health Endpoint
```powershell
curl http://localhost:8000/health
```

### Or in PowerShell
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
```

## 🔍 Pre-flight Checks

### 1. Test Database Connection
```powershell
cd D:\Freelance\GenConfi\Gen_Confi_Backend
.\venv\Scripts\python.exe -m app.db.test_connection
```

### 2. Check .env file exists
```powershell
cd D:\Freelance\GenConfi\Gen_Confi_Backend
if (Test-Path .env) { Write-Host ".env exists" } else { Copy-Item env.example .env; Write-Host "Created .env from template" }
```

### 3. Initialize Database (if needed)
```powershell
cd D:\Freelance\GenConfi\Gen_Confi_Backend
.\venv\Scripts\python.exe -m app.db.init_db
```

## 📋 Complete Setup Sequence

```powershell
# 1. Navigate to backend
cd D:\Freelance\GenConfi\Gen_Confi_Backend

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Test database connection
python -m app.db.test_connection

# 4. Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Access Points

Once server is running:
- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Base**: http://localhost:8000/api/v1

## 🛑 Stop Server

Press `Ctrl + C` in the terminal where server is running

## ⚠️ Troubleshooting

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Virtual Environment Not Found
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Database Connection Error
```powershell
# Verify PostgreSQL is running
# Check .env file has correct DATABASE_URL
# Test connection
python -m app.db.test_connection
```

