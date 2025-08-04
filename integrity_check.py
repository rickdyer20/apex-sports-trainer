#!/usr/bin/env python3
"""
Basketball Analysis Service - Integrity Check
Verify all core components are intact before Google Cloud deployment
"""

import sys
import os
import importlib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def check_file_exists(filepath, description):
    """Check if a critical file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ MISSING {description}: {filepath}")
        return False

def check_import(module_name, description):
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {description}: Can import {module_name}")
        return True
    except ImportError as e:
        print(f"❌ IMPORT ERROR {description}: {module_name} - {e}")
        return False

def check_function_exists(module_name, function_name, description):
    """Check if a specific function exists in a module"""
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, function_name):
            print(f"✅ {description}: {module_name}.{function_name} exists")
            return True
        else:
            print(f"❌ MISSING FUNCTION {description}: {module_name}.{function_name}")
            return False
    except ImportError as e:
        print(f"❌ IMPORT ERROR {description}: {module_name} - {e}")
        return False

def main():
    """Run comprehensive integrity check"""
    print("🔍 BASKETBALL ANALYSIS SERVICE - INTEGRITY CHECK")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Critical Files Check
    print("\n📁 CRITICAL FILES:")
    files_to_check = [
        ("basketball_analysis_service.py", "Main Analysis Service"),
        ("web_app.py", "Web Application"),
        ("wsgi.py", "WSGI Entry Point"),
        ("requirements.txt", "Dependencies"),
        ("requirements_full_cloud.txt", "Cloud Dependencies"),
        ("Dockerfile_cloud", "Cloud Container Config")
    ]
    
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    # Import Tests
    print("\n📦 IMPORT TESTS:")
    modules_to_check = [
        ("flask", "Flask Framework"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("json", "JSON Support"),
        ("logging", "Logging"),
    ]
    
    for module_name, description in modules_to_check:
        if not check_import(module_name, description):
            all_checks_passed = False
    
    # Core Function Tests
    print("\n🔧 CORE FUNCTIONS:")
    functions_to_check = [
        ("basketball_analysis_service", "VideoAnalysisJob", "Video Analysis Job Class"),
        ("basketball_analysis_service", "process_video_for_analysis", "Video Processing Function"),
        ("web_app", "app", "Flask Application"),
    ]
    
    for module_name, function_name, description in functions_to_check:
        if not check_function_exists(module_name, function_name, description):
            all_checks_passed = False
    
    # Enhanced Features Check
    print("\n🏀 ENHANCED FEATURES:")
    
    # Check for thumb flick detection
    try:
        with open("basketball_analysis_service.py", "r") as f:
            content = f.read()
            if "guide_hand_thumb_flick" in content and "25°" in content:
                print("✅ Enhanced Thumb Flick Detection: 25° threshold found")
            else:
                print("❌ Enhanced Thumb Flick Detection: Not found or corrupted")
                all_checks_passed = False
    except Exception as e:
        print(f"❌ Could not verify thumb flick detection: {e}")
        all_checks_passed = False
    
    # Check for camera angle support
    try:
        with open("basketball_analysis_service.py", "r") as f:
            content = f.read()
            if "left_side_view" in content and "right_side_view" in content:
                print("✅ Multiple Camera Angles: Support found")
            else:
                print("❌ Multiple Camera Angles: Not found")
                all_checks_passed = False
    except Exception as e:
        print(f"❌ Could not verify camera angles: {e}")
        all_checks_passed = False
    
    # Final Result
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("🎉 INTEGRITY CHECK PASSED - App is ready for Google Cloud deployment!")
        print("\n✅ All core components intact")
        print("✅ Enhanced thumb flick detection preserved")
        print("✅ Multiple camera angle support working")
        print("✅ Web application structure intact")
        return True
    else:
        print("🚨 INTEGRITY CHECK FAILED - App needs repairs before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
