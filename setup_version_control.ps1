# Quick Setup Script for APEX SPORTS, LLC Version Control
# Run this in PowerShell from your project directory

Write-Host "🚀 Setting up version control for APEX SPORTS, LLC Basketball Analysis Service" -ForegroundColor Green

# Check if Git is installed
try {
    $gitVersion = git --version
    Write-Host "✅ Git is installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git not found. Please install Git from https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}

# Check if we're in the right directory
if (!(Test-Path "basketball_analysis_service.py")) {
    Write-Host "❌ Please run this script from your basketball analysis project directory" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Setting up Git repository..." -ForegroundColor Yellow

# Initialize Git repository if not already done
if (!(Test-Path ".git")) {
    git init
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository already exists" -ForegroundColor Green
}

# Create .gitignore file
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
temp/
tmp/
*.tmp

# Sensitive data
config.ini
secrets/
*.key
*.pem

# Basketball analysis specific
debug_frame_*.jpg
temp_*_frames/
output_videos/
analysis_reports/

# Google Cloud
.gcloudignore
"@

if (!(Test-Path ".gitignore")) {
    $gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host "✅ .gitignore file created" -ForegroundColor Green
} else {
    Write-Host "✅ .gitignore file already exists" -ForegroundColor Green
}

# Configure Git user (if not already configured)
$userName = git config user.name
$userEmail = git config user.email

if (!$userName) {
    $name = Read-Host "Enter your name for Git commits"
    git config user.name $name
    Write-Host "✅ Git user name configured" -ForegroundColor Green
}

if (!$userEmail) {
    $email = Read-Host "Enter your email for Git commits"
    git config user.email $email
    Write-Host "✅ Git user email configured" -ForegroundColor Green
}

# Add all files and create initial commit
Write-Host "📦 Adding files to Git..." -ForegroundColor Yellow
git add .

# Check if there are any commits already
$commitCount = git rev-list --count HEAD 2>$null
if ($LASTEXITCODE -ne 0) {
    # No commits yet, create initial commit
    git commit -m "Initial commit: APEX SPORTS LLC Basketball Analysis Service v9.0

    - Complete AI basketball shot analysis service
    - MediaPipe pose estimation integration  
    - Production-ready Google Cloud deployment
    - Professional business entity: EIN 39-3553235
    - Live domain: apexsports-llc.com"
    
    # Tag the initial version
    git tag -a v9.0 -m "Version 9.0: Initial production release"
    
    Write-Host "✅ Initial commit created and tagged as v9.0" -ForegroundColor Green
} else {
    Write-Host "✅ Repository already has commits" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Create a GitHub account at https://github.com" -ForegroundColor White
Write-Host "2. Create a new repository called 'apex-sports-basketball-analysis'" -ForegroundColor White
Write-Host "3. Run these commands to connect to GitHub:" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/YOURUSERNAME/apex-sports-basketball-analysis.git" -ForegroundColor Gray
Write-Host "   git branch -M main" -ForegroundColor Gray
Write-Host "   git push -u origin main" -ForegroundColor Gray
Write-Host "   git push origin v9.0" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 See VERSION_CONTROL_GUIDE.md for complete instructions" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎉 Version control setup complete! Your code is now protected." -ForegroundColor Green
