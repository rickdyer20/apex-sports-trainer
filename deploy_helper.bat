@echo off
REM Basketball Analysis Service - Local Deployment Helper
REM This script helps you deploy from your Windows machine

echo 🚀 Basketball Analysis Service - Deployment Helper
echo ================================================

echo.
echo This script will help you deploy to apexsports-llc.com
echo.

set /p username="Enter your server username: "

echo.
echo Opening SSH connection to apexsports-llc.com...
echo.
echo IMPORTANT: After connecting, run these commands:
echo.
echo 1. curl -sSL https://raw.githubusercontent.com/rickdyer20/apex-sports-trainer/working-full-featured/deploy_from_git.sh ^| bash
echo 2. cd apex-sports-trainer
echo 3. gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app
echo.

REM Try to open SSH connection
ssh %username%@apexsports-llc.com

echo.
echo If SSH didn't work, you can:
echo 1. Use PuTTY or another SSH client
echo 2. Connect to: apexsports-llc.com
echo 3. Username: %username%
echo 4. Run the deployment commands shown above
echo.
pause
