#!/usr/bin/env python3
"""
Emergency Direct WSGI Application
Bypasses all imports - defines Flask app directly in WSGI
"""

import os
from flask import Flask

# Create Flask app directly in WSGI - no imports
application = Flask(__name__)

@application.route('/')
def home():
    """Direct WSGI home"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Direct WSGI Working!</title>
    </head>
    <body>
        <h1>🎯 DIRECT WSGI SUCCESS!</h1>
        <h2>No Imports - Direct Flask App</h2>
        <p>This app is defined directly in wsgi.py</p>
        <ul>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/status">Status</a></li>
        </ul>
    </body>
    </html>
    '''

@application.route('/health')
def health():
    """Health check for DigitalOcean"""
    return {
        'status': 'healthy',
        'method': 'direct_wsgi',
        'message': 'Direct WSGI app working perfectly'
    }

@application.route('/status')
def status():
    """Status endpoint"""
    return {
        'wsgi': 'direct',
        'flask': 'working',
        'imports': 'none',
        'deployment': 'digitalocean'
    }

# Environment setup
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'false')

# For local development
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting Flask app on port: {port}")
    print(f"🔧 Environment PORT variable: {os.environ.get('PORT', 'NOT SET')}")
    print(f"📋 All environment variables: {dict(os.environ)}")
    application.run(host='0.0.0.0', port=port, debug=True)
