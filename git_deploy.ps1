# Basketball Analysis Service - Git Deployment Script (Windows)
# Deploy directly from local repository to apexsports-llc.com

Write-Host "🚀 Basketball Analysis Service - Git Deployment" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Host "❌ Not a git repository. Initializing..." -ForegroundColor Yellow
    git init
    git remote add origin https://github.com/rickdyer20/apex-sports-trainer.git
}

# Check git status
Write-Host "📊 Checking repository status..." -ForegroundColor Yellow
git status

# Add all deployment files
Write-Host "📁 Adding deployment files..." -ForegroundColor Yellow
git add apexsports_deployment.zip
git add server_setup.sh
git add complete_web_app.py
git add enhanced_payment_manager.py
git add user_analysis_tracker.py
git add .env
git add requirements.txt
git add wsgi_production.py
git add templates/
git add terms_of_service.md

# Commit changes
Write-Host "💾 Committing deployment package..." -ForegroundColor Yellow
git commit -m "🚀 Production deployment package - Basketball Analysis Service v9.0

- Complete web application with live Stripe integration
- Aggressive freemium model (1 analysis/year free tier)
- 4-tier pricing: Free, `$9.99 one-time, `$19.99/month Pro, `$49.99/month Enterprise
- User tracking and usage enforcement
- Legal compliance (terms, privacy policy)
- Production-ready with live payment processing
- Revenue optimization features

Ready for immediate deployment to apexsports-llc.com"

# Push to GitHub
Write-Host "📤 Pushing to GitHub repository..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Code pushed to GitHub successfully!" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "🌐 Now deploying to server..." -ForegroundColor Cyan
    Write-Host "Choose deployment method:" -ForegroundColor Yellow
    Write-Host "1. Show manual server commands" -ForegroundColor White
    Write-Host "2. Create server deployment script" -ForegroundColor White
    Write-Host "3. Exit and deploy manually later" -ForegroundColor White
    
    $choice = Read-Host "Enter choice (1-3)"
    
    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Host "📋 Manual Server Deployment Commands:" -ForegroundColor Cyan
            Write-Host "=====================================" -ForegroundColor Cyan
            Write-Host "# SSH into your server:" -ForegroundColor Green
            Write-Host "ssh your_username@apexsports-llc.com" -ForegroundColor White
            Write-Host ""
            Write-Host "# Clone the repository:" -ForegroundColor Green
            Write-Host "cd /path/to/your/website" -ForegroundColor White
            Write-Host "git clone https://github.com/rickdyer20/apex-sports-trainer.git" -ForegroundColor White
            Write-Host "cd apex-sports-trainer" -ForegroundColor White
            Write-Host ""
            Write-Host "# Extract deployment package:" -ForegroundColor Green
            Write-Host "unzip -o apexsports_deployment.zip" -ForegroundColor White
            Write-Host ""
            Write-Host "# Install dependencies:" -ForegroundColor Green
            Write-Host "pip3 install flask stripe python-dotenv gunicorn" -ForegroundColor White
            Write-Host ""
            Write-Host "# Set permissions:" -ForegroundColor Green
            Write-Host "chmod +x complete_web_app.py" -ForegroundColor White
            Write-Host "chmod 644 .env" -ForegroundColor White
            Write-Host ""
            Write-Host "# Start the service:" -ForegroundColor Green
            Write-Host "python3 complete_web_app.py  # Development" -ForegroundColor White
            Write-Host "# OR" -ForegroundColor Yellow
            Write-Host "gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app  # Production" -ForegroundColor White
        }
        
        "2" {
            # Create a deployment script for the server
            $serverScript = @"
#!/bin/bash
# Server deployment script - run this on apexsports-llc.com

echo "🚀 Deploying Basketball Analysis Service from Git..."

# Navigate to web directory (adjust path as needed)
cd /home/user/public_html

# Clone or update repository
if [ -d "apex-sports-trainer" ]; then
    echo "📄 Updating existing repository..."
    cd apex-sports-trainer
    git pull origin main
else
    echo "📥 Cloning repository..."
    git clone https://github.com/rickdyer20/apex-sports-trainer.git
    cd apex-sports-trainer
fi

# Extract deployment package
echo "📦 Extracting deployment package..."
if [ -f "apexsports_deployment.zip" ]; then
    unzip -o apexsports_deployment.zip
    echo "✅ Deployment package extracted"
else
    echo "⚠️  Using individual files from repository"
fi

# Install dependencies
echo "📚 Installing Python dependencies..."
pip3 install flask stripe python-dotenv gunicorn

# Set permissions
echo "🔒 Setting file permissions..."
chmod +x complete_web_app.py
chmod 644 .env

# Test application
echo "🧪 Testing application..."
python3 -c "import complete_web_app; print('✅ Application ready!')"

echo ""
echo "🎉 Deployment complete!"
echo "🌐 Your Basketball Analysis Service is ready!"
echo ""
echo "Start your service with one of these commands:"
echo "Development: python3 complete_web_app.py"
echo "Production: gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app"
echo "Background: nohup gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app > service.log 2>&1 &"
echo ""
echo "💰 Revenue Model: Free (1/year), One-time (`$9.99), Pro (`$19.99/month), Enterprise (`$49.99/month)"
echo "🔐 Live Stripe Integration: Ready for real payments!"
echo "🌐 Visit: https://apexsports-llc.com"
"@
            
            $serverScript | Out-File -FilePath "deploy_from_git.sh" -Encoding UTF8
            Write-Host "✅ Created deploy_from_git.sh script" -ForegroundColor Green
            Write-Host "📤 Upload this script to your server and run it!" -ForegroundColor Yellow
        }
        
        "3" {
            Write-Host "🎯 Repository updated! Deploy manually when ready." -ForegroundColor Green
        }
    }
    
} else {
    Write-Host "❌ Failed to push to GitHub. Check your credentials and try again." -ForegroundColor Red
}

Write-Host ""
Write-Host "💰 Revenue Model Ready:" -ForegroundColor Green
Write-Host "  🆓 Free: 1 analysis per year" -ForegroundColor White
Write-Host "  💵 One-time: `$9.99 for 5 analyses" -ForegroundColor White
Write-Host "  🔥 Pro: `$19.99/month unlimited" -ForegroundColor White
Write-Host "  🌟 Enterprise: `$49.99/month premium" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Live Stripe Integration: Ready for real payments!" -ForegroundColor Magenta
