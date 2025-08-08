@echo off
REM Basketball Analysis Service - Simple Upload Batch File
REM Deploy to apexsports-llc.com

echo 🚀 Basketball Analysis Service - Upload Tool
echo ================================================

REM Check if deployment package exists
if not exist "apexsports_deployment.zip" (
    echo ❌ Deployment package not found!
    echo Please run the deployment script first to create apexsports_deployment.zip
    pause
    exit /b 1
)

echo ✅ Deployment package found: apexsports_deployment.zip

echo.
echo Choose your upload method:
echo 1. SSH/SCP Upload (requires OpenSSH)
echo 2. Show FTP instructions
echo 3. Show manual upload steps
echo 4. Exit

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto ssh_upload
if "%choice%"=="2" goto ftp_instructions
if "%choice%"=="3" goto manual_instructions
goto end

:ssh_upload
echo.
echo 🔐 SSH/SCP Upload Setup
echo ========================

set /p username="Enter your server username: "
set /p server_path="Web directory path (or press Enter for default): "

if "%server_path%"=="" set server_path=/home/user/public_html

echo.
echo 📊 Connection Details:
echo   Host: apexsports-llc.com
echo   User: %username%
echo   Path: %server_path%

set /p confirm="Proceed with upload? (y/n): "
if not "%confirm%"=="y" goto end

echo.
echo 📤 Uploading deployment package...
scp apexsports_deployment.zip %username%@apexsports-llc.com:%server_path%/

if errorlevel 1 (
    echo ❌ Upload failed! Check your connection and credentials.
    goto end
)

echo ✅ Deployment package uploaded!

echo.
echo 📤 Uploading setup script...
scp server_setup.sh %username%@apexsports-llc.com:%server_path%/

echo.
echo 🔧 Running server setup...
ssh %username%@apexsports-llc.com "cd %server_path% && chmod +x server_setup.sh && ./server_setup.sh"

echo.
echo ✅ Upload and setup complete!
echo 🌐 Your service should be live at: https://apexsports-llc.com
goto end

:ftp_instructions
echo.
echo 📁 FTP Upload Instructions
echo ===========================
echo.
echo 1. Download an FTP client:
echo    - FileZilla (free): https://filezilla-project.org/
echo    - WinSCP (free): https://winscp.net/
echo.
echo 2. Connect to your server:
echo    - Host: apexsports-llc.com
echo    - Username: [your hosting username]
echo    - Password: [your hosting password]
echo    - Port: 21 (FTP) or 22 (SFTP)
echo.
echo 3. Upload these files to your web directory:
echo    - apexsports_deployment.zip
echo    - server_setup.sh
echo.
echo 4. Extract the ZIP file on your server
echo 5. Run the setup script via SSH or hosting control panel
echo.
pause
goto end

:manual_instructions
echo.
echo 📋 Manual Upload Steps
echo =======================
echo.
echo Option 1 - cPanel/Hosting Control Panel:
echo   1. Login to your hosting control panel
echo   2. Go to File Manager
echo   3. Navigate to public_html (or your web directory)
echo   4. Upload apexsports_deployment.zip
echo   5. Right-click the ZIP file and select "Extract"
echo   6. Use Terminal in cPanel to run: ./server_setup.sh
echo.
echo Option 2 - Git Deployment:
echo   1. Push your code to GitHub
echo   2. SSH into your server
echo   3. Clone: git clone https://github.com/rickdyer20/apex-sports-trainer.git
echo   4. Run the deployment script
echo.
echo Option 3 - Direct File Copy:
echo   If you have direct server access, copy these files:
echo   - apexsports_deployment.zip
echo   - server_setup.sh
echo   Then extract and run setup.sh
echo.
pause
goto end

:end
echo.
echo 💰 Revenue Model Ready:
echo   🆓 Free: 1 analysis per year
echo   💵 One-time: $9.99 for 5 analyses
echo   🔥 Pro: $19.99/month unlimited
echo   🌟 Enterprise: $49.99/month premium
echo.
echo 🔐 Live Stripe Integration: Ready for real payments!
echo.
echo Thank you for using Basketball Analysis Service!
pause
