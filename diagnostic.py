#!/usr/bin/env python3
"""
MINIMAL DIAGNOSTIC SERVICE - Find the fundamental deployment issue
================================================================

This is the absolute simplest possible Flask service to identify
what's preventing deployment on cloud platforms.
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Diagnostic Test</title>
    </head>
    <body>
        <h1>🔍 DIAGNOSTIC SERVICE WORKING</h1>
        <p>If you can see this, basic Flask deployment is functional.</p>
        <p>This confirms the fundamental deployment issue is resolved.</p>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'diagnostic service working'}

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
