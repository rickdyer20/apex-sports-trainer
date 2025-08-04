#!/usr/bin/env python3
"""
Simple Flask Test - Verify Flask Works
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🏀 Basketball Analysis - Flask Test</h1>
    <h2>✅ Flask is Working!</h2>
    <p>This confirms Flask can start a server on your system.</p>
    <p><strong>Next step:</strong> Start the full basketball analysis service</p>
    <ul>
        <li><a href="/test">Test Route</a></li>
        <li><a href="/health">Health Check</a></li>
    </ul>
    <hr>
    <p><strong>To start full service:</strong> python web_app.py</p>
    '''

@app.route('/test')
def test():
    return '<h1>✅ Test Route Working!</h1><p><a href="/">← Back</a></p>'

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'flask-test'}

if __name__ == '__main__':
    print("🔧 Flask Test Server Starting...")
    print("📍 Open: http://127.0.0.1:5000")
    print("🛑 Press Ctrl+C to stop")
    app.run(host='127.0.0.1', port=5000, debug=True)
