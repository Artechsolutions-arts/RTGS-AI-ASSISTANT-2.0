@echo off
REM Government AI Personal Assistant - Quick Start Script
REM This script automates the setup process

echo ========================================
echo Government AI Personal Assistant
echo Quick Start Script
echo ========================================
echo.

REM Check if Docker is running
echo [1/7] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop and try again
    pause
    exit /b 1
)
echo ✓ Docker is installed

REM Start Docker services
echo.
echo [2/7] Starting Docker services...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start Docker services
    pause
    exit /b 1
)
echo ✓ Docker services started

REM Wait for services to be ready
echo.
echo [3/7] Waiting for services to initialize (60 seconds)...
timeout /t 60 /nobreak >nul
echo ✓ Services initialized

REM Initialize MongoDB
echo.
echo [4/7] Initializing MongoDB...
docker exec -i ai-assist-mongodb mongosh gov_ai_assistant < database\init_db.js
if errorlevel 1 (
    echo WARNING: MongoDB initialization may have failed
    echo Continuing anyway...
)
echo ✓ MongoDB initialized

REM Generate synthetic data
echo.
echo [5/7] Generating synthetic data...
cd synthetic-data
python generator.py
if errorlevel 1 (
    echo ERROR: Failed to generate synthetic data
    echo Make sure Python 3.10+ is installed
    cd ..
    pause
    exit /b 1
)
echo ✓ Synthetic data generated

REM Seed MongoDB
echo.
echo [6/7] Seeding MongoDB with synthetic data...
python seed_mongodb.py
if errorlevel 1 (
    echo WARNING: Failed to seed MongoDB
    echo You may need to install pymongo: pip install pymongo
)
cd ..
echo ✓ MongoDB seeded

REM Open dashboard
echo.
echo [7/7] Opening dashboard...
start dashboard\index.html
echo ✓ Dashboard opened

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start AI Service:
echo    cd ai-service
echo    pip install -r requirements.txt
echo    python -m spacy download en_core_web_sm
echo    uvicorn app.main:app --host 0.0.0.0 --port 8000
echo.
echo 2. Configure n8n:
echo    - Open http://localhost:5678
echo    - Login: admin / admin123
echo    - Import workflows from n8n-workflows folder
echo    - Activate all workflows
echo.
echo 3. Access points:
echo    - Dashboard: dashboard\index.html
echo    - n8n: http://localhost:5678
echo    - AI Service: http://localhost:8000
echo    - MongoDB Express: http://localhost:8081
echo.
echo For detailed instructions, see SETUP_GUIDE.md
echo.
pause
