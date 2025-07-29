#!/usr/bin/env python3
"""
Render Deployment Monitor
Real-time monitoring and status checking for Render deployment
"""

import requests
import time
import json
from datetime import datetime

def check_render_status(url):
    """Check if Render app is responding"""
    try:
        response = requests.get(url, timeout=10)
        return {
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'content_length': len(response.text),
            'headers': dict(response.headers),
            'success': response.status_code == 200
        }
    except requests.exceptions.ConnectionError:
        return {'error': 'Connection refused - app may be starting up'}
    except requests.exceptions.Timeout:
        return {'error': 'Request timed out - app may be overloaded'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}

def monitor_deployment():
    """Monitor deployment with user input for URL"""
    print("🚀 RENDER DEPLOYMENT MONITOR")
    print("=" * 50)
    
    # Get URL from user
    render_url = input("\n📝 Enter your Render app URL (or press Enter to use example): ").strip()
    
    if not render_url:
        print("⚠️  No URL provided. You can find your URL in the Render dashboard after deployment.")
        print("   It will look like: https://basketball-analysis-service-abcd123.onrender.com")
        return
    
    # Clean URL
    if not render_url.startswith('http'):
        render_url = 'https://' + render_url
    
    print(f"\n🔍 Monitoring: {render_url}")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    print("\n" + "=" * 60)
    
    # Monitor loop
    attempt = 1
    max_attempts = 20  # Monitor for ~10 minutes
    
    while attempt <= max_attempts:
        print(f"\n🔄 Attempt {attempt}/{max_attempts} - {datetime.now().strftime('%H:%M:%S')}")
        
        # Test main endpoints
        endpoints = [
            ('/', 'Home Page'),
            ('/health', 'Health Check'),
            ('/status', 'Status Check')
        ]
        
        success_count = 0
        
        for endpoint, name in endpoints:
            test_url = render_url.rstrip('/') + endpoint
            result = check_render_status(test_url)
            
            if 'error' in result:
                print(f"  ❌ {name}: {result['error']}")
            elif result['success']:
                print(f"  ✅ {name}: OK ({result['response_time']:.2f}s)")
                success_count += 1
            else:
                print(f"  ⚠️  {name}: HTTP {result['status_code']}")
        
        # Status summary
        if success_count == len(endpoints):
            print(f"\n🎉 SUCCESS! All {success_count} endpoints working!")
            print("✅ Your Render deployment is live and healthy!")
            break
        elif success_count > 0:
            print(f"\n🔶 PARTIAL: {success_count}/{len(endpoints)} endpoints working")
            print("   App is starting up - this is normal")
        else:
            print(f"\n🔴 WAITING: App not responding yet")
            if attempt <= 5:
                print("   This is normal - Render apps take 2-5 minutes to start")
            elif attempt <= 10:
                print("   Still starting up - be patient")
            else:
                print("   Taking longer than expected - check Render logs")
        
        # Wait before next attempt
        if attempt < max_attempts and success_count < len(endpoints):
            print("   ⏳ Waiting 30 seconds...")
            time.sleep(30)
        
        attempt += 1
    
    # Final status
    if success_count < len(endpoints):
        print(f"\n⚠️  TIMEOUT: App not fully responsive after {max_attempts} attempts")
        print("🔍 Troubleshooting steps:")
        print("   1. Check Render dashboard for build/deploy logs")
        print("   2. Verify your app.yaml configuration")
        print("   3. Check if the app is still building")
        print("   4. Look for error messages in Render logs")

def quick_test():
    """Quick single test for immediate feedback"""
    render_url = input("Enter your Render URL for quick test: ").strip()
    
    if not render_url:
        print("No URL provided")
        return
    
    if not render_url.startswith('http'):
        render_url = 'https://' + render_url
    
    print(f"\n🚀 Quick testing: {render_url}")
    
    result = check_render_status(render_url)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        print("\n💡 Common reasons:")
        print("   - App is still building/starting up")
        print("   - Wrong URL format")
        print("   - Build failed (check Render dashboard)")
    elif result['success']:
        print(f"✅ SUCCESS! App is live ({result['response_time']:.2f}s response)")
        print(f"📊 Response size: {result['content_length']} characters")
    else:
        print(f"⚠️  HTTP {result['status_code']} - App started but has issues")

def main():
    """Main menu"""
    print("🎯 RENDER DEPLOYMENT MONITORING TOOL")
    print("=" * 40)
    print("1. 🔄 Continuous monitoring (recommended)")
    print("2. ⚡ Quick single test")
    print("3. 📋 Show monitoring tips")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        monitor_deployment()
    elif choice == '2':
        quick_test()
    elif choice == '3':
        print("\n📋 MONITORING TIPS:")
        print("• Render apps take 2-5 minutes to build and start")
        print("• Free tier apps 'sleep' after 15 minutes of inactivity")
        print("• First request after sleep takes ~30 seconds to wake up")
        print("• Check Render dashboard for detailed build logs")
        print("• URL format: https://your-service-name-hash.onrender.com")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
