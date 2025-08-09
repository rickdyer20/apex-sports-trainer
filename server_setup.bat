@echo off
REM Server Setup Script for apexsports-llc.com (Windows)
REM Run this on your Windows server after uploading

echo 🚀 Setting up Basketball Analysis Service...

REM Extract deployment package
powershell -command "Expand-Archive -Path apexsports_deployment.zip -DestinationPath . -Force"
echo ✅ Files extracted

REM Install Python dependencies
pip install flask stripe python-dotenv gunicorn
echo ✅ Dependencies installed

REM Test the application
python -c "import complete_web_app; print('✅ Application imports successfully')"

echo 🚀 Starting Basketball Analysis Service...
echo Choose startup method:
echo 1. Development: python complete_web_app.py
echo 2. Production: gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app

echo.
echo 🎉 Setup complete! Your service is ready to go live!
echo Visit: https://apexsports-llc.com
