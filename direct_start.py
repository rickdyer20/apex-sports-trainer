#!/usr/bin/env python3
"""
Direct Server Start - No Background Mode
"""

# Simple, direct server startup
from web_app import app

if __name__ == '__main__':
    print("🏀 Basketball Analysis Service Starting...")
    print("📍 Server starting at: http://127.0.0.1:5000")
    print("🛑 Press Ctrl+C to stop")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
