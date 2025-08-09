@echo off
REM Namecheap Deployment for Windows PowerShell
REM Basketball Analysis Service Deployment

echo.
echo 🚀 NAMECHEAP DEPLOYMENT - Basketball Analysis Service
echo ===================================================
echo.

echo 📋 STEP 1: Find Your Namecheap Username
echo.
echo 1. Go to namecheap.com and login
echo 2. Navigate to: Account ^> Dashboard ^> Manage (next to apexsports-llc.com)
echo 3. Look for "SSH Access" or "Terminal" - your username will be displayed
echo.
echo 💡 Common usernames for apexsports-llc.com:
echo    - apexspo1
echo    - apexsports  
echo    - apexsportsllc
echo    - (your cPanel username)
echo.

set /p username="Enter your Namecheap username: "

if "%username%"=="" (
    echo ❌ Username required. Please check your Namecheap cPanel.
    pause
    exit /b 1
)

echo.
echo 📊 Connecting to: %username%@apexsports-llc.com
echo 📁 Target: /home/%username%/public_html
echo.

echo 🔍 Testing SSH connection...
ssh -o ConnectTimeout=10 %username%@apexsports-llc.com "echo Connection successful!"

if %errorlevel% equ 0 (
    echo ✅ SSH connection works!
    echo.
    echo 🚀 Deploying Basketball Analysis Service...
    
    ssh %username%@apexsports-llc.com "cd /home/%username%/public_html && if [ -d 'apex-sports-trainer' ]; then cd apex-sports-trainer && git pull origin working-full-featured; else git clone -b working-full-featured https://github.com/rickdyer20/apex-sports-trainer.git && cd apex-sports-trainer; fi && if [ -f 'apexsports_deployment.zip' ]; then unzip -o apexsports_deployment.zip; fi && pip3 install --user flask stripe python-dotenv gunicorn && chmod +x complete_web_app.py && chmod 644 .env && python3 -c 'import complete_web_app; print(\"✅ Application ready!\")' && echo '🎉 DEPLOYMENT COMPLETE!' && echo '🌐 Your Basketball Analysis Service is deployed!' && echo '📁 Location: /home/%username%/public_html/apex-sports-trainer' && echo '💰 Revenue Model: Free(1/year) | One-time($9.99) | Pro($19.99/mo) | Enterprise($49.99/mo)' && echo '🔐 Live Stripe Integration: Ready!' && echo '🚀 To start: python3 complete_web_app.py' && echo '🌐 Visit: https://apexsports-llc.com'"
    
    if %errorlevel% equ 0 (
        echo.
        echo ✅ DEPLOYMENT SUCCESSFUL!
        echo 🎉 Your Basketball Analysis Service is ready!
        echo.
        set /p startservice="🚀 Start the service now? (y/n): "
        
        if /i "%startservice%"=="y" (
            echo 🔧 Starting service...
            ssh %username%@apexsports-llc.com "cd /home/%username%/public_html/apex-sports-trainer && nohup python3 complete_web_app.py > service.log 2>&1 &"
            echo ✅ Service started!
            echo.
            echo 🌐 Your Basketball Analysis Service is now LIVE!
            echo    https://apexsports-llc.com
            echo.
            echo 💰 Revenue Generation Active:
            echo    🆓 Free: 1 analysis per year (forces upgrades)
            echo    💵 One-time: $9.99 for 5 analyses
            echo    🔥 Pro: $19.99/month unlimited
            echo    🌟 Enterprise: $49.99/month premium features
        )
    )
) else (
    echo ❌ SSH connection failed.
    echo.
    echo 💡 ALTERNATIVE: Use Namecheap cPanel
    echo    1. Login to cPanel at your Namecheap dashboard
    echo    2. Open File Manager
    echo    3. Upload apexsports_deployment.zip to public_html
    echo    4. Extract the ZIP file
    echo    5. Open Terminal in cPanel
    echo    6. Run: bash server_setup.sh
)

echo.
pause
