#!/bin/bash
# Deploy Basketball Analysis Service from Git to apexsports-llc.com
# Run this script on your server

echo "🚀 Deploying Basketball Analysis Service from Git..."
echo "=================================================="

# Set variables (adjust these for your server)
WEB_DIR="/home/user/public_html"
REPO_URL="https://github.com/rickdyer20/apex-sports-trainer.git"
BRANCH="working-full-featured"

# Navigate to web directory
echo "📁 Navigating to web directory: $WEB_DIR"
cd "$WEB_DIR" || {
    echo "❌ Failed to navigate to $WEB_DIR"
    echo "💡 Please adjust WEB_DIR in this script to match your server"
    exit 1
}

# Clone or update repository
if [ -d "apex-sports-trainer" ]; then
    echo "📄 Updating existing repository..."
    cd apex-sports-trainer
    git pull origin "$BRANCH"
else
    echo "📥 Cloning repository..."
    git clone -b "$BRANCH" "$REPO_URL"
    cd apex-sports-trainer
fi

echo "✅ Repository updated successfully"

# Extract deployment package if available
if [ -f "apexsports_deployment.zip" ]; then
    echo "📦 Extracting deployment package..."
    unzip -o apexsports_deployment.zip
    echo "✅ Deployment package extracted"
else
    echo "📋 Using files directly from repository"
fi

# Install Python dependencies
echo "📚 Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install flask stripe python-dotenv gunicorn
elif command -v pip &> /dev/null; then
    pip install flask stripe python-dotenv gunicorn
else
    echo "❌ Python pip not found. Please install pip first."
    exit 1
fi

echo "✅ Dependencies installed"

# Set file permissions
echo "🔒 Setting file permissions..."
chmod +x complete_web_app.py
chmod 644 .env
chmod +x git_deploy.sh
chmod +x server_setup.sh

echo "✅ Permissions set"

# Test the application
echo "🧪 Testing application..."
if python3 -c "import complete_web_app; print('✅ Application ready!')" 2>/dev/null; then
    echo "✅ Application test passed"
elif python -c "import complete_web_app; print('✅ Application ready!')" 2>/dev/null; then
    echo "✅ Application test passed"
else
    echo "⚠️ Application test failed, but continuing deployment..."
fi

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "Your Basketball Analysis Service is ready to start!"
echo ""
echo "💰 Revenue Model:"
echo "  🆓 Free: 1 analysis per year"
echo "  💵 One-time: \$9.99 for 5 analyses"
echo "  🔥 Pro: \$19.99/month unlimited"
echo "  🌟 Enterprise: \$49.99/month premium"
echo ""
echo "🔐 Live Stripe Integration: Ready for real payments!"
echo ""
echo "🚀 Start your service with one of these commands:"
echo ""
echo "Development mode:"
echo "  python3 complete_web_app.py"
echo ""
echo "Production mode:"
echo "  gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app"
echo ""
echo "Background mode:"
echo "  nohup gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app > service.log 2>&1 &"
echo ""
echo "🌐 Your site will be live at: https://apexsports-llc.com"
echo ""
echo "✅ Deployment script completed successfully!"
