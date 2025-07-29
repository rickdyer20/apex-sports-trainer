#!/usr/bin/env python3
"""
Test Render Deployment
Quick verification script for Render deployed app
"""

import requests
import time

def test_render_deployment(base_url):
    """Test the Render deployed app"""
    
    print("🚀 TESTING RENDER DEPLOYMENT")
    print(f"URL: {base_url}")
    print("=" * 60)
    
    # Test endpoints
    endpoints = [
        ("", "Home Page"),
        ("/health", "Health Check"),
        ("/status", "Status Check")
    ]
    
    success_count = 0
    
    for endpoint, description in endpoints:
        print(f"\n🔍 Testing: {description}")
        url = f"{base_url}{endpoint}"
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, timeout=15)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS!")
                success_count += 1
                
                # Show response preview
                if 'json' in response.headers.get('content-type', ''):
                    print(f"JSON Response: {response.json()}")
                else:
                    print(f"HTML Response: {len(response.text)} characters")
            else:
                print("❌ FAILED!")
                print(f"Error: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ CONNECTION ERROR: {e}")
        
        print("-" * 50)
    
    # Summary
    print(f"\n📊 RESULTS: {success_count}/{len(endpoints)} endpoints working")
    
    if success_count == len(endpoints):
        print("🎉 ALL TESTS PASSED! Render deployment successful!")
        print("\n🔄 Next Steps:")
        print("1. ✅ Basic Flask app is working on Render")
        print("2. 🔄 Gradually add back basketball analysis features")
        print("3. 🔄 Add dependencies (OpenCV, MediaPipe, etc.)")
        print("4. 🔄 Test video upload and analysis functionality")
    else:
        print("⚠️  Some endpoints failed - check Render logs")
    
    return success_count == len(endpoints)

if __name__ == "__main__":
    # You'll need to update this URL once Render gives you the deployment URL
    render_url = input("Enter your Render app URL (e.g., https://basketball-analysis-service-abcd.onrender.com): ").strip()
    
    if render_url:
        test_render_deployment(render_url)
    else:
        print("Please provide the Render app URL to test deployment")
