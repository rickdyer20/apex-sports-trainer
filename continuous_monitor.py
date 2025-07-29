#!/usr/bin/env python3
"""
Continuous Basketball Analysis Deployment Monitor
Monitors until full service is ready and alerts you
"""

import requests
import time
from datetime import datetime
import sys

class DeploymentMonitor:
    def __init__(self, url):
        self.url = url
        self.start_time = datetime.now()
        self.check_count = 0
        
    def check_status(self):
        """Check current deployment status"""
        self.check_count += 1
        
        try:
            response = requests.get(self.url, timeout=10)
            content = response.text.lower()
            
            if response.status_code != 200:
                return "http_error", f"HTTP {response.status_code}"
            
            # Analyze content to determine status
            if 'loading full version' in content or 'still be loading' in content:
                return "loading", "Dependencies installing..."
            elif 'upload' in content and 'basketball' in content and 'analyze' in content:
                return "ready", "Full basketball analysis ready!"
            elif 'fallback' in content:
                return "fallback", "Fallback mode active"
            elif 'error' in content or 'failed' in content:
                return "error", "Error detected in deployment"
            else:
                return "unknown", "Unknown status"
                
        except requests.exceptions.RequestException as e:
            return "connection_error", str(e)
    
    def format_elapsed_time(self):
        """Format elapsed time since monitoring started"""
        elapsed = datetime.now() - self.start_time
        minutes = int(elapsed.total_seconds() / 60)
        seconds = int(elapsed.total_seconds() % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def print_status_update(self, status, message):
        """Print a formatted status update"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        elapsed = self.format_elapsed_time()
        
        print(f"\r{timestamp} | Check #{self.check_count:02d} | Elapsed: {elapsed} | ", end="")
        
        if status == "loading":
            print("⏳ LOADING - Dependencies installing...", end="", flush=True)
        elif status == "ready":
            print("✅ READY! - Full service is live!        ", end="", flush=True)
        elif status == "error":
            print("❌ ERROR - Check Render dashboard       ", end="", flush=True)
        else:
            print(f"🔍 {status.upper()} - {message}           ", end="", flush=True)
    
    def monitor(self, max_checks=50, check_interval=30):
        """Monitor deployment until ready or timeout"""
        
        print("🏀 BASKETBALL ANALYSIS DEPLOYMENT MONITOR")
        print("=" * 60)
        print(f"📡 Monitoring: {self.url}")
        print(f"⏱️  Check interval: {check_interval} seconds")
        print(f"🎯 Will alert when full service is ready")
        print("-" * 60)
        
        for _ in range(max_checks):
            status, message = self.check_status()
            self.print_status_update(status, message)
            
            if status == "ready":
                print("\n" + "=" * 60)
                print("🎉 DEPLOYMENT COMPLETE!")
                print("✅ Full Basketball Analysis Service is READY!")
                print(f"🔗 URL: {self.url}")
                print(f"⏱️  Total time: {self.format_elapsed_time()}")
                print("\n🚀 FEATURES NOW AVAILABLE:")
                print("  • Video upload and analysis")
                print("  • MediaPipe pose detection")
                print("  • Shot mechanics evaluation")
                print("  • PDF report generation")
                print("  • Real-time feedback")
                print("\n🎯 Ready to analyze basketball shots!")
                return True
            
            elif status == "error":
                print("\n" + "=" * 60)
                print("❌ DEPLOYMENT ERROR DETECTED")
                print("🔍 Check your Render dashboard for details")
                print("💡 Common issues:")
                print("  • Memory limit exceeded (upgrade plan)")
                print("  • Dependency installation failed")
                print("  • Import errors in Python code")
                return False
            
            elif status == "connection_error":
                print(f"\n⚠️  Connection issue: {message}")
                print("🔄 Will continue monitoring...")
            
            # Wait before next check (unless it's the last check)
            if _ < max_checks - 1:
                time.sleep(check_interval)
        
        print("\n" + "=" * 60)
        print("⏰ MONITORING TIMEOUT")
        print(f"🔍 Checked {max_checks} times over {self.format_elapsed_time()}")
        print("💡 The deployment may still be in progress")
        print("🔄 You can continue checking manually or restart monitoring")
        return False

def main():
    """Main monitoring function"""
    
    # Basketball analysis service URL
    url = "https://apex-sports-trainer.onrender.com"
    
    print("🎯 Starting continuous deployment monitoring...")
    print("💡 Press Ctrl+C to stop monitoring at any time\n")
    
    monitor = DeploymentMonitor(url)
    
    try:
        # Monitor for up to 25 minutes (50 checks × 30 seconds)
        success = monitor.monitor(max_checks=50, check_interval=30)
        
        if success:
            # Play a success sound if possible
            try:
                print("\a")  # System beep
            except:
                pass
                
            print("\n🔔 MONITORING COMPLETE - Service is ready!")
        else:
            print("\n🔄 Monitoring ended - Check status manually")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped by user")
        print("🔍 Last status check results:")
        status, message = monitor.check_status()
        print(f"   Status: {status}")
        print(f"   Message: {message}")
        print(f"🔗 Check manually: {url}")

if __name__ == "__main__":
    main()
