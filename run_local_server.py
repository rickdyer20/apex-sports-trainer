#!/usr/bin/env python3
"""
🏀 LOCAL BASKETBALL ANALYSIS SERVER
Simple script to run your basketball analysis service locally
"""

import os
import sys
import subprocess

def start_local_server():
    """Start the basketball analysis service on localhost"""
    print("🏀 BASKETBALL ANALYSIS SERVICE - LOCAL HOST")
    print("=" * 55)
    print()
    
    # Set environment for local development
    os.environ['FLASK_DEBUG'] = 'True'
    os.environ['FLASK_HOST'] = '127.0.0.1'
    os.environ['PORT'] = '5000'
    
    print("🔧 Environment configured for local development")
    print("📍 Server starting at: http://127.0.0.1:5000")
    print("📝 Upload basketball shot videos for analysis")
    print("🎯 Enhanced thumb flick detection active (25° threshold)")
    print("💡 Press Ctrl+C to stop the server")
    print()
    print("⚡ Starting Flask server...")
    print("-" * 55)
    
    try:
        # Start the Flask application directly
        exec(open('web_app.py').read())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except FileNotFoundError:
        print("❌ web_app.py not found in current directory")
        print("💡 Make sure you're in the basketball analysis project folder")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_local_server()
