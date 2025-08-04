#!/usr/bin/env python3
"""
Start Local Basketball Analysis Service
Simple script to start the web app for local testing
"""

import os
import sys

def start_local_server():
    """Start the basketball analysis web service locally"""
    print("🏀 STARTING BASKETBALL ANALYSIS SERVICE LOCALLY")
    print("=" * 55)
    
    # Set environment variables for local development
    os.environ['FLASK_DEBUG'] = 'True'
    os.environ['FLASK_HOST'] = '127.0.0.1'
    os.environ['PORT'] = '5000'
    
    print("🔧 Environment configured for local development")
    print("📍 Server will start at: http://127.0.0.1:5000")
    print("📝 You can upload basketball shot videos for analysis")
    print("🎯 Enhanced thumb flick detection is active (25° threshold)")
    print("\n⚡ Starting server...\n")
    
    try:
        # Import and run the web app
        import web_app
        # The web_app.py file has the app.run() call at the bottom
        # so just importing it will start the server
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("💡 Try running: python web_app.py directly")

if __name__ == "__main__":
    start_local_server()
