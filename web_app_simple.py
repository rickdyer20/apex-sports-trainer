"""
Simple Basketball Shot Analysis Web Application for DigitalOcean Deployment
"""

import os
import logging
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

@app.route('/')
def index():
    """Home page"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Basketball Shot Analysis - Deployment Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            .status {
                background: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Basketball Shot Analysis Service</h1>
            <div class="status">
                ✅ Deployment Test Successful! The application is running on DigitalOcean.
            </div>
            <p>Service Status: <strong>Active</strong></p>
            <p>Platform: <strong>DigitalOcean App Platform</strong></p>
            <p>Framework: <strong>Flask + Gunicorn</strong></p>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Basketball Analysis Service is running'})

@app.route('/api/health')
def api_health_check():
    """API health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Basketball Analysis API'})

@app.route('/upload', methods=['POST'])
def upload_video():
    """Simple upload endpoint for testing"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # For testing, just return success
    return jsonify({
        'job_id': 'test-deployment',
        'message': 'Video uploaded successfully (deployment test)',
        'status': 'success'
    })

@app.route('/results/<job_id>')
def get_results(job_id):
    """Simple results endpoint for testing"""
    return jsonify({
        'job_id': job_id,
        'message': 'Results endpoint working (deployment test)',
        'status': 'success'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
