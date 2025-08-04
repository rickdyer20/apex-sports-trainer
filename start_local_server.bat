@echo off
REM Start Basketball Analysis Service Locally
echo.
echo 🏀 STARTING BASKETBALL ANALYSIS SERVICE LOCALLY
echo =====================================================
echo.
echo 📍 Server will start at: http://127.0.0.1:5000
echo 📝 Upload basketball shot videos for analysis
echo 🎯 Enhanced thumb flick detection active (25° threshold)
echo.
echo ⚡ Starting server...
echo.

REM Set environment variables for local development
set FLASK_DEBUG=True
set FLASK_HOST=127.0.0.1
set PORT=5000

REM Start the Flask application
python web_app.py

pause
