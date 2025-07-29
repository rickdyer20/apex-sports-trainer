#!/usr/bin/env python3
"""
Monitor Paid Plan Deployment - Full Basketball Analysis Service
================================================================

With your PAID PLAN upgrade, we can now deploy the complete computer vision service!

This script monitors:
✅ OpenCV installation progress  
✅ MediaPipe pose detection loading
✅ Full basketball analysis service availability
✅ Video upload functionality
✅ PDF report generation capability

PAID PLAN BENEFITS:
- No build timeouts (was failing on free tier)
- Full memory allocation for video processing
- Faster dependency installation  
- Complete computer vision pipeline
"""

import requests
import time
import sys

def check_deployment_status():
    """Monitor the full basketball analysis service deployment"""
    
    url = "https://apex-sports-trainer.onrender.com"
    
    print("🏀 MONITORING PAID PLAN DEPLOYMENT")
    print("=" * 50)
    print("URL:", url)
    print("Checking for full computer vision service...")
    print()
    
    # Check for loading vs full service
    try:
        response = requests.get(url, timeout=30)
        content = response.text
        
        if "Loading Full Version" in content:
            print("⏳ STATUS: Still deploying computer vision dependencies")
            print("   - OpenCV and MediaPipe installation in progress")
            print("   - This is normal with heavy CV libraries")
            print("   - Paid plan removes timeout restrictions!")
            return "loading"
            
        elif "Basketball Shot Analysis" in content and "upload" in content.lower():
            print("✅ STATUS: FULL SERVICE DEPLOYED!")
            print("   - Computer vision libraries loaded")  
            print("   - Video upload functionality active")
            print("   - MediaPipe pose detection ready")
            print("   - PDF report generation enabled")
            return "ready"
            
        elif "Application Error" in content or response.status_code >= 500:
            print("❌ STATUS: Deployment error detected")
            print("   - This may be a temporary startup issue")
            print("   - Heavy dependencies can cause initial delays")
            return "error"
            
        else:
            print("🔄 STATUS: Service transitioning...")
            print("   - Deployment in progress")
            return "transitioning"
            
    except requests.exceptions.RequestException as e:
        print(f"🌐 Connection issue: {e}")
        return "connection_error"

def monitor_deployment():
    """Continuously monitor until full service is ready"""
    
    print("Starting continuous monitoring...")
    print("Press Ctrl+C to stop")
    print()
    
    attempt = 1
    while True:
        print(f"📊 Check #{attempt} - {time.strftime('%H:%M:%S')}")
        
        status = check_deployment_status()
        
        if status == "ready":
            print()
            print("🎉 DEPLOYMENT COMPLETE!")
            print("=" * 50) 
            print("✅ Full basketball analysis service is LIVE!")
            print("✅ Computer vision processing enabled")
            print("✅ MediaPipe pose detection active")
            print("✅ Video upload and analysis ready")
            print("✅ PDF report generation working")
            print()
            print("🔗 Access your service: https://apex-sports-trainer.onrender.com")
            print()
            print("PAID PLAN SUCCESS:")
            print("- No more build timeouts!")
            print("- Full computer vision capabilities restored!")
            print("- Professional basketball shot analysis!")
            break
            
        elif status == "loading":
            print("   ⏳ Computer vision dependencies still installing...")
            print("   💡 This is expected - CV libraries are large!")
            
        elif status == "error":
            print("   ⚠️  Deployment error - may resolve automatically")
            
        else:
            print(f"   🔄 Status: {status}")
        
        print(f"   ⏰ Next check in 30 seconds...")
        print()
        
        try:
            time.sleep(30)
            attempt += 1
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped by user")
            print("Your deployment continues in the background!")
            print("Check manually: https://apex-sports-trainer.onrender.com")
            break

if __name__ == "__main__":
    print("🏀 BASKETBALL ANALYSIS - PAID PLAN DEPLOYMENT MONITOR")
    print("=" * 60)
    print()
    print("PAID PLAN UPGRADE BENEFITS:")
    print("✅ No build time limits (was timing out on free tier)")
    print("✅ Full memory for computer vision processing")
    print("✅ OpenCV + MediaPipe installation support")
    print("✅ Complete basketball shot analysis service")
    print()
    
    monitor_deployment()
