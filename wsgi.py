#!/usr/bin/env python3
"""
Basketball Analysis Service - Production WSGI
Gradual restoration of full functionality
"""

import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variables for production
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'false')

# Import the full web application
try:
    from web_app import app as application
    print(f"✅ Successfully loaded full basketball analysis app: {application}")
except ImportError as e:
    print(f"⚠️ Failed to import full app, falling back to simple version: {e}")
    # Fallback to simple app if full app fails
    from flask import Flask
    application = Flask(__name__)
    
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
