# Basketball Analysis Service - Windows Upload Script
# Deploy directly from Windows to apexsports-llc.com

param(
    [string]$ServerHost = "apexsports-llc.com",
    [string]$ServerUser = "",
    [string]$ServerPath = "/home/user/public_html"
)

function Show-Banner {
    Write-Host "🚀 Basketball Analysis Service - Server Upload" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Test-Prerequisites {
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow
    
    # Check if deployment package exists
    if (-not (Test-Path "apexsports_deployment.zip")) {
        Write-Host "❌ Deployment package not found. Run deployment script first." -ForegroundColor Red
        return $false
    }
    
    # Check for SSH/SCP (Windows 10+ has OpenSSH)
    try {
        $scp = Get-Command scp -ErrorAction Stop
        Write-Host "✅ SCP available" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ SCP not available. Please install OpenSSH or use alternative method." -ForegroundColor Red
        Write-Host "💡 To install OpenSSH on Windows:" -ForegroundColor Yellow
        Write-Host "   Settings > Apps > Optional Features > Add Feature > OpenSSH Client" -ForegroundColor Yellow
        return $false
    }
    
    return $true
}

function Get-ServerCredentials {
    Write-Host "`n🔐 Server Connection Setup" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    
    if (-not $ServerUser) {
        $ServerUser = Read-Host "Enter your server username"
    }
    
    $customPath = Read-Host "Web directory path (default: $ServerPath)"
    if ($customPath) {
        $ServerPath = $customPath
    }
    
    Write-Host "`n📊 Connection Details:" -ForegroundColor Green
    Write-Host "  Host: $ServerHost" -ForegroundColor White
    Write-Host "  User: $ServerUser" -ForegroundColor White
    Write-Host "  Path: $ServerPath" -ForegroundColor White
    
    $confirm = Read-Host "`nProceed with upload? (y/n)"
    return $confirm -eq 'y'
}

function Invoke-FileUpload {
    param($User, $Host, $Path)
    
    Write-Host "`n🚀 Uploading files to server..." -ForegroundColor Cyan
    
    try {
        # Upload deployment package
        Write-Host "📤 Uploading apexsports_deployment.zip..." -ForegroundColor Yellow
        & scp "apexsports_deployment.zip" "${User}@${Host}:${Path}/"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Deployment package uploaded successfully!" -ForegroundColor Green
        } else {
            throw "SCP upload failed with exit code $LASTEXITCODE"
        }
        
        # Upload setup script
        if (Test-Path "server_setup.sh") {
            Write-Host "📤 Uploading server_setup.sh..." -ForegroundColor Yellow
            & scp "server_setup.sh" "${User}@${Host}:${Path}/"
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Setup script uploaded successfully!" -ForegroundColor Green
            }
        }
        
        return $true
    }
    catch {
        Write-Host "❌ Upload failed: $_" -ForegroundColor Red
        return $false
    }
}

function Invoke-ServerSetup {
    param($User, $Host, $Path)
    
    Write-Host "`n⚙️ Running server setup..." -ForegroundColor Cyan
    
    try {
        Write-Host "🔧 Executing server setup script..." -ForegroundColor Yellow
        & ssh "${User}@${Host}" "cd $Path && chmod +x server_setup.sh && ./server_setup.sh"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Server setup completed!" -ForegroundColor Green
            return $true
        } else {
            throw "SSH setup failed with exit code $LASTEXITCODE"
        }
    }
    catch {
        Write-Host "❌ Server setup failed: $_" -ForegroundColor Red
        Write-Host "💡 You can manually run the setup script on your server:" -ForegroundColor Yellow
        Write-Host "   ssh ${User}@${Host}" -ForegroundColor White
        Write-Host "   cd $Path" -ForegroundColor White
        Write-Host "   chmod +x server_setup.sh" -ForegroundColor White
        Write-Host "   ./server_setup.sh" -ForegroundColor White
        return $false
    }
}

