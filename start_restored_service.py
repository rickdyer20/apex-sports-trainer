#!/usr/bin/env python3
"""
🏀 RESTORED BASKETBALL ANALYSIS SERVICE
Start the working version from git (before deployment issues)
"""

import os
import sys

def start_restored_service():
    """Start the restored basketball analysis service"""
    print("🏀 RESTORED BASKETBALL ANALYSIS SERVICE")
    print("=" * 55)
    print("✅ This is the WORKING version from git commit 4e4f299")
    print("✅ All enhanced features included (thumb flick detection)")
    print("✅ Full dependencies restored (MediaPipe, OpenCV, etc.)")
    print()
    
    # Set environment for local development
    os.environ['FLASK_DEBUG'] = 'True'
    os.environ['FLASK_HOST'] = '127.0.0.1'
    os.environ['PORT'] = '5000'
    
    print("🔧 Environment configured for local development")
    print("📍 Server starting at: http://127.0.0.1:5000")
    print("📝 Upload basketball shot videos for analysis")
    print("🎯 Enhanced thumb flick detection active (25° threshold)")
    print("💡 Press Ctrl+C to stop the server")
    print()
    print("⚡ Starting restored Flask server...")
    print("-" * 55)
    
    try:
        # Import and start the restored web app
        from web_app import app
        app.run(host='127.0.0.1', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure you're in the basketball analysis folder")
        print("2. Check that all dependencies are installed:")
        print("   pip install flask mediapipe opencv-python-headless numpy reportlab")

if __name__ == "__main__":
    start_restored_service()
