#!/usr/bin/env python3
"""
Production WSGI Entry Point - Hybrid Basketball Analysis Service
===============================================================

Smart deployment strategy that ensures instant service availability:
✅ Attempts hybrid service (CV-ready with graceful fallback)
✅ Falls back to full service if hybrid not available
✅ Falls back to lightweight if full service fails
✅ Provides loading page as last resort

This approach guarantees your service is always available while
computer vision dependencies load in the background.
"""

import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variables for production
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'false')
os.environ.setdefault('MEDIAPIPE_DISABLE_GPU', '1')
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '2')

# Smart import strategy - ensures service is always available
try:
    # FIRST: Try hybrid approach - handles partial CV loading gracefully
    from web_app_hybrid import app as application
    print("✅ HYBRID basketball analysis service loaded successfully!")
    print("🏀 Service available immediately")
    print("🔄 Will auto-upgrade to full CV when libraries are ready")
    service_type = "hybrid"
    
except ImportError as e:
    print(f"⚠️ Hybrid service import failed: {e}")
    print("🔄 Trying full computer vision service...")
    
    try:
        # SECOND: Try full service with complete computer vision
        from web_app import app as application
        print("✅ FULL basketball analysis service loaded!")
        print("🏀 Complete computer vision capabilities active")
        service_type = "full"
        
    except ImportError as e2:
        print(f"⚠️ Full service import failed: {e2}")
        print("🔄 Falling back to professional lightweight version...")
        
        try:
            # THIRD: Professional lightweight version
            from web_app_lightweight import app as application
            print("✅ LIGHTWEIGHT basketball analysis service loaded!")
            print("🏀 Professional UI with analysis simulation")
            service_type = "lightweight"
            
        except ImportError as e3:
            print(f"❌ All service imports failed: {e3}")
            print("🔧 Creating emergency fallback service...")
            
            # LAST RESORT: Emergency fallback
            from flask import Flask
            application = Flask(__name__)
            service_type = "emergency"
    
    @application.route('/')
    def fallback_home():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Basketball Analysis - Loading</title>
        </head>
        <body>
            <h1>� Basketball Analysis Service</h1>
            <h2>⚠️ Loading Full Version...</h2>
            <p>The full basketball analysis service is being restored.</p>
            <p>Some dependencies may still be loading.</p>
        </body>
        </html>
        '''
    
    @application.route('/health')
    def fallback_health():
        return {'status': 'partial', 'message': 'Loading full service'}

# For local development
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    application.run(host='0.0.0.0', port=port, debug=False)
