#!/usr/bin/env python3
"""
Diagnostic Web App for DigitalOcean Deployment
Basketball Shot Analysis Service - Simplified for debugging

This version helps identify deployment issues by starting with minimal dependencies
and gradually adding functionality.
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info("🚀 Starting diagnostic web app...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Environment PORT: {os.getenv('PORT', 'not set')}")
logger.info(f"Environment FLASK_ENV: {os.getenv('FLASK_ENV', 'not set')}")

try:
    from flask import Flask, jsonify, render_template_string, request
    logger.info("✅ Flask import successful")
except ImportError as e:
    logger.error(f"❌ Flask import failed: {e}")
    sys.exit(1)

# Create Flask app
app = Flask(__name__)
app.secret_key = 'diagnostic_key_2025'

# Test template
DIAGNOSTIC_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Basketball Analysis - Diagnostic Mode</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
            background: #f5f5f5; 
        }
        .container { 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 0 15px rgba(0,0,0,0.1); 
        }
        .status { 
            background: #d1ecf1; 
            color: #0c5460; 
            padding: 15px; 
            border-radius: 5px; 
            margin: 15px 0; 
        }
        .success { background: #d4edda; color: #155724; }
        .warning { background: #fff3cd; color: #856404; }
        .error { background: #f8d7da; color: #721c24; }
        h1 { color: #333; text-align: center; }
        .info { background: #e2e3e5; color: #383d41; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏀 Basketball Analysis Service</h1>
        <h2>🔧 Diagnostic Mode</h2>
        
        <div class="status success">
            <h3>✅ Deployment Status: RUNNING</h3>
            <p>The Flask application is successfully running on DigitalOcean!</p>
        </div>
        
        <div class="info">
            <h4>🔍 System Information:</h4>
            <ul>
                <li><strong>Timestamp:</strong> {{ timestamp }}</li>
                <li><strong>Python Version:</strong> {{ python_version }}</li>
                <li><strong>Flask Status:</strong> Active</li>
                <li><strong>Port:</strong> {{ port }}</li>
                <li><strong>Environment:</strong> {{ env }}</li>
            </ul>
        </div>
        
        <div class="status warning">
            <h4>⚠️ Diagnostic Mode Active</h4>
            <p>This is a simplified version to test deployment. The full basketball analysis features are temporarily disabled for debugging.</p>
        </div>
        
        <div class="info">
            <h4>📋 Next Steps:</h4>
            <ol>
                <li>Verify this page loads correctly</li>
                <li>Test the health endpoint: <a href="/health">/health</a></li>
                <li>Check dependency compatibility</li>
                <li>Gradually enable full features</li>
            </ol>
        </div>
        
        <div class="status">
            <h4>🔗 Useful Links:</h4>
            <ul>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/api/health">API Health Check</a></li>
                <li><a href="/test">Dependency Test</a></li>
            </ul>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    """Diagnostic home page"""
    logger.info("📱 Home page requested")
    
    return render_template_string(
        DIAGNOSTIC_TEMPLATE,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        python_version=sys.version.split()[0],
        port=os.getenv('PORT', '8080'),
        env=os.getenv('FLASK_ENV', 'development')
    )

@app.route('/health')
def health():
    """Simple health check endpoint"""
    logger.info("🔍 Health check requested")
    
    return jsonify({
        'status': 'healthy',
        'service': 'Basketball Analysis Service - Diagnostic Mode',
        'timestamp': datetime.now().isoformat(),
        'mode': 'diagnostic',
        'python_version': sys.version.split()[0],
        'port': os.getenv('PORT', '8080')
    })

@app.route('/api/health')
def api_health():
    """Comprehensive API health check"""
    logger.info("🔍 API health check requested")
    
    health_data = {
        'status': 'healthy',
        'service': 'Basketball Analysis Service',
        'mode': 'diagnostic',
        'timestamp': datetime.now().isoformat(),
        'checks': {
            'flask': 'ok',
            'python': sys.version.split()[0],
            'environment': os.getenv('FLASK_ENV', 'development'),
            'port': os.getenv('PORT', '8080')
        }
    }
    
    return jsonify(health_data)

@app.route('/test')
def test_dependencies():
    """Test if key dependencies can be imported"""
    logger.info("🧪 Dependency test requested")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'dependencies': {}
    }
    
    # Test core dependencies
    test_imports = [
        ('cv2', 'OpenCV'),
        ('mediapipe', 'MediaPipe'),
        ('numpy', 'NumPy'),
        ('reportlab', 'ReportLab'),
        ('PIL', 'Pillow'),
        ('requests', 'Requests')
    ]
    
    for module, name in test_imports:
        try:
            __import__(module)
            results['dependencies'][name] = 'available'
            logger.info(f"✅ {name} import successful")
        except ImportError as e:
            results['dependencies'][name] = f'error: {str(e)}'
            logger.warning(f"⚠️ {name} import failed: {e}")
    
    return jsonify(results)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error for path: {request.path}")
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found',
        'available_endpoints': [
            '/',
            '/health',
            '/api/health', 
            '/test'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An internal error occurred',
        'timestamp': datetime.now().isoformat()
    }), 500

def create_required_directories():
    """Create directories needed by the application"""
    required_dirs = ['temp_videos', 'output_videos', 'logs', 'jobs', 'results']
    
    for directory in required_dirs:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✅ Directory ensured: {directory}")
        except Exception as e:
            logger.warning(f"⚠️ Could not create directory {directory}: {e}")

if __name__ == '__main__':
    logger.info("🏀 Basketball Analysis Diagnostic Service Starting...")
    
    # Create required directories
    create_required_directories()
    
    # Get port from environment
    port = int(os.getenv('PORT', 8080))
    
    logger.info(f"🌐 Starting server on port {port}")
    logger.info("🔧 Running in diagnostic mode")
    
    # Start the Flask application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
