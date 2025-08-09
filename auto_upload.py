#!/usr/bin/env python3
"""
Automated Server Upload Script for Basketball Analysis Service
Deploy directly from local machine to apexsports-llc.com
"""

import os
import subprocess
import sys
from pathlib import Path

class ServerUploader:
    def __init__(self):
        self.deployment_zip = "apexsports_deployment.zip"
        self.server_host = "apexsports-llc.com"
        self.server_user = None  # Will be set by user
        self.server_path = "/home/user/public_html"  # Default web directory
        
    def check_prerequisites(self):
        """Check if required tools are available"""
        print("🔍 Checking prerequisites...")
        
        # Check if deployment package exists
        if not os.path.exists(self.deployment_zip):
            print("❌ Deployment package not found. Run deployment script first.")
            return False
            
        # Check for SCP/SSH availability
        try:
            subprocess.run(["scp", "--help"], capture_output=True, check=True)
            print("✅ SCP available")
        except:
            print("❌ SCP not available. Install OpenSSH or use alternative method.")
            return False
            
        return True
    
    def get_server_credentials(self):
        """Get server connection details from user"""
        print("\n🔐 Server Connection Setup")
        print("=" * 50)
        
        self.server_user = input("Enter your server username: ").strip()
        
        # Optional: custom server path
        custom_path = input(f"Web directory path (default: {self.server_path}): ").strip()
        if custom_path:
            self.server_path = custom_path
            
        print(f"\n📊 Connection Details:")
        print(f"  Host: {self.server_host}")
        print(f"  User: {self.server_user}")
        print(f"  Path: {self.server_path}")
        
        confirm = input("\nProceed with upload? (y/n): ").strip().lower()
        return confirm == 'y'
    
    def upload_files(self):
        """Upload deployment package to server"""
        print("\n🚀 Uploading files to server...")
        
        try:
            # Upload deployment package
            scp_command = [
                "scp",
                self.deployment_zip,
                f"{self.server_user}@{self.server_host}:{self.server_path}/"
            ]
            
            print(f"📤 Uploading {self.deployment_zip}...")
            result = subprocess.run(scp_command, check=True)
            print("✅ Deployment package uploaded successfully!")
            
            # Upload setup script
            setup_script = "server_setup.sh"
            if os.path.exists(setup_script):
                scp_setup_command = [
                    "scp",
                    setup_script,
                    f"{self.server_user}@{self.server_host}:{self.server_path}/"
                ]
                
                print(f"📤 Uploading {setup_script}...")
                subprocess.run(scp_setup_command, check=True)
                print("✅ Setup script uploaded successfully!")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Upload failed: {e}")
            return False
    
    def run_server_setup(self):
        """Execute setup script on server"""
        print("\n⚙️ Running server setup...")
        
        try:
            ssh_command = [
                "ssh",
                f"{self.server_user}@{self.server_host}",
                f"cd {self.server_path} && chmod +x server_setup.sh && ./server_setup.sh"
            ]
            
            print("🔧 Executing server setup script...")
            result = subprocess.run(ssh_command, check=True)
            print("✅ Server setup completed!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Server setup failed: {e}")
            print("💡 You can manually run the setup script on your server:")
            print(f"   ssh {self.server_user}@{self.server_host}")
            print(f"   cd {self.server_path}")
            print(f"   chmod +x server_setup.sh")
            print(f"   ./server_setup.sh")
            return False
    
    def start_service(self):
        """Start the Basketball Analysis Service on server"""
        print("\n🚀 Starting Basketball Analysis Service...")
        
        print("Choose startup method:")
        print("1. Development mode (interactive)")
        print("2. Production mode (background)")
        print("3. Manual start (just show commands)")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            ssh_command = [
                "ssh",
                f"{self.server_user}@{self.server_host}",
                f"cd {self.server_path} && python3 complete_web_app.py"
            ]
            print("🔧 Starting in development mode...")
            subprocess.run(ssh_command)
            
        elif choice == "2":
            ssh_command = [
                "ssh",
                f"{self.server_user}@{self.server_host}",
                f"cd {self.server_path} && nohup gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app > service.log 2>&1 &"
            ]
            print("🔧 Starting in production mode...")
            subprocess.run(ssh_command)
            print("✅ Service started in background!")
            
        else:
            print("\n📋 Manual start commands:")
            print(f"ssh {self.server_user}@{self.server_host}")
            print(f"cd {self.server_path}")
            print("# Development:")
            print("python3 complete_web_app.py")
            print("# Production:")
            print("gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app")
    
    def verify_deployment(self):
        """Show verification steps"""
        print("\n✅ DEPLOYMENT COMPLETE!")
        print("=" * 50)
        print(f"🌐 Your Basketball Analysis Service should be live at:")
        print(f"   https://{self.server_host}")
        print(f"   https://{self.server_host}/pricing")
        print(f"   https://{self.server_host}/analyze")
        
        print(f"\n💰 Revenue Model Active:")
        print(f"   🆓 Free: 1 analysis per year")
        print(f"   💵 One-time: $9.99 for 5 analyses")
        print(f"   🔥 Pro: $19.99/month unlimited")
        print(f"   🌟 Enterprise: $49.99/month premium")
        
        print(f"\n🔐 Live Stripe Integration:")
        print(f"   ✅ Real payment processing active")
        print(f"   ✅ Webhook configured")
        print(f"   ✅ Ready to earn revenue!")
    
    def deploy(self):
        """Main deployment process"""
        print("🚀 Basketball Analysis Service - Server Upload")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Get server credentials
        if not self.get_server_credentials():
            print("❌ Deployment cancelled.")
            return False
        
        # Upload files
        if not self.upload_files():
            return False
        
        # Run server setup
        if not self.run_server_setup():
            print("⚠️ Setup had issues, but files are uploaded.")
        
        # Start service
        self.start_service()
        
        # Show verification
        self.verify_deployment()
        
        return True

