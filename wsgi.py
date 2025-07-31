#!/usr/bin/env python3
"""
WSGI Entry Point for Basketball Analysis Service
Ultra-robust configuration with multiple fallbacks
"""

import os
import sys
import logging

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

try:
    # Try to import the full application first
    from web_app import app as application
    print("✅ Loaded full basketball analysis service")
except ImportError as e:
    print(f"⚠️ Full service import failed: {e}")
    try:
        # Fallback to minimal service that will definitely work
        from web_app_minimal import app as application
        print("✅ Loaded minimal service as fallback")
    except ImportError as e2:
        print(f"❌ All imports failed, creating emergency service: {e2}")
        # Create emergency fallback
        from flask import Flask, jsonify
        application = Flask(__name__)
        
        @application.route('/')
        def emergency():
            return "Basketball Analysis Service - Emergency Mode - Service Starting"
            
        @application.route('/health')
        def emergency_health():
            return jsonify({'status': 'emergency_mode', 'message': 'Service initializing'})

# Also make it available as 'app' for compatibility
app = application

# Configure for production
if hasattr(application, 'config'):
    application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'basketball-analysis-2025')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
