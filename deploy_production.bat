@echo off
REM Windows Production Deployment Script
REM Government AI Personal Assistant - NTR District

echo ============================================================
echo         Production Deployment - RTGS AI Assistant
echo                 NTR District (Vijayawada)
echo ============================================================
echo.

REM Step 1: Pre-deployment validation
echo [1/8] Running pre-deployment validation...
python pre_deployment_check.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Pre-deployment validation failed!
    echo Please fix the issues and try again.
    pause
    exit /b 1
)
echo [OK] Pre-deployment validation passed
echo.

REM Step 2: Create backup
echo [2/8] Creating backup...
set BACKUP_NAME=backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_NAME=%BACKUP_NAME: =0%
mkdir backup 2>nul
tar -czf backup\%BACKUP_NAME%.tar.gz dashboard\.env.local docker-compose.yml n8n-workflows 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backup created: backup\%BACKUP_NAME%.tar.gz
) else (
    echo [WARNING] Backup creation failed or tar not available
)
echo.

REM Step 3: Stop current services
echo [3/8] Stopping current services...
docker-compose down
echo [OK] Docker services stopped
echo.

REM Step 4: Clean up n8n workflows (remove duplicates)
echo [4/8] Cleaning up n8n workflows...
python final_cleanup_dashboard.py
echo [OK] Workflow cleanup completed
echo.

REM Step 5: Start Docker services
echo [5/8] Starting Docker services...
docker-compose up -d
echo Waiting 30 seconds for services to initialize...
timeout /t 30 /nobreak >nul
echo [OK] Docker services started
echo.

REM Step 6: Build dashboard for production
echo [6/8] Building dashboard for production...
cd dashboard
call npm install --production
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Dashboard build failed!
    cd ..
    pause
    exit /b 1
)
cd ..
echo [OK] Dashboard built successfully
echo.

REM Step 7: Start dashboard in production mode
echo [7/8] Starting dashboard in production mode...
cd dashboard
start /B npm start
cd ..
echo [OK] Dashboard started
echo.

REM Step 8: Final health checks
echo [8/8] Running health checks...
timeout /t 10 /nobreak >nul

REM Check Docker services
docker ps | findstr "ai-assist-n8n" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] n8n container is running
) else (
    echo [ERROR] n8n container is NOT running
)

docker ps | findstr "ai-assist-ai-service" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] AI service container is running
) else (
    echo [ERROR] AI service container is NOT running
)

REM Check dashboard
curl -s http://localhost:3000 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Dashboard is responding
) else (
    echo [WARNING] Dashboard may still be starting up
)

echo.
echo ============================================================
echo              DEPLOYMENT COMPLETED SUCCESSFULLY
echo ============================================================
echo.
echo Services are now running:
echo   - Dashboard:   http://localhost:3000
echo   - n8n Admin:   http://localhost:5678
echo   - AI Service:  http://localhost:8000
echo.
echo Backup saved to: backup\%BACKUP_NAME%.tar.gz
echo.
echo Next Steps:
echo   1. Test the dashboard at http://localhost:3000
echo   2. Configure production domain and SSL (if needed)
echo   3. Update Telegram webhook URL (if needed)
echo   4. Monitor logs for any issues
echo.
echo To view logs:
echo   docker logs ai-assist-n8n
echo   docker logs ai-assist-ai-service
echo.
pause
