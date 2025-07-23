# Basketball Analysis Service - Development Deployment Script
# PowerShell script for Windows development environment

Write-Host "🏀 Basketball Analysis Service - Development Deployment" -ForegroundColor Cyan

# Step 1: Environment Setup
Write-Host "`n📋 Step 1: Environment Verification" -ForegroundColor Yellow
Write-Host "Checking Python environment..."
python --version
Write-Host "Checking required dependencies..."
pip list | Select-String "flask|opencv|mediapipe|pytest"

# Step 2: Database Setup
Write-Host "`n💾 Step 2: Database Initialization" -ForegroundColor Yellow
Write-Host "Setting up development database..."
python setup_sqlite_db.py

# Step 3: Test Suite
Write-Host "`n🧪 Step 3: Running Core Tests" -ForegroundColor Yellow
Write-Host "Executing test suite..."
python -m pytest test_basketball_analysis.py -v --tb=short

# Step 4: Web Application
Write-Host "`n🌐 Step 4: Starting Web Application" -ForegroundColor Yellow
Write-Host "Web application will start on http://localhost:5000"
Write-Host "Press Ctrl+C to stop the server"
Write-Host ""

# Start the Flask application
python web_app.py
