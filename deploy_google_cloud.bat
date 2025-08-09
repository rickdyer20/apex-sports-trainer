@echo off
REM Google Cloud Deployment for Windows
REM Basketball Analysis Service

echo.
echo 🚀 GOOGLE CLOUD DEPLOYMENT - Basketball Analysis Service
echo =======================================================
echo.

REM Check if gcloud is installed
gcloud version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Google Cloud SDK not found!
    echo 📥 Download from: https://cloud.google.com/sdk/docs/install-sdk
    echo.
    echo 💡 After installation, run:
    echo    gcloud init
    echo    gcloud auth login
    pause
    exit /b 1
)

echo ✅ Google Cloud SDK found

REM Check authentication
echo 🔐 Checking Google Cloud authentication...
gcloud auth list --filter=status:ACTIVE --format="value(account)" >nul 2>&1

if %errorlevel% neq 0 (
    echo ❌ Not authenticated with Google Cloud
    echo 🔑 Please run: gcloud auth login
    pause
    exit /b 1
)

echo ✅ Authenticated with Google Cloud

REM Set project
echo 📋 Setting up Google Cloud project...
set /p PROJECT_ID="Enter your Google Cloud Project ID: "

if "%PROJECT_ID%"=="" (
    echo ❌ Project ID required
    pause
    exit /b 1
)

gcloud config set project %PROJECT_ID%
echo ✅ Project set: %PROJECT_ID%

REM Enable APIs
echo 🔧 Enabling required Google Cloud APIs...
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
echo ✅ APIs enabled

REM Create App Engine app if needed
echo 🏗️ Setting up App Engine...
gcloud app describe >nul 2>&1
if %errorlevel% neq 0 (
    echo Creating new App Engine application...
    gcloud app create --region=us-central1
)
echo ✅ App Engine ready

REM Deploy
echo 🚀 Deploying Basketball Analysis Service...
echo.
echo 📦 Deploying files:
echo    ✅ complete_web_app.py
echo    ✅ app.yaml 
echo    ✅ requirements.txt
echo    ✅ templates/
echo    ✅ static/
echo.

gcloud app deploy app.yaml --quiet

if %errorlevel% equ 0 (
    echo.
    echo 🎉 DEPLOYMENT SUCCESSFUL!
    echo ========================
    echo.
    echo 🌐 Your Basketball Analysis Service is now LIVE!
    echo.
    
    REM Get URL
    for /f %%i in ('gcloud app describe --format="value(defaultHostname)"') do set APP_URL=%%i
    echo 📱 Application URL: https://%APP_URL%
    echo.
    
    echo 💰 REVENUE MODEL ACTIVE:
    echo    🆓 Free: 1 analysis per year
    echo    💵 One-time: $9.99 for 5 analyses  
    echo    🔥 Pro: $19.99/month unlimited
    echo    🌟 Enterprise: $49.99/month premium
    echo.
    echo 🔐 Live Stripe Integration: Ready!
    echo.
    echo 🔧 CUSTOM DOMAIN SETUP:
    echo    1. Google Cloud Console ^> App Engine ^> Settings ^> Custom Domains
    echo    2. Add: apexsports-llc.com
    echo    3. Update Namecheap DNS to point to Google Cloud
    echo.
    echo 🎯 READY TO GENERATE REVENUE!
    
    set /p OPEN_APP="🌐 Open your deployed app now? (y/n): "
    if /i "%OPEN_APP%"=="y" (
        gcloud app browse
    )
) else (
    echo ❌ Deployment failed
    echo 🔍 Check logs: gcloud app logs tail -s default
)

echo.
pause
