#!/usr/bin/env python3
"""
Quick Status Check for Basketball Analysis Deployment
"""

import requests
import time
from datetime import datetime

def check_status():
    url = 'https://apex-sports-trainer.onrender.com'
    
    print(f"🔍 DEPLOYMENT STATUS CHECK - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    try:
        response = requests.get(url, timeout=10)
        content = response.text.lower()
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            if 'loading full version' in content:
                print("⚠️  STATUS: Dependencies still loading")
                print("📦 OpenCV, MediaPipe being installed...")
                print("⏱️  ETA: 3-5 more minutes")
                return "loading"
            elif 'upload' in content and 'basketball' in content:
                print("✅ STATUS: FULL VERSION READY!")
                print("🏀 Basketball analysis service is live!")
                return "ready"
            elif 'error' in content:
                print("❌ STATUS: Error detected")
                return "error"
            else:
                print("🔧 STATUS: Unknown state")
                return "unknown"
        else:
            print(f"⚠️  HTTP Error: {response.status_code}")
            return "http_error"
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return "connection_error"

if __name__ == "__main__":
    status = check_status()
    
    if status == "loading":
        print("\n💡 WHAT'S HAPPENING:")
        print("- Render is installing computer vision libraries")
        print("- This includes opencv-python-headless and mediapipe")
        print("- Large dependencies take time to download and install")
        print("\n🔄 NEXT STEPS:")
        print("- Wait 3-5 minutes")
        print("- Refresh the URL to check progress")
        print("- The page will update automatically when ready")
    elif status == "ready":
        print("\n🎉 READY TO USE:")
        print("- Visit: https://apex-sports-trainer.onrender.com")
        print("- Upload basketball videos")
        print("- Get complete shot analysis")
    else:
        print("\n🔍 CHECK RENDER DASHBOARD:")
        print("- Look for build/deploy logs")
        print("- Check for any error messages")
        print("- Verify all dependencies installed successfully")
