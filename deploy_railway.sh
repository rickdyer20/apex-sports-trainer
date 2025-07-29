#!/bin/bash
# Railway Deployment Script for Basketball Analysis Service
# This script prepares and deploys the optimized basketball analysis service to Railway

set -e  # Exit on any error

echo "🚂 Basketball Analysis Service - Railway Deployment"
echo "=================================================================="

# Function to check if Railway CLI is installed
check_railway_cli() {
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI not found. Please install it first:"
        echo "   npm install -g @railway/cli"
        echo "   Or visit: https://docs.railway.app/quick-start"
        exit 1
    fi
    echo "✅ Railway CLI found"
}

# Function to check if user is logged in to Railway
check_railway_auth() {
    if ! railway auth &> /dev/null; then
        echo "❌ Please log in to Railway first:"
        echo "   railway login"
        exit 1
    fi
    echo "✅ Railway authentication verified"
}

# Function to validate required files
validate_files() {
    local required_files=(
        "web_app.py"
        "basketball_analysis_service.py"
        "wsgi.py"
        "requirements.txt"
        "Dockerfile"
        "railway.json"
        "ideal_shot_guide.json"
    )
    
    echo "🔍 Validating required files..."
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            echo "❌ Missing required file: $file"
            exit 1
        fi
        echo "   ✅ $file"
    done
    echo "✅ All required files present"
}

# Function to display deployment configuration
show_config() {
    echo ""
    echo "🔧 Deployment Configuration:"
    echo "   • Platform: Railway"
    echo "   • Runtime: Python 3.11"
    echo "   • Framework: Flask + Gunicorn"
    echo "   • Container: Docker"
    echo "   • Optimizations: CPU-only processing, reduced timeouts"
    echo "   • Health Check: /health endpoint"
    echo "   • Auto-restart: On failure (max 10 retries)"
    echo ""
}

# Function to create .railwayignore if it doesn't exist
create_railwayignore() {
    if [[ ! -f ".railwayignore" ]]; then
        echo "📝 Creating .railwayignore..."
        cat > .railwayignore << EOF
# Railway Ignore File
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
EOF
        echo "✅ Created .railwayignore"
    else
        echo "✅ .railwayignore already exists"
    fi
}

# Function to set environment variables
set_environment_variables() {
    echo "🌍 Setting Railway environment variables..."
    
    # Performance optimizations
    railway variables set TF_CPP_MIN_LOG_LEVEL=2
    railway variables set CUDA_VISIBLE_DEVICES=""
    railway variables set TF_ENABLE_ONEDNN_OPTS=0
    railway variables set MEDIAPIPE_DISABLE_GPU=1
    
    # Flask configuration
    railway variables set FLASK_ENV=production
    railway variables set FLASK_DEBUG=false
    railway variables set FLASK_HOST=0.0.0.0
    
    # Application settings
    railway variables set PYTHONUNBUFFERED=1
    railway variables set PORT=8080
    
    echo "✅ Environment variables configured"
}

# Function to deploy to Railway
deploy_to_railway() {
    echo "🚀 Starting Railway deployment..."
    echo ""
    echo "   This will:"
    echo "   1. Build the Docker container with optimizations"
    echo "   2. Deploy to Railway with health checks"
    echo "   3. Set up auto-scaling and monitoring"
    echo ""
    
    read -p "   Continue with deployment? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        echo "❌ Deployment cancelled"
        exit 0
    fi
    
    # Deploy using Railway CLI
    railway up --detach
    
    echo ""
    echo "✅ Deployment started!"
    echo ""
    echo "📊 Monitoring deployment..."
    railway status
    
    echo ""
    echo "🌐 Getting service URL..."
    SERVICE_URL=$(railway domain 2>/dev/null || echo "Not yet available")
    
    if [[ "$SERVICE_URL" != "Not yet available" ]]; then
        echo "🎉 Deployment successful!"
        echo ""
        echo "🌐 Your Basketball Analysis Service is available at:"
        echo "   $SERVICE_URL"
        echo ""
        echo "🔍 Health check: $SERVICE_URL/health"
        echo "📊 Upload page: $SERVICE_URL/"
        echo ""
    else
        echo "⏳ Deployment in progress..."
        echo "   Run 'railway domain' to get the URL once deployment completes"
        echo "   Run 'railway logs' to monitor deployment progress"
    fi
}

# Function to show post-deployment info
show_post_deployment_info() {
    echo ""
    echo "📋 Post-Deployment Commands:"
    echo "   • View logs:     railway logs"
    echo "   • Check status:  railway status"
    echo "   • Open service:  railway open"
    echo "   • View metrics:  railway metrics"
    echo "   • Scale service: railway scale"
    echo ""
    echo "🛠️  Management:"
    echo "   • Environment variables: railway variables"
    echo "   • Database setup: railway add (if needed)"
    echo "   • Custom domain: railway domain add <domain>"
    echo ""
    echo "🎯 Performance Optimizations Applied:"
    echo "   • CPU-only processing (no GPU dependencies)"
    echo "   • Optimized MediaPipe settings"
    echo "   • Reduced TensorFlow logging"
    echo "   • Production Flask configuration"
    echo "   • Gunicorn with 2 workers and thread pooling"
    echo ""
}

# Main deployment process
main() {
    echo "Starting Basketball Analysis Service deployment to Railway..."
    echo ""
    
    check_railway_cli
    check_railway_auth
    validate_files
    show_config
    create_railwayignore
    set_environment_variables
    deploy_to_railway
    show_post_deployment_info
    
    echo "🎉 Railway deployment process completed!"
    echo ""
    echo "Your optimized Basketball Analysis Service is now running on Railway"
    echo "with all performance optimizations that made localhost work perfectly!"
}

# Run the deployment
main "$@"
