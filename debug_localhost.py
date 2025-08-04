#!/usr/bin/env python3
"""
Debug Local Server Issues
Test what's preventing the localhost from starting
"""

import os
import sys
import traceback

def test_flask_basic():
    """Test basic Flask functionality"""
    print("🔍 Testing basic Flask functionality...")
    try:
        from flask import Flask
        test_app = Flask(__name__)
        
        @test_app.route('/')
        def hello():
            return "Basketball Analysis Service - Test Page"
            
        @test_app.route('/health')
        def health():
            return {"status": "ok", "message": "Test server running"}
            
        print("✅ Basic Flask app created successfully")
        return test_app
    except Exception as e:
        print(f"❌ Flask basic test failed: {e}")
        return None

def test_imports():
    """Test all required imports"""
    print("\n🔍 Testing imports...")
    imports_status = {}
    
    try:
        import flask
        imports_status['flask'] = f"✅ {flask.__version__}"
    except Exception as e:
        imports_status['flask'] = f"❌ {e}"
    
    try:
        import cv2
        imports_status['opencv'] = f"✅ {cv2.__version__}"
    except Exception as e:
        imports_status['opencv'] = f"❌ {e}"
    
    try:
        import mediapipe
        imports_status['mediapipe'] = f"✅ {mediapipe.__version__}"
    except Exception as e:
        imports_status['mediapipe'] = f"❌ {e}"
    
    try:
        import numpy
        imports_status['numpy'] = f"✅ {numpy.__version__}"
    except Exception as e:
        imports_status['numpy'] = f"❌ {e}"
    
    for lib, status in imports_status.items():
        print(f"  {lib}: {status}")
    
    return all("✅" in status for status in imports_status.values())

def test_web_app_import():
    """Test importing the main web app"""
    print("\n🔍 Testing web_app.py import...")
    try:
        # Try to import the main app
        from web_app import app
        print("✅ web_app.py imported successfully")
        print(f"✅ App name: {app.name}")
        return app
    except Exception as e:
        print(f"❌ web_app.py import failed: {e}")
        print("\nFull error traceback:")
        traceback.print_exc()
        return None

def test_basketball_service():
    """Test the basketball analysis service"""
    print("\n🔍 Testing basketball_analysis_service.py...")
    try:
        from basketball_analysis_service import BasketballAnalysisService
        service = BasketballAnalysisService()
        print("✅ Basketball Analysis Service imported and created")
        return True
    except Exception as e:
        print(f"❌ Basketball service failed: {e}")
        return False

def start_simple_test_server():
    """Start a minimal test server"""
    print("\n🚀 Starting simple test server...")
    try:
        test_app = test_flask_basic()
        if test_app:
            print("📍 Test server starting at: http://127.0.0.1:5001")
            print("💡 Try opening this URL in your browser")
            print("🛑 Press Ctrl+C to stop")
            test_app.run(host='127.0.0.1', port=5001, debug=True)
    except Exception as e:
        print(f"❌ Test server failed: {e}")

def main():
    """Run diagnostic tests"""
    print("🏀 LOCALHOST TROUBLESHOOTING")
    print("=" * 50)
    
    # Test 1: Basic imports
    imports_ok = test_imports()
    
    # Test 2: Web app import
    app = test_web_app_import()
    
    # Test 3: Basketball service
    service_ok = test_basketball_service()
    
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY:")
    print(f"  Imports: {'✅' if imports_ok else '❌'}")
    print(f"  Web App: {'✅' if app else '❌'}")
    print(f"  Basketball Service: {'✅' if service_ok else '❌'}")
    
    if app:
        print("\n🎉 Your web app should work!")
        print("\n💡 Try these commands:")
        print("1. python web_app.py")
        print("2. python -m flask --app web_app run")
        print("3. Or run this script with --test-server")
    else:
        print("\n❌ Issues found - check error messages above")
        print("\n🔧 If you want to test with a simple server:")
        print("   python debug_localhost.py --test-server")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test-server":
        start_simple_test_server()
    else:
        main()
