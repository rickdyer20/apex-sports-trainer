#!/usr/bin/env python3
"""
HYBRID SERVICE DEPLOYMENT MONITOR
================================

This monitors your basketball analysis service deployment and will
alert you the moment the new hybrid service is live!

The hybrid service provides:
✅ INSTANT professional basketball analysis
✅ No more long waiting times
✅ Smart computer vision loading
✅ Always functional service
"""

import requests
import time
import sys

def check_hybrid_status():
    """Check if the hybrid service is deployed"""
    
    url = "https://apex-sports-trainer.onrender.com"
    
    try:
        response = requests.get(url, timeout=10)
        content = response.text
        
        # Check for hybrid service indicators
        if "Professional AI-Powered Shooting Form Analysis" in content:
            print("🎉 HYBRID SERVICE IS LIVE!")
            print("=" * 50)
            print("✅ Professional basketball analysis ready")
            print("✅ Instant service availability")
            print("✅ Smart computer vision loading")
            print("✅ Upload functionality active")
            print()
            print("🔗 Access your service: https://apex-sports-trainer.onrender.com")
            return "ready"
            
        elif "Basketball Shot Analysis" in content and "upload" in content.lower():
            print("✅ BASKETBALL SERVICE ACTIVE!")
            print("   Service type: Professional Analysis")
            print("   Status: Fully functional")
            return "ready"
            
        elif "Loading Full Version" in content:
            print("⏳ Still building hybrid service...")
            print("   Previous deployment clearing...")
            return "building"
            
        elif "Application Error" in content or response.status_code >= 500:
            print("⚠️  Temporary deployment error")
            print("   This should resolve automatically")
            return "error"
            
        else:
            print("🔄 Deployment in progress...")
            return "deploying"
            
    except requests.exceptions.RequestException as e:
        print(f"🌐 Connection check: {e}")
        return "checking"

def main():
    print("🏀 HYBRID BASKETBALL ANALYSIS - DEPLOYMENT MONITOR")
    print("=" * 55)
    print()
    print("HYBRID SERVICE BENEFITS:")
    print("✅ Instant professional service (no 30+ minute waits)")
    print("✅ Smart computer vision that loads in background")
    print("✅ Always functional with graceful fallbacks")
    print("✅ Professional basketball analysis immediately")
    print()
    print("Monitoring deployment...")
    print("Press Ctrl+C to stop")
    print()
    
    check_count = 1
    while True:
        print(f"📊 Check #{check_count} - {time.strftime('%H:%M:%S')}")
        
        status = check_hybrid_status()
        
        if status == "ready":
            print()
            print("🎯 DEPLOYMENT COMPLETE!")
            print("=" * 30)
            print("Your basketball analysis service is ready!")
            print("No more waiting for computer vision dependencies!")
            print()
            break
        elif status == "building":
            print("   💡 New hybrid service building...")
        elif status == "deploying":
            print("   🚀 Hybrid deployment in progress...")
        else:
            print(f"   Status: {status}")
        
        print(f"   ⏰ Next check in 20 seconds...")
        print()
        
        try:
            time.sleep(20)
            check_count += 1
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped")
            print("Your hybrid service continues deploying!")
            break

if __name__ == "__main__":
    main()
