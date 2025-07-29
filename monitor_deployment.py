#!/usr/bin/env python3
"""
DigitalOcean Deployment Monitor
Basketball Analysis Service - Monitor deployment status and health
"""

import requests
import time
import sys
from datetime import datetime
import json

class DeploymentMonitor:
    def __init__(self, app_url=None):
        """Initialize the deployment monitor"""
        self.app_url = app_url
        self.health_endpoint = "/health"
        self.api_health_endpoint = "/api/health"
        
    def check_health(self, endpoint="/health"):
        """Check if the app is responding at the health endpoint"""
        if not self.app_url:
            print("❌ No app URL provided. Please set the URL after deployment.")
            return False
            
        try:
            full_url = f"{self.app_url.rstrip('/')}{endpoint}"
            print(f"🔍 Checking: {full_url}")
            
            response = requests.get(full_url, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Health check passed!")
                    print(f"📊 Status: {data.get('status', 'unknown')}")
                    print(f"🏀 Service: {data.get('service', 'unknown')}")
                    print(f"⏰ Timestamp: {data.get('timestamp', 'unknown')}")
                    
                    if 'active_jobs' in data:
                        print(f"💼 Active jobs: {data.get('active_jobs', 0)}")
                    
                    return True
                    
                except json.JSONDecodeError:
                    print(f"✅ Health check passed (status: {response.status_code})")
                    print(f"📝 Response: {response.text[:200]}")
                    return True
                    
            else:
                print(f"⚠️ Health check returned status: {response.status_code}")
                print(f"📝 Response: {response.text[:200]}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed - app may still be starting or URL incorrect")
            return False
        except requests.exceptions.Timeout:
            print(f"⏱️ Request timed out - app may be slow to respond")
            return False
        except Exception as e:
            print(f"❌ Error checking health: {e}")
            return False
    
    def check_main_page(self):
        """Check if the main page loads"""
        if not self.app_url:
            return False
            
        try:
            print(f"🔍 Checking main page: {self.app_url}")
            response = requests.get(self.app_url, timeout=30)
            
            if response.status_code == 200:
                # Check if it contains expected content
                content = response.text.lower()
                if "basketball" in content and ("upload" in content or "analysis" in content):
                    print("✅ Main page loaded successfully with expected content")
                    return True
                else:
                    print("⚠️ Main page loaded but content seems unexpected")
                    return False
            else:
                print(f"❌ Main page returned status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking main page: {e}")
            return False
    
    def monitor_deployment(self, max_attempts=20, delay=30):
        """Monitor deployment with multiple attempts"""
        print("🚀 Starting deployment monitoring...")
        print(f"⏰ Will check every {delay} seconds for up to {max_attempts} attempts")
        print("=" * 60)
        
        for attempt in range(1, max_attempts + 1):
            print(f"\n🔄 Attempt {attempt}/{max_attempts} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Check health endpoint
            health_ok = self.check_health(self.health_endpoint)
            
            if health_ok:
                print("🎉 Health check passed! Checking main page...")
                main_page_ok = self.check_main_page()
                
                if main_page_ok:
                    print("\n🎯 DEPLOYMENT SUCCESSFUL! 🎉")
                    print("=" * 60)
                    print(f"✅ App URL: {self.app_url}")
                    print(f"✅ Health endpoint: {self.app_url}{self.health_endpoint}")
                    print(f"✅ Main page: Working")
                    print("=" * 60)
                    return True
                    
            if attempt < max_attempts:
                print(f"⏳ Waiting {delay} seconds before next check...")
                time.sleep(delay)
            
        print(f"\n⚠️ Monitoring completed after {max_attempts} attempts")
        print("The app may still be deploying or there may be an issue.")
        return False

def main():
    """Main function to run deployment monitoring"""
    print("🌊 DigitalOcean Deployment Monitor")
    print("Basketball Analysis Service")
    print("=" * 50)
    
    # Instructions for user
    print("\n📋 INSTRUCTIONS:")
    print("1. Deploy your app on DigitalOcean following the deployment guide")
    print("2. Copy the app URL from DigitalOcean dashboard") 
    print("3. Run this script with the URL:")
    print("   python monitor_deployment.py <your-app-url>")
    print("\nExample:")
    print("   python monitor_deployment.py https://apex-sports-trainer-abc123.ondigitalocean.app")
    
    # Check for command line argument
    if len(sys.argv) > 1:
        app_url = sys.argv[1]
        print(f"\n🎯 Monitoring deployment at: {app_url}")
        
        monitor = DeploymentMonitor(app_url)
        success = monitor.monitor_deployment()
        
        if success:
            print("\n🚀 Deployment monitoring completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️ Deployment monitoring completed with issues.")
            print("Check DigitalOcean dashboard for build/runtime logs.")
            sys.exit(1)
    else:
        print("\n⚠️ No app URL provided.")
        print("After deploying on DigitalOcean, run:")
        print("   python monitor_deployment.py <your-app-url>")

if __name__ == "__main__":
    main()
