#!/usr/bin/env python3
"""
Quick Deployment Status Checker
Check common deployment URLs and provide status
"""

import requests
import time
from datetime import datetime

def check_common_digitalocean_urls():
    """Check common DigitalOcean URL patterns"""
    
    # Common URL patterns for apex-sports-trainer
    possible_urls = [
        "https://apex-sports-trainer.ondigitalocean.app",
        "https://apex-sports-trainer-dev.ondigitalocean.app", 
        "https://apex-sports-trainer-main.ondigitalocean.app",
        "https://apex-sports-trainer-master.ondigitalocean.app"
    ]
    
    print("🔍 Checking common DigitalOcean URL patterns...")
    print("=" * 50)
    
    found_apps = []
    
    for url in possible_urls:
        try:
            print(f"Checking: {url}")
            response = requests.get(f"{url}/health", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ FOUND ACTIVE APP: {url}")
                found_apps.append(url)
            else:
                print(f"⚠️ Responded but not ready (status: {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ No app found at this URL")
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout - may be starting up")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        print()
    
    return found_apps

def manual_url_check():
    """Allow user to manually input URL to check"""
    print("\n📝 Manual URL Check")
    print("=" * 30)
    
    while True:
        url = input("Enter your DigitalOcean app URL (or 'quit' to exit): ").strip()
        
        if url.lower() in ['quit', 'exit', 'q']:
            break
            
        if not url.startswith('http'):
            url = f"https://{url}"
            
        try:
            print(f"\n🔍 Checking: {url}")
            
            # Check health endpoint
            health_response = requests.get(f"{url}/health", timeout=15)
            if health_response.status_code == 200:
                print("✅ Health check: PASSED")
                
                # Check main page
                main_response = requests.get(url, timeout=15)
                if main_response.status_code == 200:
                    print("✅ Main page: LOADED")
                    print(f"🎉 SUCCESS! Your app is running at: {url}")
                    
                    # Check for basketball content
                    if "basketball" in main_response.text.lower():
                        print("✅ Basketball content detected - deployment looks good!")
                    else:
                        print("⚠️ Basketball content not found - may be wrong app")
                        
                else:
                    print(f"⚠️ Main page: Status {main_response.status_code}")
                    
            else:
                print(f"❌ Health check failed: Status {health_response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - URL may be incorrect or app not deployed")
        except requests.exceptions.Timeout:
            print("⏱️ Request timed out - app may be slow or starting up")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        print("\n" + "="*50)

def main():
    """Main function"""
    print("🌊 DigitalOcean Deployment Status Checker")
    print("Basketball Analysis Service")
    print("⏰", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    # First, check common URL patterns
    found_apps = check_common_digitalocean_urls()
    
    if found_apps:
        print(f"\n🎉 Found {len(found_apps)} active app(s):")
        for app in found_apps:
            print(f"  ✅ {app}")
    else:
        print("\n⚠️ No apps found at common URLs")
        print("Your app may have a different URL pattern")
    
    # Offer manual URL checking
    print("\n" + "="*60)
    choice = input("Would you like to manually check a specific URL? (y/n): ").strip().lower()
    
    if choice in ['y', 'yes']:
        manual_url_check()
    
    print("\n📋 Next Steps:")
    print("1. If app found: Test video upload functionality")
    print("2. If not found: Check DigitalOcean dashboard for deployment status")
    print("3. Check build logs if deployment failed")
    print("4. Monitor with: python monitor_deployment.py <your-url>")

if __name__ == "__main__":
    main()