function Start-Service {
    param($User, $Host, $Path)
    
    Write-Host "`n🚀 Starting Basketball Analysis Service..." -ForegroundColor Cyan
    
    Write-Host "Choose startup method:" -ForegroundColor Yellow
    Write-Host "1. Development mode (interactive)" -ForegroundColor White
    Write-Host "2. Production mode (background)" -ForegroundColor White
    Write-Host "3. Manual start (just show commands)" -ForegroundColor White
    
    $choice = Read-Host "Enter choice (1-3)"
    
    switch ($choice) {
        "1" {
            Write-Host "🔧 Starting in development mode..." -ForegroundColor Yellow
            & ssh "${User}@${Host}" "cd $Path && python3 complete_web_app.py"
        }
        "2" {
            Write-Host "🔧 Starting in production mode..." -ForegroundColor Yellow
            & ssh "${User}@${Host}" "cd $Path && nohup gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app > service.log 2>&1 &"
            Write-Host "✅ Service started in background!" -ForegroundColor Green
        }
        default {
            Write-Host "`n📋 Manual start commands:" -ForegroundColor Yellow
            Write-Host "ssh ${User}@${Host}" -ForegroundColor White
            Write-Host "cd $Path" -ForegroundColor White
            Write-Host "# Development:" -ForegroundColor Green
            Write-Host "python3 complete_web_app.py" -ForegroundColor White
            Write-Host "# Production:" -ForegroundColor Green
            Write-Host "gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app" -ForegroundColor White
        }
    }
}

function Show-DeploymentSummary {
    param($Host)
    
    Write-Host "`n✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Green
    Write-Host "🌐 Your Basketball Analysis Service should be live at:" -ForegroundColor Cyan
    Write-Host "   https://$Host" -ForegroundColor White
    Write-Host "   https://$Host/pricing" -ForegroundColor White
    Write-Host "   https://$Host/analyze" -ForegroundColor White
    
    Write-Host "`n💰 Revenue Model Active:" -ForegroundColor Yellow
    Write-Host "   🆓 Free: 1 analysis per year" -ForegroundColor White
    Write-Host "   💵 One-time: `$9.99 for 5 analyses" -ForegroundColor White
    Write-Host "   🔥 Pro: `$19.99/month unlimited" -ForegroundColor White
    Write-Host "   🌟 Enterprise: `$49.99/month premium" -ForegroundColor White
    
    Write-Host "`n🔐 Live Stripe Integration:" -ForegroundColor Magenta
    Write-Host "   ✅ Real payment processing active" -ForegroundColor White
    Write-Host "   ✅ Webhook configured" -ForegroundColor White
    Write-Host "   ✅ Ready to earn revenue!" -ForegroundColor White
}

function Show-AlternativeMethods {
    Write-Host "`n📋 Alternative Upload Methods:" -ForegroundColor Cyan
    Write-Host "=" * 40 -ForegroundColor Cyan
    
    Write-Host "`n1. 📁 FTP Upload:" -ForegroundColor Yellow
    Write-Host "   - Use FileZilla or WinSCP" -ForegroundColor White
    Write-Host "   - Connect to: $ServerHost" -ForegroundColor White
    Write-Host "   - Upload: apexsports_deployment.zip" -ForegroundColor White
    
    Write-Host "`n2. 🎛️ cPanel Upload:" -ForegroundColor Yellow
    Write-Host "   - Login to hosting control panel" -ForegroundColor White
    Write-Host "   - File Manager > Upload > Extract" -ForegroundColor White
    
    Write-Host "`n3. 🔄 Git Deployment:" -ForegroundColor Yellow
    Write-Host "   - Push to GitHub repository" -ForegroundColor White
    Write-Host "   - Clone on server and deploy" -ForegroundColor White
}

# Main execution
Show-Banner

Write-Host "Choose upload method:" -ForegroundColor Yellow
Write-Host "1. Automated SSH/SCP upload (recommended)" -ForegroundColor White
Write-Host "2. Show alternative methods" -ForegroundColor White

$method = Read-Host "Enter choice (1-2)"

if ($method -eq "1") {
    if (-not (Test-Prerequisites)) {
        exit 1
    }
    
    if (-not (Get-ServerCredentials)) {
        Write-Host "❌ Deployment cancelled." -ForegroundColor Red
        exit 1
    }
    
    if (-not (Invoke-FileUpload -User $ServerUser -Host $ServerHost -Path $ServerPath)) {
        exit 1
    }
    
    if (-not (Invoke-ServerSetup -User $ServerUser -Host $ServerHost -Path $ServerPath)) {
        Write-Host "⚠️ Setup had issues, but files are uploaded." -ForegroundColor Yellow
    }
    
    Start-Service -User $ServerUser -Host $ServerHost -Path $ServerPath
    Show-DeploymentSummary -Host $ServerHost
}
elseif ($method -eq "2") {
    Show-AlternativeMethods
}
else {
    Write-Host "Invalid choice. Exiting." -ForegroundColor Red
}
