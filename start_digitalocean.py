#!/usr/bin/env python3
"""
DigitalOcean Production Startup Script
Basketball Analysis Service - Simplified for App Platform

This script starts the Flask application without external database/Redis dependencies.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_required_directories():
    """Create required directories for video processing"""
    logger.info("📁 Creating required directories...")
    
    required_dirs = ['temp_videos', 'output_videos', 'logs', 'jobs']
    project_root = Path(__file__).parent
    
    for directory in required_dirs:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)
        logger.info(f"✅ Directory created/verified: {directory}")

def check_core_dependencies():
    """Check that core dependencies are available"""
    logger.info("📦 Checking core dependencies...")
    
    try:
        import flask
        import cv2
        import mediapipe as mp
        import numpy as np
        logger.info("✅ Core dependencies available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False

def start_flask_app():
    """Start the Flask application with Gunicorn"""
    logger.info("🚀 Starting Flask application...")
    
    # Get port from environment (DigitalOcean sets this)
    port = int(os.getenv('PORT', 8080))
    
    # Set environment variables for Flask
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = 'False'
    
    logger.info(f"🌐 Starting server on port {port}")
    
    # Import and run the Flask app
    try:
        from web_app import app
        
        # Start with Gunicorn for production
        import gunicorn.app.wsgiapp as wsgi
        
        # Configure Gunicorn
        sys.argv = [
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '2',
            '--timeout', '300',
            '--keep-alive', '5',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            '--log-level', 'info',
            '--access-logfile', '-',
            '--error-logfile', '-',
            'web_app:app'
        ]
        
        wsgi.run()
        
    except Exception as e:
        logger.error(f"❌ Failed to start Flask app: {e}")
        sys.exit(1)

def main():
    """Main entry point for DigitalOcean App Platform"""
    logger.info("🏀 Starting Basketball Analysis Service on DigitalOcean...")
    logger.info(f"🔧 Python version: {sys.version}")
    logger.info(f"📍 Working directory: {os.getcwd()}")
    logger.info(f"🌐 PORT: {os.getenv('PORT', '8080')}")
    
    # Run startup checks
    if not check_core_dependencies():
        logger.error("❌ Dependency check failed")
        sys.exit(1)
    
    # Create required directories
    create_required_directories()
    
    # Start the Flask application
    start_flask_app()

if __name__ == "__main__":
    main()
