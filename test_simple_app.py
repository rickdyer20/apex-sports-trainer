#!/usr/bin/env python3
"""
Ultra-Simple Test App for DigitalOcean
Minimal Flask app to test basic functionality
"""

from flask import Flask

# Create Flask app - named 'application' for WSGI compatibility
app = Flask(__name__)
application = app  # WSGI servers often expect 'application'

@app.route('/')
def home():
    """Ultra-simple home page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test App Working</title>
    </head>
    <body>
        <h1>✅ SUCCESS!</h1>
        <h2>DigitalOcean App is Working</h2>
        <p>This is a minimal test to verify the deployment works.</p>
        <hr>
        <ul>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/test">Simple Test</a></li>
        </ul>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    """Simple health check"""
    return {
        'status': 'healthy',
        'message': 'Ultra-simple app is working',
        'app': 'test_simple'
    }

@app.route('/test')
def test():
    """Simple test endpoint"""
    return {
        'test': 'passed',
        'message': 'All basic functionality working',
        'endpoints': ['/', '/health', '/test']
    }

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
