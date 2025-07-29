#!/usr/bin/env python3
"""
Advanced Deployment Diagnostics
Try multiple diagnostic approaches to figure out what's wrong
"""

import requests
import time
import json

def advanced_diagnostics():
    """Run comprehensive tests"""
    
    base_url = "https://clownfish-app-nlqru.ondigitalocean.app"
    
    print("🔍 ADVANCED DEPLOYMENT DIAGNOSTICS")
    print("=" * 60)
    
    # Test 1: Check if server responds at all
    print("\n1️⃣ Testing Server Response")
    try:
        response = requests.get(base_url, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    # Test 2: Try different endpoints
    print("\n2️⃣ Testing Multiple Endpoints")
    endpoints = ["/", "/health", "/status", "/test", "/favicon.ico"]
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            print(f"  {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"  {endpoint}: ERROR - {e}")
    
    # Test 3: Check response headers for clues
    print("\n3️⃣ Analyzing Response Headers")
    try:
        response = requests.head(base_url, timeout=10)
        headers = dict(response.headers)
        important_headers = [
            'server', 'x-powered-by', 'content-type', 
            'x-digitalocean-app', 'x-cache', 'x-forwarded-proto'
        ]
        for header in important_headers:
            value = headers.get(header, headers.get(header.title(), 'Not found'))
            print(f"  {header}: {value}")
    except Exception as e:
        print(f"❌ Header check failed: {e}")
    
    # Test 4: Test with different HTTP methods
    print("\n4️⃣ Testing HTTP Methods")
    methods = ['GET', 'POST', 'HEAD', 'OPTIONS']
    for method in methods:
        try:
            response = requests.request(method, base_url, timeout=10)
            print(f"  {method}: {response.status_code}")
        except Exception as e:
            print(f"  {method}: ERROR - {e}")
    
    print("\n✨ Diagnostics Complete!")
    print("\nIf all tests show 404, the issue is likely:")
    print("- Flask app not starting on DigitalOcean")
    print("- Port binding problem")  
    print("- DigitalOcean configuration issue")

if __name__ == "__main__":
    advanced_diagnostics()
