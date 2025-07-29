"""
Simple Basketball Shot Analysis Web Application for DigitalOcean Deployment
"""

import os
import logging
from flask import Flask, render_template, request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

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
