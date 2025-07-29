#!/usr/bin/env python3
"""
Production Deployment Script for Basketball Analysis Service
Optimized for performance with flaw still generation
"""

import os
import sys
import logging
from datetime import datetime

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'basketball_analysis_production_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

def set_performance_environment():
    """Set environment variables for optimized performance"""
    logging.info("Setting performance optimization environment variables...")
    
    performance_vars = {
        'TF_CPP_MIN_LOG_LEVEL': '2',
        'CUDA_VISIBLE_DEVICES': '',
        'TF_ENABLE_ONEDNN_OPTS': '0',
        'MEDIAPIPE_DISABLE_GPU': '1',
        'FLASK_ENV': 'production',
        'FLASK_DEBUG': 'false',
        'FLASK_HOST': '0.0.0.0'
    }
    
    for key, value in performance_vars.items():
        os.environ[key] = value
        logging.info(f"Set {key}={value}")

def check_system_requirements():
    """Check system requirements for production deployment"""
    logging.info("Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logging.error("Python 3.8+ required for production deployment")
        return False
    
    # Check available disk space
    import shutil
    total, used, free = shutil.disk_usage('.')
    free_gb = free // (1024**3)
    
    if free_gb < 5:  # Require at least 5GB free space
        logging.error(f"Insufficient disk space: {free_gb}GB free (minimum 5GB required)")
        return False
    
    logging.info(f"System check passed - {free_gb}GB free space available")
    return True

def optimize_directories():
    """Create and optimize directory structure for production"""
    directories = [
        'uploads',
        'results', 
        'jobs',
        'logs',
        'temp',
        'static/cache'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logging.info(f"Created/verified directory: {directory}")

def cleanup_temp_files():
    """Clean up temporary files from previous runs"""
    import glob
    
    temp_patterns = [
        'temp_*.png',
        'temp_*.mp4',
        '*.tmp'
    ]
    
    cleaned_files = 0
    for pattern in temp_patterns:
        files = glob.glob(pattern)
        for file in files:
            try:
                os.remove(file)
                cleaned_files += 1
            except Exception as e:
                logging.warning(f"Could not remove {file}: {e}")
    
    if cleaned_files > 0:
        logging.info(f"Cleaned up {cleaned_files} temporary files")

def start_production_server():
    """Start the production-optimized Flask server"""
    logging.info("🏀 Starting Basketball Analysis Service - Production Mode")
    logging.info("📊 Production Features Enabled:")
    logging.info("   • Optimized flaw still generation")
    logging.info("   • Reduced processing timeouts")
    logging.info("   • Enhanced frame skipping")
    logging.info("   • Performance monitoring")
    logging.info("   • Production logging")
    
    # Import and run the web application
    from web_app import app
    
    # Production configuration
    app.config['ENV'] = 'production'
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # Get host and port from environment (for containerized deployment)
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    # Start server with production settings
    logging.info(f"🌐 Server starting at http://{host}:{port}")
    logging.info("📝 Ready for basketball shot analysis with optimized performance!")
    
    try:
        app.run(
            debug=False,
            host=host,
            port=port,
            threaded=True,
            use_reloader=False
        )
    except KeyboardInterrupt:
        logging.info("Server shutdown requested by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        cleanup_temp_files()
        logging.info("Production server stopped")

if __name__ == '__main__':
    print("🏀 Basketball Analysis Service - Production Deployment")
    print("=" * 60)
    
    if not check_system_requirements():
        sys.exit(1)
    
    set_performance_environment()
    optimize_directories()
    cleanup_temp_files()
    start_production_server()
