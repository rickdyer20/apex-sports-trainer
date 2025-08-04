#!/usr/bin/env python3
"""
Quick Local Test - Basketball Analysis Service
Test the web app functionality locally before cloud deployment
"""

import os
import sys
import time
import subprocess
from threading import Thread
import requests
import json

def test_imports():
    """Test that all required imports work"""
    print("🔍 Testing imports...")
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
        
        import cv2
        print(f"✅ OpenCV {cv2.__version__}")
        
        import mediapipe as mp
        print(f"✅ MediaPipe {mp.__version__}")
        
        import numpy as np
        print(f"✅ NumPy {np.__version__}")
        
        # Test basketball analysis service import
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from basketball_analysis_service import BasketballAnalysisService
        print("✅ Basketball Analysis Service imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_service_creation():
    """Test creating the analysis service"""
    print("\n🏀 Testing service creation...")
    try:
        from basketball_analysis_service import BasketballAnalysisService
        service = BasketballAnalysisService()
        print("✅ Basketball Analysis Service created successfully")
        return True
    except Exception as e:
        print(f"❌ Service creation error: {e}")
        return False

def test_web_app_import():
    """Test importing the web app"""
    print("\n🌐 Testing web app import...")
    try:
        import web_app
        print("✅ Web app imported successfully")
        return True
    except Exception as e:
        print(f"❌ Web app import error: {e}")
        return False

def run_server_test():
    """Start the Flask server for testing"""
    print("\n🚀 Starting Flask server...")
    try:
        os.environ['FLASK_APP'] = 'web_app.py'
        os.environ['FLASK_ENV'] = 'development'
        
        # Import and run the app
        import web_app
        print("✅ Flask app ready to start")
        print("📝 To start manually, run: python -m flask run --host=127.0.0.1 --port=5000")
        print("📝 Or run: python web_app.py")
        return True
        
    except Exception as e:
        print(f"❌ Server setup error: {e}")
        return False

def main():
    """Run all tests"""
    print("🏀 BASKETBALL ANALYSIS SERVICE - QUICK LOCAL TEST")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test 1: Imports
    if not test_imports():
        all_tests_passed = False
    
    # Test 2: Service Creation
    if not test_service_creation():
        all_tests_passed = False
    
    # Test 3: Web App Import
    if not test_web_app_import():
        all_tests_passed = False
    
    # Test 4: Server Setup
    if not run_server_test():
        all_tests_passed = False
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Your basketball analysis service is ready!")
        print("\n📋 NEXT STEPS:")
        print("1. Start the server manually with: python web_app.py")
        print("2. Open browser to: http://127.0.0.1:5000")
        print("3. Upload a basketball shot video to test")
        print("4. Verify thumb flick detection and other analysis features")
        print("5. Once confirmed working, proceed with Google Cloud deployment")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
    
    return all_tests_passed

if __name__ == "__main__":
    main()
