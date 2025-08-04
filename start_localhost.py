#!/usr/bin/env python3
"""
🏀 Basketball Analysis Service - Local Host Startup
Optimized for local development with proper environment configuration
"""

import os
import sys
from pathlib import Path

def load_local_env():
    """Load local environment variables"""
    env_file = Path('.env.local')
    if env_file.exists():
        print("📄 Loading local environment variables...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Local environment loaded")
    else:
        print("⚠️ No .env.local file found, using defaults")

def setup_local_environment():
    """Set up environment for local development"""
    # Load environment variables
    load_local_env()
    
    # Set default local development variables
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', 'True')
    os.environ.setdefault('FLASK_HOST', '127.0.0.1')
    os.environ.setdefault('PORT', '5000')
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    os.makedirs('jobs', exist_ok=True)
    
    print("📁 Local directories created/verified")

def start_localhost_server():
    """Start the basketball analysis service on localhost"""
    print("🏀 BASKETBALL ANALYSIS SERVICE - LOCALHOST")
    print("=" * 60)
    
    # Setup environment
    setup_local_environment()
    
    # Display configuration
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = os.environ.get('PORT', '5000')
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🔧 Configuration:")
    print(f"   • Host: {host}")
    print(f"   • Port: {port}")
    print(f"   • Debug: {debug}")
    print(f"   • Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print()
    
    print("🎯 Features Active:")
    print("   • Enhanced thumb flick detection (25° threshold)")
    print("   • 12+ flaw detection types")
    print("   • Multiple camera angle support")
    print("   • Real-time progress tracking")
    print("   • PDF report generation")
    print()
    
    print(f"🌐 Server will start at: http://{host}:{port}")
    print("📝 Upload basketball shot videos for analysis")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    print("⚡ Starting localhost server...")
    print("-" * 60)
    
    try:
        # Import and start the web application
        from web_app import app
        
        # Run with local configuration
        app.run(
            host=host,
            port=int(port),
            debug=debug,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n🔧 Install missing dependencies:")
        print("pip install flask mediapipe opencv-python-headless numpy reportlab")
        
    except Exception as e:
        print(f"❌ Server Error: {e}")
        print(f"Error Type: {type(e).__name__}")
        
        # Try emergency fallback server
        print("\n🚨 Starting emergency fallback server...")
        from flask import Flask
        
        emergency_app = Flask(__name__)
        
        @emergency_app.route('/')
        def emergency():
            return f"""
            <h1>🏀 Basketball Analysis - Emergency Mode</h1>
            <p><strong>Main server failed:</strong> {str(e)}</p>
            <p><strong>Error Type:</strong> {type(e).__name__}</p>
            <hr>
            <h3>Troubleshooting:</h3>
            <ul>
                <li>Check that all dependencies are installed</li>
                <li>Verify web_app.py exists and is accessible</li>
                <li>Try running: pip install -r requirements.txt</li>
            </ul>
            <p><a href="/test">Test Emergency Server</a></p>
            """
        
        @emergency_app.route('/test')
        def test():
            return "<h1>✅ Emergency server working!</h1><p><a href='/'>Back</a></p>"
        
        print(f"📍 Emergency server at: http://{host}:5001")
        emergency_app.run(host=host, port=5001, debug=True)

if __name__ == "__main__":
    start_localhost_server()
