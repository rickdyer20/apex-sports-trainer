@echo off
echo 🏀 Basketball Analysis - Restoring Simplified Version...
echo.

echo Stopping current processes...
taskkill /F /IM python.exe 2>nul

echo.
echo Restoring backup files...
copy "backup_simplified_version\web_app_simplified.py" "web_app.py" >nul
copy "backup_simplified_version\basketball_analysis_service_simplified.py" "basketball_analysis_service.py" >nul
copy "backup_simplified_version\results_simplified.html" "templates\results.html" >nul
copy "backup_simplified_version\ideal_shot_guide_simplified.json" "ideal_shot_guide.json" >nul
copy "backup_simplified_version\pdf_generator_simplified.py" "pdf_generator.py" >nul

echo.
echo ✅ Simplified version restored successfully!
echo.
echo To start the application:
echo    python web_app.py
echo.
echo Then visit: http://127.0.0.1:5000
echo.
pause
