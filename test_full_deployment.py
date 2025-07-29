#!/usr/bin/env python3
"""
Test Full Basketball Analysis Deployment
Progressive testing as we restore functionality
"""

import requests
import time

def test_basketball_analysis_deployment(url):
    """Test the basketball analysis deployment"""
    
    print("🏀 TESTING BASKETBALL ANALYSIS DEPLOYMENT")
    print(f"URL: {url}")
    print("=" * 60)
    
    # Test basic endpoints
    endpoints = [
        ("", "Home Page"),
        ("/health", "Health Check"),
        ("/analyze", "Analysis Page (if available)"),
        ("/api/status", "API Status (if available)")
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        print(f"\n🔍 Testing: {description}")
        test_url = url.rstrip('/') + endpoint
        print(f"URL: {test_url}")
        
        try:
            response = requests.get(test_url, timeout=15)
            status = response.status_code
            results[endpoint] = status
            
            if status == 200:
                print("✅ SUCCESS!")
                # Check content for clues about what's loaded
                content = response.text.lower()
                if 'basketball' in content:
                    print("  🏀 Full basketball analysis detected!")
                elif 'loading' in content or 'fallback' in content:
                    print("  ⚠️  Fallback mode - dependencies still loading")
                elif 'wsgi' in content:
                    print("  🔧 Basic WSGI app running")
                
                # Show relevant content preview
                if 'json' in response.headers.get('content-type', ''):
                    print(f"  JSON: {response.json()}")
                else:
                    preview = response.text[:150].replace('\n', ' ')
                    print(f"  Preview: {preview}...")
                    
            elif status == 404:
                print("❌ Not found")
            else:
                print(f"⚠️  HTTP {status}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ CONNECTION ERROR: {e}")
            results[endpoint] = 'error'
        
        print("-" * 50)
    
    # Summary
    success_count = sum(1 for status in results.values() if status == 200)
    print(f"\n📊 RESULTS: {success_count}/{len(endpoints)} endpoints responding")
    
    # Determine deployment status
    if results.get('', 0) == 200:
        print("🎉 DEPLOYMENT ACTIVE!")
        
        if results.get('/analyze', 0) == 200:
            print("✅ FULL BASKETBALL ANALYSIS: Ready!")
            print("🚀 You can now upload videos for analysis")
        elif 'loading' in str(results):
            print("⚠️  PARTIAL DEPLOYMENT: Some features still loading")
            print("🔄 Check again in a few minutes as dependencies install")
        else:
            print("🔧 BASIC DEPLOYMENT: Simple version running")
            print("📈 Full features being restored incrementally")
    else:
        print("❌ DEPLOYMENT ISSUE: Check Render dashboard for errors")
    
    return results

if __name__ == "__main__":
    # Get URL from user
    render_url = input("Enter your Render app URL: ").strip()
    
    if not render_url:
        print("Please provide your Render URL")
        exit(1)
    
    if not render_url.startswith('http'):
        render_url = 'https://' + render_url
    
    test_basketball_analysis_deployment(render_url)
