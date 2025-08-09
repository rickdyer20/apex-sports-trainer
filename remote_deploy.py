#!/usr/bin/env python3
"""
Remote Deployment Script - Deploy from local machine to apexsports-llc.com
This script will SSH into your server and run the deployment commands
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def deploy_to_server():
    """Deploy Basketball Analysis Service to apexsports-llc.com"""
    
    print("🚀 Basketball Analysis Service - Remote Deployment")
    print("=" * 60)
    
    # Get server credentials
    server_user = input("Enter your server username: ").strip()
    if not server_user:
        print("❌ Username is required")
        return False
    
    server_host = "apexsports-llc.com"
    server_path = input("Enter web directory path (default: /home/user/public_html): ").strip()
    if not server_path:
        server_path = "/home/user/public_html"
    
    print(f"\n📊 Connection Details:")
    print(f"  Host: {server_host}")
    print(f"  User: {server_user}")
    print(f"  Path: {server_path}")
    
    confirm = input("\nProceed with deployment? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Deployment cancelled")
        return False
    
    # Create the remote deployment command
    remote_commands = f"""
cd {server_path}
echo "🚀 Starting deployment to apexsports-llc.com..."

# Clone or update repository
if [ -d "apex-sports-trainer" ]; then
    echo "📄 Updating existing repository..."
    cd apex-sports-trainer
    git pull origin working-full-featured
else
    echo "📥 Cloning repository..."
    git clone -b working-full-featured https://github.com/rickdyer20/apex-sports-trainer.git
    cd apex-sports-trainer
fi

echo "✅ Repository updated"

# Extract deployment package if available
if [ -f "apexsports_deployment.zip" ]; then
    echo "📦 Extracting deployment package..."
    unzip -o apexsports_deployment.zip
    echo "✅ Files extracted"
fi

# Install dependencies
echo "📚 Installing dependencies..."
pip3 install flask stripe python-dotenv gunicorn

# Set permissions
echo "🔒 Setting permissions..."
chmod +x complete_web_app.py
chmod 644 .env

# Test application
echo "🧪 Testing application..."
python3 -c "import complete_web_app; print('✅ Application ready!')"

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "Your Basketball Analysis Service is ready!"
echo ""
echo "💰 Revenue Model:"
echo "  🆓 Free: 1 analysis per year"
echo "  💵 One-time: \\$9.99 for 5 analyses"
echo "  🔥 Pro: \\$19.99/month unlimited"
echo "  🌟 Enterprise: \\$49.99/month premium"
echo ""
echo "🔐 Live Stripe Integration: Ready for real payments!"
echo ""
echo "🚀 To start your service, run:"
echo "  python3 complete_web_app.py  # Development"
echo "  # OR"
echo "  gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app  # Production"
echo ""
echo "🌐 Your site will be live at: https://apexsports-llc.com"
"""
    
    # Execute deployment via SSH
    ssh_command = f'ssh {server_user}@{server_host} "{remote_commands}"'
    
    print("\n🔗 Connecting to server and deploying...")
    success = run_command(ssh_command, "Remote deployment")
    
    if success:
        print("\n✅ DEPLOYMENT SUCCESSFUL!")
        print("🌐 Your Basketball Analysis Service should now be deployed!")
        print(f"📋 Next step: SSH into your server and start the service:")
        print(f"   ssh {server_user}@{server_host}")
        print(f"   cd {server_path}/apex-sports-trainer")
        print(f"   gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app")
        
        # Offer to start the service automatically
        start_now = input("\nWould you like to start the service now? (y/n): ").strip().lower()
        if start_now == 'y':
            start_command = f'ssh {server_user}@{server_host} "cd {server_path}/apex-sports-trainer && nohup gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app > service.log 2>&1 &"'
            
            print("🚀 Starting Basketball Analysis Service...")
            if run_command(start_command, "Service startup"):
                print("\n🎉 SUCCESS! Your Basketball Analysis Service is now LIVE!")
                print("🌐 Visit: https://apexsports-llc.com")
                print("💰 Ready to accept payments and analyze basketball shots!")
            else:
                print("⚠️ Service deployment completed but startup had issues.")
                print("You can start it manually with the commands shown above.")
    
    return success

if __name__ == "__main__":
    deploy_to_server()
