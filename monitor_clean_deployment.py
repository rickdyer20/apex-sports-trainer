#!/usr/bin/env python3
"""
CLEAN DEPLOYMENT MONITOR - Fundamental Issue Test
================================================

This monitors the deployment of the minimal diagnostic service
to determine if we've resolved the fundamental deployment issue.

If this simple service deploys successfully:
✅ Platform configuration is working
✅ Can proceed to add basketball analysis features

If this fails:
❌ There's a deeper platform/account issue
❌ Need to investigate Render account settings
"""

import requests
import time
from datetime import datetime

def test_fundamental_deployment():
    """Test if the clean diagnostic service deploys"""
    
    url = "https://apex-sports-trainer.onrender.com"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            if "DIAGNOSTIC SERVICE WORKING" in content:
                return "success", "✅ Clean deployment successful!"
            elif "Basketball" in content:
                return "partial", "⚠️ Old service still cached"
            else:
                return "unknown", f"🔄 Got response but unexpected content"
        else:
            return "error", f"❌ HTTP {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "building", "🔄 Service building/deploying"
    except requests.exceptions.Timeout:
        return "timeout", "⏱️ Service slow to respond"
    except Exception as e:
        return "error", f"❌ {str(e)[:50]}"

def main():
    print("🔧 FUNDAMENTAL DEPLOYMENT TEST")
    print("=" * 45)
    print()
    print("TESTING: Minimal diagnostic service deployment")
    print("PURPOSE: Confirm platform configuration fix")
    print()
    print("DEPLOYMENT CHANGES MADE:")
    print("✅ Removed render.yaml, railway.json, Dockerfile")
    print("✅ Simplified wsgi.py to single import")
    print("✅ Minimal requirements.txt (Flask + Gunicorn only)")
    print("✅ Standard Procfile configuration")
    print()
    
    start_time = datetime.now()
    check_count = 1
    
    while True:
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"🔍 Check #{check_count} - {datetime.now().strftime('%H:%M:%S')} (Elapsed: {elapsed:.0f}s)")
        
        status, message = test_fundamental_deployment()
        print(f"   {message}")
        
        if status == "success":
            print()
            print("🎉 FUNDAMENTAL ISSUE RESOLVED!")
            print("=" * 40)
            print(f"✅ Clean deployment successful in {elapsed:.0f} seconds")
            print("✅ Platform configuration is working")
            print("✅ Ready to add basketball analysis features")
            print()
            print("🔗 Service URL: https://apex-sports-trainer.onrender.com")
            print()
            print("NEXT STEPS:")
            print("1. Gradually add basketball analysis features")
            print("2. Test each addition incrementally")
            print("3. Avoid complex import chains")
            break
            
        elif status == "partial":
            print("   💡 May need cache clearing or full redeploy")
            
        elif status == "building":
            print(f"   ⏳ Deployment in progress (elapsed: {elapsed:.0f}s)")
            if elapsed > 300:  # 5 minutes
                print("   ⚠️ Taking longer than expected for minimal service")
                
        elif status == "error":
            print(f"   🔍 Error detected (elapsed: {elapsed:.0f}s)")
            if elapsed > 180:  # 3 minutes
                print("   ❌ Minimal service failing - may be platform issue")
        
        print(f"   ⏰ Next check in 20 seconds...")
        print()
        
        try:
            time.sleep(20)
            check_count += 1
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break

if __name__ == "__main__":
    main()
