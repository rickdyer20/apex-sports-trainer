#!/bin/bash
# Server Setup Script for apexsports-llc.com
# Run this on your server after uploading the deployment package

echo "🚀 Setting up Basketball Analysis Service..."

# Extract deployment package
unzip -o apexsports_deployment.zip
echo "✅ Files extracted"

# Install Python dependencies
pip3 install flask stripe python-dotenv gunicorn
echo "✅ Dependencies installed"

# Set file permissions
chmod +x complete_web_app.py
chmod 644 .env
echo "✅ Permissions set"

# Test the application
echo "🧪 Testing application..."
python3 -c "import complete_web_app; print('✅ Application imports successfully')"

# Start the service
echo "🚀 Starting Basketball Analysis Service..."
echo "Choose startup method:"
echo "1. Development: python3 complete_web_app.py"
echo "2. Production: gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app"
echo "3. Background: nohup gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app &"

echo ""
echo "🎉 Setup complete! Your service is ready to go live!"
echo "Visit: https://apexsports-llc.com"
