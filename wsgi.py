#!/usr/bin/env python3
"""
WSGI Entry Point for Basketball Analysis Service
Ensures proper gunicorn compatibility
"""

import os
import sys

# Add the project directory to the Python path.
# This ensures that 'web_app' can be imported by the WSGI server.
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask application object from our web_app module
# and rename it to 'application' as is conventional for Gunicorn.
from web_app import app as application

# The block below is for local development and allows running the app
# directly with `python wsgi.py`. Gunicorn will not execute this part.
if __name__ == "__main__":
    # Use the PORT environment variable if available, otherwise default to 8080.
    port = int(os.environ.get('PORT', 8080))
    # Run the app. Host '0.0.0.0' makes it accessible from the network.
    application.run(host='0.0.0.0', port=port)