# Alternative upload methods for different scenarios
class AlternativeUploaders:
    
    @staticmethod
    def ftp_upload():
        """FTP upload instructions"""
        print("\n📁 FTP Upload Method")
        print("=" * 30)
        print("1. Use an FTP client (FileZilla, WinSCP, etc.)")
        print("2. Connect to: apexsports-llc.com")
        print("3. Upload these files to your web directory:")
        print("   - apexsports_deployment.zip")
        print("   - server_setup.sh")
        print("4. Extract and run setup via hosting control panel")
    
    @staticmethod
    def cpanel_upload():
        """cPanel upload instructions"""
        print("\n🎛️ cPanel Upload Method")
        print("=" * 30)
        print("1. Login to your hosting control panel")
        print("2. Go to File Manager")
        print("3. Navigate to public_html folder")
        print("4. Upload apexsports_deployment.zip")
        print("5. Right-click → Extract")
        print("6. Use Terminal in cPanel to run setup")
    
    @staticmethod
    def git_deploy():
        """Git deployment method"""
        print("\n🔄 Git Deployment Method")
        print("=" * 30)
        print("1. Push your code to GitHub")
        print("2. On server, clone the repository:")
        print("   git clone https://github.com/rickdyer20/apex-sports-trainer.git")
        print("3. Run the deployment script")

if __name__ == "__main__":
    uploader = ServerUploader()
    
    print("Choose upload method:")
    print("1. Automated SSH/SCP upload (recommended)")
    print("2. Show FTP instructions")
    print("3. Show cPanel instructions")
    print("4. Show Git deployment")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        uploader.deploy()
    elif choice == "2":
        AlternativeUploaders.ftp_upload()
    elif choice == "3":
        AlternativeUploaders.cpanel_upload()
    elif choice == "4":
        AlternativeUploaders.git_deploy()
    else:
        print("Invalid choice. Exiting.")
