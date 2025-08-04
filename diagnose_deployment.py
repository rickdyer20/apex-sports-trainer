#!/usr/bin/env python3
"""
Quick Diagnostic - Basketball Analysis Service
Test if the web app can start without errors
"""

import sys
import os

def test_web_app_startup():
    """Test if the web app can start successfully"""
    print("🏀 BASKETBALL ANALYSIS SERVICE - STARTUP TEST")
    print("=" * 55)
    
    try:
        print("🔍 Testing web app import...")
        from web_app import app
        print("✅ Web app imported successfully")
        
        print("\n🔍 Testing app configuration...")
        print(f"✅ App name: {app.name}")
        print(f"✅ Debug mode: {app.debug}")
        
        print("\n🔍 Testing routes...")
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            print(f"✅ Health endpoint: {response.status_code}")
            
            # Test main page
            response = client.get('/')
            print(f"✅ Main page: {response.status_code}")
        
        print("\n🎉 WEB APP IS WORKING!")
        print("💡 The issue might be with your deployment, not the code")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Missing dependencies - check requirements.txt")
        return False
    except Exception as e:
        print(f"❌ App error: {e}")
        print("💡 Check your code for syntax or runtime errors")
        return False

def test_basketball_analysis():
    """Test if the core analysis service works"""
    print("\n🏀 Testing Basketball Analysis Service...")
    try:
        from basketball_analysis_service import BasketballAnalysisService
        service = BasketballAnalysisService()
        print("✅ Basketball Analysis Service working")
        return True
    except Exception as e:
        print(f"❌ Analysis service error: {e}")
        return False

def main():
    """Run diagnostic tests"""
    web_app_ok = test_web_app_startup()
    analysis_ok = test_basketball_analysis()
    
    if web_app_ok and analysis_ok:
        print("\n🎉 YOUR APP IS WORKING LOCALLY!")
        print("\n📋 DEPLOYMENT TROUBLESHOOTING:")
        print("1. Redeploy to Render with updated requirements.txt")
        print("2. Check Render logs for specific error messages")
        print("3. Verify environment variables are set correctly")
        print("4. Make sure you're using the Starter Plan ($7/month)")
        print("\n🔗 RENDER DEPLOYMENT STEPS:")
        print("• git add . && git commit -m 'Fix dependencies' && git push")
        print("• Go to Render dashboard and trigger manual deploy")
        print("• Check deployment logs for any build errors")
    else:
        print("\n❌ LOCAL ISSUES FOUND - FIX THESE FIRST")

if __name__ == "__main__":
    main()
