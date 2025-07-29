#!/usr/bin/env python3
"""
Test the deployed DigitalOcean app endpoints
"""

import requests
import time

def test_endpoint(url, description):
    """Test a single endpoint"""
    print(f"\n🔍 Testing: {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            if len(response.text) < 500:
                print(f"Response: {response.text[:200]}...")
            else:
                print(f"Response length: {len(response.text)} characters")
        else:
            print("❌ FAILED!")
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CONNECTION ERROR: {e}")
    
    print("-" * 50)

def main():
    """Test all endpoints"""
    base_url = "https://clownfish-app-nlqru.ondigitalocean.app"
    
    print("🚀 Testing DigitalOcean Deployment")
    print(f"Base URL: {base_url}")
    print("=" * 60)
    
    # Test endpoints
    endpoints = [
        ("", "Home Page"),
        ("/health", "Health Check"),
        ("/test", "Simple Test")
    ]
    
    for endpoint, description in endpoints:
        test_endpoint(f"{base_url}{endpoint}", description)
        time.sleep(1)  # Brief pause between requests
    
    print("\n✨ Testing Complete!")

if __name__ == "__main__":
    main()
