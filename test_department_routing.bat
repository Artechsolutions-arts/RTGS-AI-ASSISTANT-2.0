@echo off
REM Test script for Multi-Department WhatsApp Routing
REM Tests messages from Pava, Santosh, and Ramya

echo ========================================
echo Multi-Department WhatsApp Routing Test
echo ========================================
echo.

REM Check if n8n is running
echo [1/4] Checking if n8n is accessible...
curl -s http://localhost:5678/healthz >nul 2>&1
if errorlevel 1 (
    echo ERROR: n8n is not running on port 5678
    echo Please start n8n first: docker-compose up -d
    pause
    exit /b 1
)
echo ✓ n8n is running

echo.
echo [2/4] Testing message from Pava (Disaster Management)...
curl -X POST http://localhost:5678/webhook/department-update ^
  -H "Content-Type: application/json" ^
  -d "{\"from\": \"+919876543210\", \"message\": \"Heavy rainfall in Vijayawada. Flood alert issued. Evacuation in progress in low-lying areas.\", \"timestamp\": \"%date% %time%\"}"

echo.
echo.
echo [3/4] Testing message from Santosh (Electricity)...
timeout /t 2 /nobreak >nul
curl -X POST http://localhost:5678/webhook/department-update ^
  -H "Content-Type: application/json" ^
  -d "{\"from\": \"+919876543211\", \"message\": \"Power outage in Krishna district due to transformer failure. Restoration expected in 2 hours.\", \"timestamp\": \"%date% %time%\"}"

echo.
echo.
echo [4/4] Testing message from Ramya (Infrastructure)...
timeout /t 2 /nobreak >nul
curl -X POST http://localhost:5678/webhook/department-update ^
  -H "Content-Type: application/json" ^
  -d "{\"from\": \"+919876543212\", \"message\": \"Road damage reported on NH-16 near Guntur. Traffic diverted. Repair work scheduled for tomorrow.\", \"timestamp\": \"%date% %time%\"}"

echo.
echo.
echo ========================================
echo Test Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Check n8n executions at http://localhost:5678
echo 2. Verify MongoDB has messages: docker exec -i ai-assist-mongodb mongosh gov_ai_assistant --eval "db.messages.find().pretty()"
echo 3. Check console logs for WhatsApp group messages
echo.
echo Note: WhatsApp sending is currently simulated (logged to console)
echo For production, configure WhatsApp Business API credentials in the workflow
echo.
pause
