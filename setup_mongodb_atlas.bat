@echo off
REM Setup script for MongoDB Atlas migration

echo ========================================
echo MongoDB Atlas Setup
echo ========================================
echo.

echo Database: gov_ai_assistant
echo Cluster: rtgsai.pjyqjep.mongodb.net
echo.

REM Check if mongosh is installed
echo [1/3] Checking for MongoDB Shell (mongosh)...
where mongosh >nul 2>&1
if errorlevel 1 (
    echo WARNING: mongosh not found
    echo.
    echo Please install MongoDB Shell:
    echo https://www.mongodb.com/try/download/shell
    echo.
    echo Or run the initialization script manually:
    echo mongosh "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/gov_ai_assistant" ^< database\init_atlas.js
    echo.
    pause
    exit /b 1
)
echo ✓ mongosh found

echo.
echo [2/3] Connecting to MongoDB Atlas...
echo This may take a few seconds...
echo.

REM Run initialization script
mongosh "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/gov_ai_assistant" < database\init_atlas.js

if errorlevel 1 (
    echo.
    echo ERROR: Failed to initialize MongoDB Atlas
    echo.
    echo Possible issues:
    echo - Network connectivity
    echo - IP not whitelisted in MongoDB Atlas
    echo - Invalid credentials
    echo.
    echo Please check MongoDB Atlas dashboard and try again
    pause
    exit /b 1
)

echo.
echo [3/3] Verifying connection...

REM Test connection
mongosh "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/gov_ai_assistant" --eval "db.getCollectionNames()"

echo.
echo ========================================
echo MongoDB Atlas Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Update n8n MongoDB credentials:
echo    - Open http://localhost:5678
echo    - Go to Credentials ^> MongoDB
echo    - Connection String: mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/gov_ai_assistant
echo.
echo 2. Start n8n:
echo    docker-compose up -d
echo.
echo 3. Import workflows and test
echo.
pause
