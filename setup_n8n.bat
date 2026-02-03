@echo off
REM ============================================
REM N8N Quick Setup Script
REM Government of Andhra Pradesh AI Assistant
REM ============================================

echo.
echo ========================================
echo N8N SETUP - Government AI Assistant
echo ========================================
echo.

REM Check if Docker is installed
echo [1/7] Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Docker is not installed!
    echo.
    echo Please install Docker Desktop:
    echo https://www.docker.com/products/docker-desktop
    echo.
    echo After installation:
    echo 1. Restart your computer
    echo 2. Run this script again
    echo.
    pause
    exit /b 1
)
echo [OK] Docker is installed
echo.

REM Check if Docker is running
echo [2/7] Checking if Docker is running...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Docker is not running!
    echo.
    echo Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)
echo [OK] Docker is running
echo.

REM Stop existing containers
echo [3/7] Stopping existing containers...
docker-compose down >nul 2>&1
echo [OK] Containers stopped
echo.

REM Start all services
echo [4/7] Starting all services...
echo This may take 2-3 minutes...
docker-compose up -d
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start containers!
    echo.
    echo Check docker-compose.yml for errors.
    echo.
    pause
    exit /b 1
)
echo [OK] Services started
echo.

REM Wait for services to be ready
echo [5/7] Waiting for services to initialize...
timeout /t 30 /nobreak >nul
echo [OK] Services should be ready
echo.

REM Check if services are running
echo [6/7] Verifying services...
docker ps | findstr "mongodb" >nul
if %errorlevel% neq 0 (
    echo [WARNING] MongoDB may not be running
) else (
    echo [OK] MongoDB is running
)

docker ps | findstr "postgres" >nul
if %errorlevel% neq 0 (
    echo [WARNING] PostgreSQL may not be running
) else (
    echo [OK] PostgreSQL is running
)

docker ps | findstr "n8n" >nul
if %errorlevel% neq 0 (
    echo [WARNING] n8n may not be running
) else (
    echo [OK] n8n is running
)

docker ps | findstr "mongo-express" >nul
if %errorlevel% neq 0 (
    echo [WARNING] MongoDB Express may not be running
) else (
    echo [OK] MongoDB Express is running
)
echo.

REM Display access URLs
echo [7/7] Setup complete!
echo.
echo ========================================
echo ACCESS URLS
echo ========================================
echo.
echo n8n Dashboard:
echo   http://localhost:5678
echo.
echo MongoDB Express:
echo   http://localhost:8081
echo.
echo AI Service (if running):
echo   http://localhost:8000/health
echo.
echo ========================================
echo NEXT STEPS
echo ========================================
echo.
echo 1. Open n8n: http://localhost:5678
echo 2. Create admin account (first time)
echo 3. Configure MongoDB credentials:
echo    - Host: mongodb
echo    - Port: 27017
echo    - Database: gov_ai_assistant
echo 4. Import workflows from n8n-workflows/ folder
echo 5. Activate each workflow
echo 6. Test with webhook
echo.
echo See N8N_SETUP_GUIDE.md for detailed instructions
echo.
echo ========================================
echo.

REM Ask if user wants to open n8n
set /p OPEN_N8N="Open n8n in browser now? (Y/N): "
if /i "%OPEN_N8N%"=="Y" (
    start http://localhost:5678
)

echo.
echo Press any key to exit...
pause >nul
