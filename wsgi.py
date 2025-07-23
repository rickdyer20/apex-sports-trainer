#!/usr/bin/env python3
"""
WSGI Entry Point for Basketball Analysis Service
Ensures proper gunicorn compatibility
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask application
from web_app import app

# This is what gunicorn will use
application = app

if __name__ == "__main__":
    # For local testing
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
