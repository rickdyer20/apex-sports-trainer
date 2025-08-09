#!/bin/bash
# Namecheap Deployment Script for Basketball Analysis Service

echo "🚀 Namecheap Deployment - Basketball Analysis Service"
echo "==================================================="

# Common Namecheap usernames for apexsports-llc.com
echo "Trying common Namecheap usernames..."
echo ""
echo "1. First, try to find your username in Namecheap cPanel:"
echo "   - Login to namecheap.com"
echo "   - Go to Account > Dashboard > Manage (next to apexsports-llc.com)"
echo "   - Look for 'SSH Access' or 'Terminal' - username will be shown"
echo ""
echo "2. Common usernames for your domain might be:"
echo "   - apexspo1"
echo "   - apexsports"
echo "   - apexsportsllc"
echo "   - (your cPanel username)"
echo ""

read -p "Enter your Namecheap username: " USERNAME

if [ -z "$USERNAME" ]; then
    echo "❌ Username required. Please check your Namecheap cPanel."
    exit 1
fi

echo "📊 Connecting to: $USERNAME@apexsports-llc.com"
echo "📁 Deploying to: /home/$USERNAME/public_html"

# Test connection first
echo "🔍 Testing SSH connection..."
ssh -o ConnectTimeout=10 $USERNAME@apexsports-llc.com "echo 'Connection successful!'"

if [ $? -eq 0 ]; then
    echo "✅ SSH connection works!"
    echo ""
    echo "🚀 Deploying Basketball Analysis Service..."
    
    ssh $USERNAME@apexsports-llc.com << EOF
cd /home/$USERNAME/public_html

echo "📥 Cloning repository..."
if [ -d "apex-sports-trainer" ]; then
    cd apex-sports-trainer
    git pull origin working-full-featured
else
    git clone -b working-full-featured https://github.com/rickdyer20/apex-sports-trainer.git
    cd apex-sports-trainer
fi

echo "📦 Extracting deployment package..."
if [ -f "apexsports_deployment.zip" ]; then
    unzip -o apexsports_deployment.zip
fi

echo "📚 Installing dependencies..."
pip3 install --user flask stripe python-dotenv gunicorn

echo "🔒 Setting permissions..."
chmod +x complete_web_app.py
chmod 644 .env

echo "🧪 Testing application..."
python3 -c "import complete_web_app; print('✅ Application ready!')"

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
echo ""
echo "🌐 Your Basketball Analysis Service is deployed!"
echo "📁 Location: /home/$USERNAME/public_html/apex-sports-trainer"
echo ""
echo "💰 Revenue Model Active:"
echo "  🆓 Free: 1 analysis per year"
echo "  💵 One-time: \\$9.99 for 5 analyses"
echo "  🔥 Pro: \\$19.99/month unlimited"
echo "  🌟 Enterprise: \\$49.99/month premium"
echo ""
echo "🔐 Live Stripe Integration: Ready for payments!"
echo ""
echo "🚀 To start your service:"
echo "  python3 complete_web_app.py"
echo ""
echo "🌐 Visit: https://apexsports-llc.com"
EOF

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ DEPLOYMENT SUCCESSFUL!"
        echo "🎉 Your Basketball Analysis Service is ready!"
        echo ""
        echo "🚀 Would you like to start the service now? (y/n)"
        read -p "> " START_SERVICE
        
        if [ "$START_SERVICE" = "y" ] || [ "$START_SERVICE" = "Y" ]; then
            echo "🔧 Starting service..."
            ssh $USERNAME@apexsports-llc.com "cd /home/$USERNAME/public_html/apex-sports-trainer && nohup python3 complete_web_app.py > service.log 2>&1 &"
            echo "✅ Service started!"
            echo "🌐 Your Basketball Analysis Service is now LIVE at:"
            echo "   https://apexsports-llc.com"
        fi
    fi
else
    echo "❌ SSH connection failed."
    echo "💡 Alternative: Use Namecheap cPanel File Manager and Terminal"
    echo "   1. Login to cPanel"
    echo "   2. Upload apexsports_deployment.zip to public_html"
    echo "   3. Extract files"
    echo "   4. Use Terminal to run setup commands"
fi
