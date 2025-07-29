#!/usr/bin/env python3
"""
Railway Deployment Script for Basketball Analysis Service
Python version for cross-platform compatibility
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header():
    """Print deployment header"""
    print("🚂 Basketball Analysis Service - Railway Deployment")
    print("=" * 66)

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], 
                              capture_output=True, text=True, check=True)
        print("✅ Railway CLI found:", result.stdout.strip())
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Railway CLI not found. Please install it first:")
        print("   npm install -g @railway/cli")
        print("   Or visit: https://docs.railway.app/quick-start")
        return False

def check_railway_auth():
    """Check if user is logged in to Railway"""
    try:
        result = subprocess.run(['railway', 'whoami'], 
                              capture_output=True, text=True, check=True)
        print("✅ Railway authentication verified:", result.stdout.strip())
        return True
    except subprocess.CalledProcessError:
        print("❌ Please log in to Railway first:")
        print("   railway login")
        return False

def validate_files():
    """Validate required files exist"""
    required_files = [
        "web_app.py",
        "basketball_analysis_service.py", 
        "wsgi.py",
        "requirements.txt",
        "Dockerfile",
        "railway.json",
        "ideal_shot_guide.json"
    ]
    
    print("🔍 Validating required files...")
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def show_config():
    """Display deployment configuration"""
    print("")
    print("🔧 Deployment Configuration:")
    print("   • Platform: Railway")
    print("   • Runtime: Python 3.11")
    print("   • Framework: Flask + Gunicorn")
    print("   • Container: Docker")
    print("   • Optimizations: CPU-only processing, reduced timeouts")
    print("   • Health Check: /health endpoint")
    print("   • Auto-restart: On failure (max 10 retries)")
    print("")

def create_railwayignore():
    """Create .railwayignore file if it doesn't exist"""
    railwayignore_path = Path(".railwayignore")
    
    if railwayignore_path.exists():
        print("✅ .railwayignore already exists")
        return
    
    print("📝 Creating .railwayignore...")
    
    railwayignore_content = """# Railway Ignore File
# Files and directories to exclude from Railway deployment

# Development files
*.pyc
__pycache__/
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.env
.env.local
.env.development

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/

# Documentation
docs/
*.md
!README.md

# Version control
.git/
.gitignore
.gitattributes

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary files
*.tmp
*.temp
temp/
tmp/

# Local data (will be recreated)
uploads/*.mp4
uploads/*.avi
uploads/*.mov
results/*.mp4
results/*.png
results/*.pdf
jobs/*.json
logs/*.log

# Node modules (if any)
node_modules/
"""
    
    railwayignore_path.write_text(railwayignore_content.strip())
    print("✅ Created .railwayignore")

def set_environment_variables():
    """Set Railway environment variables"""
    print("🌍 Setting Railway environment variables...")
    
    env_vars = {
        # Performance optimizations
        'TF_CPP_MIN_LOG_LEVEL': '2',
        'CUDA_VISIBLE_DEVICES': '',
        'TF_ENABLE_ONEDNN_OPTS': '0',
        'MEDIAPIPE_DISABLE_GPU': '1',
        
        # Flask configuration
        'FLASK_ENV': 'production',
        'FLASK_DEBUG': 'false',
        'FLASK_HOST': '0.0.0.0',
        
        # Application settings
        'PYTHONUNBUFFERED': '1',
    }
    
    for key, value in env_vars.items():
        try:
            result = subprocess.run(
                ['railway', 'variables', 'set', f'{key}={value}'],
                capture_output=True, text=True, check=True
            )
            print(f"   ✅ {key}={value}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to set {key}: {e}")
            return False
    
    print("✅ Environment variables configured")
    return True

def deploy_to_railway():
    """Deploy to Railway"""
    print("🚀 Starting Railway deployment...")
    print("")
    print("   This will:")
    print("   1. Build the Docker container with optimizations")
    print("   2. Deploy to Railway with health checks")
    print("   3. Set up auto-scaling and monitoring")
    print("")
    
    confirm = input("   Continue with deployment? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Deployment cancelled")
        return False
    
    try:
        # Deploy using Railway CLI
        print("🚀 Deploying to Railway...")
        result = subprocess.run(
            ['railway', 'up', '--detach'],
            capture_output=True, text=True, check=True
        )
        print("✅ Deployment started!")
        
        # Get deployment status
        print("")
        print("📊 Monitoring deployment...")
        status_result = subprocess.run(
            ['railway', 'status'],
            capture_output=True, text=True
        )
        if status_result.returncode == 0:
            print(status_result.stdout)
        
        # Try to get service URL
        print("")
        print("🌐 Getting service URL...")
        try:
            domain_result = subprocess.run(
                ['railway', 'domain'],
                capture_output=True, text=True, check=True
            )
            service_url = domain_result.stdout.strip()
            
            print("🎉 Deployment successful!")
            print("")
            print("🌐 Your Basketball Analysis Service is available at:")
            print(f"   {service_url}")
            print("")
            print(f"🔍 Health check: {service_url}/health")
            print(f"📊 Upload page: {service_url}/")
            print("")
            
        except subprocess.CalledProcessError:
            print("⏳ Deployment in progress...")
            print("   Run 'railway domain' to get the URL once deployment completes")
            print("   Run 'railway logs' to monitor deployment progress")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        print("Error output:", e.stderr)
        return False

def show_post_deployment_info():
    """Show post-deployment information"""
    print("")
    print("📋 Post-Deployment Commands:")
    print("   • View logs:     railway logs")
    print("   • Check status:  railway status")
    print("   • Open service:  railway open")
    print("   • View metrics:  railway metrics")
    print("   • Scale service: railway scale")
    print("")
    print("🛠️  Management:")
    print("   • Environment variables: railway variables")
    print("   • Database setup: railway add (if needed)")
    print("   • Custom domain: railway domain add <domain>")
    print("")
    print("🎯 Performance Optimizations Applied:")
    print("   • CPU-only processing (no GPU dependencies)")
    print("   • Optimized MediaPipe settings")
    print("   • Reduced TensorFlow logging")
    print("   • Production Flask configuration")
    print("   • Gunicorn with 2 workers and thread pooling")
    print("")

def main():
    """Main deployment process"""
    print_header()
    print("Starting Basketball Analysis Service deployment to Railway...")
    print("")
    
    # Validation steps
    if not check_railway_cli():
        return 1
    
    if not check_railway_auth():
        return 1
    
    if not validate_files():
        return 1
    
    # Deployment steps
    show_config()
    create_railwayignore()
    
    if not set_environment_variables():
        return 1
    
    if not deploy_to_railway():
        return 1
    
    show_post_deployment_info()
    
    print("🎉 Railway deployment process completed!")
    print("")
    print("Your optimized Basketball Analysis Service is now running on Railway")
    print("with all performance optimizations that made localhost work perfectly!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
