#!/usr/bin/env python3
"""
Quick URL Tester for DigitalOcean App
Test specific endpoints to diagnose 404 issues
"""

import requests
import json
from datetime import datetime

def test_url_endpoints(base_url):
    """Test various endpoints on the deployed app"""
    
    print(f"🔍 Testing DigitalOcean App: {base_url}")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # List of endpoints to test
    endpoints = [
        "/",
        "/health", 
        "/api/health",
        "/test",
        "/favicon.ico"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        full_url = f"{base_url.rstrip('/')}{endpoint}"
        print(f"Testing: {full_url}")
        
        try:
            response = requests.get(full_url, timeout=15)
            status = response.status_code
            
            if status == 200:
                print(f"✅ SUCCESS: {status}")
                # Try to get some content info
                content_type = response.headers.get('content-type', 'unknown')
                content_length = len(response.text)
                print(f"   Content-Type: {content_type}")
                print(f"   Content-Length: {content_length} chars")
                
                # If it's JSON, show some data
                if 'json' in content_type:
                    try:
                        data = response.json()
                        print(f"   JSON Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    except:
                        print("   JSON parse failed")
                        
                results[endpoint] = "SUCCESS"
                
            elif status == 404:
                print(f"❌ NOT FOUND: {status}")
                results[endpoint] = "404 - Not Found"
                
            elif status == 500:
                print(f"⚠️ SERVER ERROR: {status}")
                print(f"   Response: {response.text[:200]}")
                results[endpoint] = "500 - Server Error"
                
            else:
                print(f"⚠️ UNEXPECTED: {status}")
                print(f"   Response: {response.text[:100]}")
                results[endpoint] = f"{status} - {response.reason}"
                
        except requests.exceptions.ConnectionError:
            print(f"❌ CONNECTION FAILED")
            results[endpoint] = "Connection Failed"
            
        except requests.exceptions.Timeout:
            print(f"⏱️ TIMEOUT")
            results[endpoint] = "Timeout"
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results[endpoint] = f"Error: {str(e)}"
            
        print()
    
    # Summary
    print("📊 SUMMARY:")
    print("=" * 30)
    working_endpoints = [ep for ep, result in results.items() if result == "SUCCESS"]
    
    if working_endpoints:
        print(f"✅ Working endpoints ({len(working_endpoints)}):")
        for ep in working_endpoints:
            print(f"   {base_url.rstrip('/')}{ep}")
    else:
        print("❌ No working endpoints found")
        
    print(f"\n🔍 Diagnosis:")
    if results.get("/") == "SUCCESS":
        print("✅ Main app is working - no 404 issue!")
    elif results.get("/health") == "SUCCESS":
        print("⚠️ Health endpoint works but main page doesn't - routing issue")
    elif not any("SUCCESS" in str(r) for r in results.values()):
        print("❌ No endpoints working - app may not be running correctly")
        
    return results

if __name__ == "__main__":
    # Test the specific URL provided
    app_url = "https://clownfish-app-nlqru.ondigitalocean.app/"
    test_url_endpoints(app_url)
