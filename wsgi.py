#!/usr/bin/env python3
"""
WSGI Entry Point for Basketball Analysis Service
Production-ready configuration for deployment platforms
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
        logging.FileHandler('basketball_analysis_production.log'),
        logging.StreamHandler()
    ]
)

try:
    # Import the Flask application
    from web_app import app as application
    
    # Also make it available as 'app' for compatibility
    app = application
    
    # Production-specific configurations
    application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'production-secret-key-change-me')
    application.config['DEBUG'] = False
    application.config['TESTING'] = False
    
    # Set maximum file size for uploads
    application.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
    
    logging.info("Basketball Analysis Service successfully initialized for production")
    
except ImportError as e:
    logging.error(f"Failed to import application: {e}")
    # Fallback: try direct import
    try:
        import web_app
        application = web_app.app
        app = application
        logging.info("Fallback import successful")
    except Exception as fallback_error:
        logging.error(f"Fallback import failed: {fallback_error}")
        raise
except Exception as e:
    logging.error(f"Error initializing application: {e}")
    raise

if __name__ == "__main__":
    # This runs only if wsgi.py is executed directly (for testing)
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
