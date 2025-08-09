#!/bin/bash
# Git Deployment Script for Basketball Analysis Service
# Deploy directly from local repository to apexsports-llc.com

echo "🚀 Basketball Analysis Service - Git Deployment"
echo "================================================"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not a git repository. Initializing..."
    git init
    git remote add origin https://github.com/rickdyer20/apex-sports-trainer.git
fi

# Check git status
echo "📊 Checking repository status..."
git status

# Add all deployment files
echo "📁 Adding deployment files..."
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
echo "💾 Committing deployment package..."
git commit -m "🚀 Production deployment package - Basketball Analysis Service v9.0

- Complete web application with live Stripe integration
- Aggressive freemium model (1 analysis/year free tier)
- 4-tier pricing: Free, $9.99 one-time, $19.99/month Pro, $49.99/month Enterprise
- User tracking and usage enforcement
- Legal compliance (terms, privacy policy)
- Production-ready with live payment processing
- Revenue optimization features

Ready for immediate deployment to apexsports-llc.com"

# Push to GitHub
echo "📤 Pushing to GitHub repository..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Code pushed to GitHub successfully!"
    
    echo ""
    echo "🌐 Now deploying to server..."
    echo "Choose deployment method:"
    echo "1. Automated server deployment (requires SSH access)"
    echo "2. Show manual server commands"
    echo "3. Exit and deploy manually later"
    
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1)
            echo ""
            read -p "Enter your server username: " username
            read -p "Enter server path (default: /home/user/public_html): " server_path
            server_path=${server_path:-/home/user/public_html}
            
            echo "🔧 Deploying to server via SSH..."
            
            # Deploy to server
            ssh $username@apexsports-llc.com << EOF
cd $server_path
echo "🔄 Cloning/updating repository..."
if [ -d "apex-sports-trainer" ]; then
    cd apex-sports-trainer
    git pull origin main
else
    git clone https://github.com/rickdyer20/apex-sports-trainer.git
    cd apex-sports-trainer
fi

echo "📦 Extracting deployment package..."
if [ -f "apexsports_deployment.zip" ]; then
    unzip -o apexsports_deployment.zip
else
    echo "⚠️  Using individual files..."
fi

echo "📚 Installing dependencies..."
pip3 install flask stripe python-dotenv gunicorn

echo "🔒 Setting permissions..."
chmod +x complete_web_app.py
chmod 644 .env

echo "🧪 Testing application..."
python3 -c "import complete_web_app; print('✅ Application ready!')"

echo "🚀 Starting Basketball Analysis Service..."
echo "Service is ready to start!"
echo ""
echo "Manual start options:"
echo "Development: python3 complete_web_app.py"
echo "Production: gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app"
echo "Background: nohup gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app > service.log 2>&1 &"
EOF
            
            if [ $? -eq 0 ]; then
                echo "✅ Deployment completed successfully!"
                echo "🌐 Your service should be live at: https://apexsports-llc.com"
            else
                echo "❌ SSH deployment failed. Use manual method below."
            fi
            ;;
            
        2)
            echo ""
            echo "📋 Manual Server Deployment Commands:"
            echo "====================================='"
            echo "# SSH into your server:"
            echo "ssh your_username@apexsports-llc.com"
            echo ""
            echo "# Clone the repository:"
            echo "cd /path/to/your/website"
            echo "git clone https://github.com/rickdyer20/apex-sports-trainer.git"
            echo "cd apex-sports-trainer"
            echo ""
            echo "# Extract deployment package:"
            echo "unzip -o apexsports_deployment.zip"
            echo ""
            echo "# Install dependencies:"
            echo "pip3 install flask stripe python-dotenv gunicorn"
            echo ""
            echo "# Set permissions:"
            echo "chmod +x complete_web_app.py"
            echo "chmod 644 .env"
            echo ""
            echo "# Start the service:"
            echo "python3 complete_web_app.py  # Development"
            echo "# OR"
            echo "gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app  # Production"
            ;;
            
        3)
            echo "🎯 Repository updated! Deploy manually when ready."
            ;;
    esac
    
else
    echo "❌ Failed to push to GitHub. Check your credentials and try again."
fi

echo ""
echo "💰 Revenue Model Ready:"
echo "  🆓 Free: 1 analysis per year"
echo "  💵 One-time: \$9.99 for 5 analyses"
echo "  🔥 Pro: \$19.99/month unlimited"
echo "  🌟 Enterprise: \$49.99/month premium"
echo ""
echo "🔐 Live Stripe Integration: Ready for real payments!"
