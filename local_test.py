#!/usr/bin/env python3
"""
Local Testing Script for Basketball Analysis Service
Test all functionality before cloud deployment
"""

import os
import sys
import subprocess
import time
import requests
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 CHECKING DEPENDENCIES...")
    
    required_modules = [
        'flask', 'cv2', 'mediapipe', 'numpy', 'reportlab', 
        'psutil', 'gunicorn'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n🚨 Missing dependencies: {', '.join(missing_modules)}")
        print("Install with: pip install -r requirements_gcloud.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def test_imports():
    """Test critical imports"""
    print("\n🧪 TESTING IMPORTS...")
    
    try:
        from basketball_analysis_service import VideoAnalysisJob, process_video_for_analysis
        print("✅ Basketball analysis service imports")
    except Exception as e:
        print(f"❌ Basketball analysis service: {e}")
        return False
    
    try:
        from web_app import app
        print("✅ Web application imports")
    except Exception as e:
        print(f"❌ Web application: {e}")
        return False
    
    try:
        import mediapipe as mp
        pose = mp.solutions.pose.Pose()
        print("✅ MediaPipe pose detection")
        pose.close()
    except Exception as e:
        print(f"❌ MediaPipe: {e}")
        return False
    
    return True

def start_local_server():
    """Start the local development server"""
    print("\n🚀 STARTING LOCAL SERVER...")
    
    try:
        # Start Flask development server
        from web_app import app
        print("Starting server on http://localhost:5000")
        print("Press Ctrl+C to stop")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    print("\n🏥 TESTING HEALTH ENDPOINT...")
    
    try:
        response = requests.get('http://localhost:5000/health', timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def create_test_video():
    """Create a simple test video for analysis"""
    print("\n🎥 CREATING TEST VIDEO...")
    
    try:
        import cv2
        import numpy as np
        
        # Create a simple test video (basketball shot simulation)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('test_shot.mp4', fourcc, 30.0, (640, 480))
        
        for frame_num in range(90):  # 3 seconds at 30 fps
            # Create a simple animation of a basketball shot
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Draw a stick figure (simple lines)
            # Head
            cv2.circle(img, (320, 100), 20, (255, 255, 255), 2)
            
            # Body
            cv2.line(img, (320, 120), (320, 300), (255, 255, 255), 2)
            
            # Arms (animate for shooting motion)
            arm_angle = frame_num * 2  # Animate arms
            arm_x = int(50 * np.cos(np.radians(arm_angle)))
            arm_y = int(30 * np.sin(np.radians(arm_angle)))
            
            cv2.line(img, (320, 180), (320 - arm_x, 180 + arm_y), (255, 255, 255), 2)
            cv2.line(img, (320, 180), (320 + arm_x, 180 + arm_y), (255, 255, 255), 2)
            
            # Legs
            cv2.line(img, (320, 300), (300, 400), (255, 255, 255), 2)
            cv2.line(img, (320, 300), (340, 400), (255, 255, 255), 2)
            
            # Add frame number
            cv2.putText(img, f"Frame {frame_num}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            out.write(img)
        
        out.release()
        print("✅ Test video created: test_shot.mp4")
        return True
        
    except Exception as e:
        print(f"❌ Test video creation failed: {e}")
        return False

def main():
    """Main testing function"""
    print("🏀 BASKETBALL ANALYSIS SERVICE - LOCAL TESTING")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Install missing packages first.")
        return False
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Check for import errors.")
        return False
    
    # Create test video
    create_test_video()
    
    print("\n" + "=" * 60)
    print("🎉 LOCAL TESTING SETUP COMPLETE!")
    print("\n📋 NEXT STEPS:")
    print("1. Run: python local_test.py --server")
    print("2. Open: http://localhost:5000")
    print("3. Upload: test_shot.mp4 or your own video")
    print("4. Verify: Analysis completes successfully")
    print("5. Check: Enhanced thumb flick detection works")
    
    print("\n🚀 TO START SERVER:")
    print("python local_test.py --server")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--server':
        # Start the server
        start_local_server()
    elif len(sys.argv) > 1 and sys.argv[1] == '--health':
        # Test health endpoint
        test_health_endpoint()
    else:
        # Run setup and tests
        success = main()
        sys.exit(0 if success else 1)
