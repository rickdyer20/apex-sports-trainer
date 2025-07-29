#!/usr/bin/env python3
"""
Quick Render Status Check
Check if deployment is ready
"""

import requests
import sys

def check_render_ready():
    """Check common Render URLs to see if deployment is active"""
    
    print("🔍 RENDER DEPLOYMENT STATUS CHECK")
    print("=" * 40)
    
    # Common Render URL patterns for your app
    possible_urls = [
        "https://basketball-analysis-service.onrender.com",
        "https://basketball-analysis-service-latest.onrender.com", 
        "https://apex-sports-trainer.onrender.com"
    ]
    
    print("🌐 Checking common URL patterns...")
    
    for url in possible_urls:
        print(f"\n🔍 Testing: {url}")
        try:
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                print(f"✅ FOUND! Your app is live at: {url}")
                print(f"📄 Response preview: {response.text[:100]}...")
                return url
            else:
                print(f"⚠️  HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Not found")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n📋 STATUS SUMMARY:")
    print("❌ No active deployment found at common URLs")
    print("\n💡 NEXT STEPS:")
    print("1. 🔍 Check your Render dashboard for the exact URL")
    print("2. 🏗️  Verify the deployment is complete (not still building)")
    print("3. 📋 Copy the exact URL from Render and test manually")
    print("4. 🔧 If deployment failed, check build logs in Render dashboard")
    
    return None

if __name__ == "__main__":
    found_url = check_render_ready()
    
    if found_url:
        print(f"\n🎉 SUCCESS! Use this URL: {found_url}")
        
        # Test key endpoints
        print("\n🧪 Testing key endpoints:")
        endpoints = ['/health', '/status']
        
        for endpoint in endpoints:
            try:
                test_url = found_url + endpoint
                response = requests.get(test_url, timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ {endpoint}: Working")
                else:
                    print(f"  ⚠️  {endpoint}: HTTP {response.status_code}")
            except:
                print(f"  ❌ {endpoint}: Failed")
    else:
        print("\n⏳ Keep checking - deployment may still be in progress")
